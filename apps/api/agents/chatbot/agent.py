from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from agents.base.agent import BaseAgent
from agents.chatbot.state import (
    ChatbotOrchestratorState,
    ChatbotStep,
    HospitalOption,
)
from agents.chatbot.intent_detector import detect_intent, should_pivot
from agents.chatbot.hospital_client import HospitalClient

from models.hospital import Hospital
from models.department import Department
from models.doctor import Doctor

from services.hospital_service import HospitalService


class ChatbotOrchestratorAgent(BaseAgent):
    """
    The unified chatbot gateway.
    Routes user conversations to the right hospital's Registration Agent.

    Flow:
      GREETING → COLLECT_SYMPTOMS → DETECT_INTENT → DISCOVER_HOSPITALS
      → SELECT_HOSPITAL → PROXY_REGISTRATION → COMPLETED
    """

    def __init__(self, state: ChatbotOrchestratorState, db: AsyncSession):
        self.state = state
        self.db = db
        self.hospital_client = HospitalClient()

    async def handle(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Main handler — delegates to the correct step."""
        step = self.state.step
        user_message = user_input.get("message", "").strip()

        # Pivot detection for applicable steps
        if step not in (
            ChatbotStep.GREETING,
            ChatbotStep.DETECT_INTENT,
            ChatbotStep.COMPLETED,
            ChatbotStep.CONFIRM_BOOKING,
        ):
            pivot_result = await should_pivot(
                user_message, step.value, self.state.last_bot_message or ""
            )

            if pivot_result == "exit":
                self.state.step = ChatbotStep.COMPLETED
                return self._reply("Thank you for using our service. Goodbye!")

            if pivot_result == "pivot":
                # Merge new symptoms with existing symptoms_raw
                old_symptoms = self.state.symptoms_raw or ""
                if old_symptoms:
                    self.state.symptoms_raw = f"{old_symptoms} | {user_message}"
                else:
                    self.state.symptoms_raw = user_message
                self.state.step = ChatbotStep.DETECT_INTENT
                return await self._handle_detect_intent(user_input)

            if pivot_result == "help":
                # Provide help and stay on current step
                return self._reply(
                    f"I can help you with hospital booking. {self.state.last_bot_message or 'Please continue with your booking.'}"
                )

        if step == ChatbotStep.GREETING:
            return await self._handle_greeting(user_input)

        elif step == ChatbotStep.COLLECT_SYMPTOMS:
            return await self._handle_collect_symptoms(user_input)

        elif step == ChatbotStep.DETECT_INTENT:
            return await self._handle_detect_intent(user_input)

        elif step == ChatbotStep.DISCOVER_HOSPITALS:
            return await self._handle_discover_hospitals(user_input)

        elif step == ChatbotStep.CONFIRM_BOOKING:
            return await self._handle_confirm_booking(user_input)

        elif step == ChatbotStep.SELECT_HOSPITAL:
            return await self._handle_select_hospital(user_input)

        elif step == ChatbotStep.PROXY_REGISTRATION:
            return await self._handle_proxy_registration(user_input)

        elif step == ChatbotStep.COMPLETED:
            return self._reply(
                "Your session is complete. Type 'hi' to start a new conversation."
            )

        return self._reply("Something went wrong. Please try again.")

    # ──────────────────────────────────────────────
    # STEP 1: GREETING
    # ──────────────────────────────────────────────
    async def _handle_greeting(self, user_input: Dict) -> Dict:
        message = user_input.get("message", "").strip()

        if not message:
            return self._reply(
                "👋 Hello! I'm your healthcare assistant. "
                "Tell me what health concern you're experiencing, "
                "and I'll help you find the right hospital and doctor."
            )

        # User already typed something meaningful — treat as symptoms
        self.state.symptoms_raw = message
        self.state.step = ChatbotStep.DETECT_INTENT
        return await self._handle_detect_intent(user_input)

    # ──────────────────────────────────────────────
    # STEP 2: COLLECT SYMPTOMS
    # ──────────────────────────────────────────────
    async def _handle_collect_symptoms(self, user_input: Dict) -> Dict:
        message = user_input.get("message", "").strip()

        if not message:
            return self._reply("Please describe your symptoms or health concern.")

        self.state.symptoms_raw = message
        self.state.step = ChatbotStep.DETECT_INTENT
        return await self._handle_detect_intent(user_input)

    # ──────────────────────────────────────────────
    # STEP 3: DETECT INTENT (LLM)
    # ──────────────────────────────────────────────
    async def _handle_detect_intent(self, user_input: Dict) -> Dict:
        intent_result = await detect_intent(self.state.symptoms_raw)

        self.state.detected_intent = intent_result.get("intent", "medical")
        self.state.department_hint = intent_result.get("department_hint")
        self.state.intent_confidence = intent_result.get("confidence", 0.5)

        if self.state.detected_intent == "hotel_booking":
            self.state.step = ChatbotStep.EXTERNAL_HANDOFF
            return self._reply(
                "🏨 It seems like you need hotel accommodation. "
                "This feature is coming soon! Please contact the hospital directly for now."
            )

        if self.state.detected_intent == "general_query":
            self.state.step = ChatbotStep.COLLECT_SYMPTOMS
            return self._reply(
                "I can help you find hospitals and book doctor appointments. "
                "Could you describe any symptoms you're experiencing?"
            )

        # Intent is "medical" — discover hospitals
        self.state.step = ChatbotStep.DISCOVER_HOSPITALS
        return await self._handle_discover_hospitals(user_input)

    # ──────────────────────────────────────────────
    # STEP 4: DISCOVER HOSPITALS
    # ──────────────────────────────────────────────
    async def _handle_discover_hospitals(self, user_input: Dict) -> Dict:
        """Find hospitals that have the suggested department and available doctors."""

        service = HospitalService(self.db)

        if self.state.department_hint:
            hospitals = await service.search_by_department(self.state.department_hint)
        else:
            hospitals = await service.list_all()

        # Filter to active hospitals only
        hospitals = [h for h in hospitals if h.is_active]

        if not hospitals:
            return self._reply(
                "Sorry, I couldn't find any hospitals with available doctors "
                f"for {self.state.department_hint or 'your concern'}. "
                "Please try describing your symptoms differently."
            )

        # Build hospital options with doctor info
        options: List[HospitalOption] = []
        for hospital in hospitals:
            doctors = await self._get_doctors_for_hospital(
                hospital.id, self.state.department_hint
            )
            options.append(
                HospitalOption(
                    hospital_id=hospital.id,
                    hospital_name=hospital.name,
                    location=hospital.location,
                    doctors=[
                        {
                            "id": str(d.id),
                            "name": d.name,
                            "specialization": d.specialization,
                        }
                        for d in doctors
                    ],
                )
            )

        self.state.available_hospitals = options
        self.state.step = ChatbotStep.CONFIRM_BOOKING

        # Build display message
        dept_label = self.state.department_hint or "your concern"
        msg = (
            f"🏥 I found **{len(options)} hospital(s)** with {dept_label} services:\n\n"
        )

        for i, opt in enumerate(options, 1):
            doctor_names = (
                ", ".join(d["name"] for d in opt.doctors)
                if opt.doctors
                else "Doctors available"
            )
            msg += f"**{i}. {opt.hospital_name}** ({opt.location})\n"
            msg += f"   Doctors: {doctor_names}\n\n"

        msg += (
            "Would you like to proceed with booking at one of these hospitals? (yes/no)"
        )

        return self._reply(msg)

    # ──────────────────────────────────────────────
    # STEP 4b: CONFIRM BOOKING
    # ──────────────────────────────────────────────
    async def _handle_confirm_booking(self, user_input: Dict) -> Dict:
        """Ask user to confirm before showing hospital selection."""
        message = user_input.get("message", "").strip().lower()

        if message in ("yes", "y", "proceed", "ok", "continue"):
            self.state.step = ChatbotStep.SELECT_HOSPITAL

            options = self.state.available_hospitals
            dept_label = self.state.department_hint or "your concern"
            msg = f"🏥 Here are **{len(options)} hospital(s)** with {dept_label} services:\n\n"

            for i, opt in enumerate(options, 1):
                doctor_names = (
                    ", ".join(d["name"] for d in opt.doctors)
                    if opt.doctors
                    else "Doctors available"
                )
                msg += f"**{i}. {opt.hospital_name}** ({opt.location})\n"
                msg += f"   Doctors: {doctor_names}\n\n"

            msg += "Please reply with the **hospital number** (e.g., `1`) to proceed."
            return self._reply(msg)

        elif message in ("no", "n", "stop", "cancel"):
            self.state.step = ChatbotStep.COMPLETED
            return self._reply("No problem. Thank you for using our service. Goodbye!")

        return self._reply("Please reply with 'yes' to proceed or 'no' to cancel.")

    # ──────────────────────────────────────────────
    # STEP 5: SELECT HOSPITAL
    # ──────────────────────────────────────────────
    async def _handle_select_hospital(self, user_input: Dict) -> Dict:
        message = user_input.get("message", "").strip()

        # Try to parse selection as a number
        try:
            choice = int(message)
            if choice < 1 or choice > len(self.state.available_hospitals):
                raise ValueError()
        except (ValueError, TypeError):
            return self._reply(
                f"Please enter a valid hospital number (1-{len(self.state.available_hospitals)})."
            )

        selected = self.state.available_hospitals[choice - 1]
        self.state.selected_hospital_id = selected.hospital_id
        self.state.selected_hospital_name = selected.hospital_name

        # Transition to proxy mode — ask for phone number
        self.state.step = ChatbotStep.PROXY_REGISTRATION

        return self._reply(
            f"✅ You've selected **{selected.hospital_name}** ({selected.location}).\n\n"
            "Let's start your registration. Please provide your **10-digit phone number**."
        )

    # ──────────────────────────────────────────────
    # STEP 6: PROXY REGISTRATION
    # ──────────────────────────────────────────────
    async def _handle_proxy_registration(self, user_input: Dict) -> Dict:
        """
        Proxy mode: Forward all user messages to the hospital's Registration Agent
        and relay the response back to the user.
        """
        message = user_input.get("message", "").strip()

        if not self.state.delegated_session_id:
            # First message in proxy mode — should be phone number
            if not message:
                return self._reply("Please provide your 10-digit phone number.")

            self.state.proxy_phone_number = message

            try:
                result = await self.hospital_client.start_registration(
                    hospital_id=self.state.selected_hospital_id,
                    phone_number=message,
                )

                self.state.delegated_session_id = UUID(result["session_id"])
                # Track which step the Registration Agent is now on
                reg_step = result.get("state", {}).get("step", "")
                self.state.registration_step = reg_step

                bot_message = result.get("response", {}).get(
                    "message", "Registration started."
                )
                return self._reply(bot_message)

            except Exception as e:
                print(f"[ChatbotOrchestrator] Registration start failed: {e}")
                return self._reply(
                    "Sorry, there was an error connecting to the hospital. Please try again."
                )
        else:
            # Continuing an existing registration session
            # Map user input to the format the Registration Agent expects
            reg_input = self._parse_registration_input(message, user_input)

            try:
                result = await self.hospital_client.continue_registration(
                    session_id=self.state.delegated_session_id,
                    hospital_id=self.state.selected_hospital_id,
                    input_data=reg_input,
                )

                # Extract the response and new step
                response_data = result.get("response", {})
                bot_message = response_data.get("message", "")
                current_step = result.get("state", {}).get("step", "")

                # Update the tracked registration step
                self.state.registration_step = current_step

                # Check if registration is complete
                if current_step == "handoff_complete":
                    self.state.step = ChatbotStep.COMPLETED

                    # Extract queue info for tracking link
                    queue_status = response_data.get("queue_status", {})
                    token_number = queue_status.get("token_number", "")
                    visit_id = result.get("state", {}).get("visit_id", "")
                    doctor_id = result.get("state", {}).get("doctor_id", "")
                    doctor_name = result.get("state", {}).get("doctor_name", "")
                    department = result.get("state", {}).get("department_final", "")

                    # Build queue tracking link
                    tracking_url = (
                        f"/queue?visit_id={visit_id}"
                        f"&doctor_id={doctor_id}"
                        f"&token={token_number}"
                        f"&doctor_name={doctor_name}"
                        f"&department={department}"
                    )

                    return self._reply(
                        f"{bot_message}\n\n"
                        "🎉 Your registration is complete! "
                        f"You're registered at **{self.state.selected_hospital_name}**.\n\n"
                        f"🎫 **Token #{token_number}**\n"
                        f"📋 [Track your queue live]({tracking_url})"
                    )

                # Enrich message with extra data from response
                display_message = bot_message

                # Department suggestion
                if "suggested_department" in response_data:
                    dept = response_data["suggested_department"]
                    confidence = response_data.get("confidence", 0)
                    departments = response_data.get("departments", [])
                    display_message = (
                        f"Based on your symptoms, I suggest **{dept}** "
                        f"(confidence: {confidence:.0%}).\n\n"
                        f"Available departments: {', '.join(departments)}\n\n"
                        "Reply **yes** to confirm, or type a different department name."
                    )

                # Doctor list
                if "doctors" in response_data:
                    doctors = response_data["doctors"]
                    doc_list = "\n".join(
                        f"  {i + 1}. **{d['name']}** ({d['specialization']})"
                        for i, d in enumerate(doctors)
                    )
                    display_message = f"{bot_message}\n\n{doc_list}\n\nReply with the doctor **number** to select."
                    # Store doctor list for mapping index -> ID
                    self.state.messages.append(
                        {
                            "role": "system",
                            "content": str(
                                [{"id": d["id"], "name": d["name"]} for d in doctors]
                            ),
                        }
                    )

                return self._reply(display_message)

            except Exception as e:
                print(f"[ChatbotOrchestrator] Registration proxy failed: {e}")
                return self._reply(
                    "Sorry, there was an error processing your input. Please try again."
                )

    # ──────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────
    def _parse_registration_input(self, message: str, user_input: Dict) -> Dict:
        """
        Map the user's free-text message to the structured input keys
        that the Registration Agent expects at each step.
        """
        # If the user_input already has structured keys (from frontend buttons)
        if user_input.get("doctor_id"):
            return {"doctor_id": user_input["doctor_id"]}
        if user_input.get("department"):
            return {"department_override": user_input["department"]}
        if user_input.get("confirm"):
            return {
                "confirm": user_input["confirm"] == "true"
                or user_input["confirm"] is True
            }

        reg_step = self.state.registration_step

        # COLLECT_SYMPTOMS → send as "symptoms"
        if reg_step == "collect_symptoms":
            return {"symptoms": message}

        # COLLECT_PATIENT_DETAILS → parse name and age
        if reg_step == "collect_patient_details":
            import re

            match = re.match(r"^(.+?)[,\s]+(\d{1,3})$", message.strip())
            if match:
                return {"full_name": match.group(1).strip(), "age": int(match.group(2))}
            return {"full_name": message, "age": 0}

        # RESOLVE_DEPARTMENT → "yes" = confirm, else override
        if reg_step == "resolve_department":
            if message.lower() in ("yes", "y", "confirm", "ok"):
                return {"confirm": True}
            return {"department_override": message}

        # SELECT_DOCTOR → parse doctor number or ID
        if reg_step == "select_doctor":
            # Try to map number to doctor ID from stored list
            try:
                choice = int(message)
                # Look for the doctor list in recent system messages
                for msg in reversed(self.state.messages):
                    if msg.get("role") == "system":
                        import ast

                        doctors = ast.literal_eval(msg["content"])
                        if 1 <= choice <= len(doctors):
                            return {"doctor_id": doctors[choice - 1]["id"]}
                        break
            except (ValueError, Exception):
                pass
            return {"doctor_id": message}

        # COLLECT_PHONE → phone number
        if reg_step == "collect_phone":
            return {"phone_number": message}

        # Fallback: send as symptoms (safest default)
        return {"symptoms": message}

    async def _get_doctors_for_hospital(
        self, hospital_id: UUID, department_name: str = None
    ) -> list:
        """Query doctors for a hospital, optionally filtered by department."""
        query = select(Doctor).where(
            Doctor.hospital_id == hospital_id,
            Doctor.is_available == True,
        )

        if department_name:
            dept_result = await self.db.execute(
                select(Department.id).where(
                    Department.hospital_id == hospital_id,
                    Department.name == department_name,
                )
            )
            dept_id = dept_result.scalar_one_or_none()
            if dept_id:
                query = query.where(Doctor.department_id == dept_id)

        result = await self.db.execute(query)
        return result.scalars().all()

    def _reply(self, message: str) -> Dict[str, Any]:
        """Build a standard reply and track in conversation history."""
        self.state.last_bot_message = message
        self.state.messages.append({"role": "bot", "content": message})
        return {
            "message": message,
            "step": self.state.step.value,
            "session_data": {
                "detected_intent": self.state.detected_intent,
                "department_hint": self.state.department_hint,
                "selected_hospital": self.state.selected_hospital_name,
                "available_hospitals": [
                    {"name": h.hospital_name, "location": h.location}
                    for h in self.state.available_hospitals
                ]
                if self.state.available_hospitals
                else None,
            },
        }
