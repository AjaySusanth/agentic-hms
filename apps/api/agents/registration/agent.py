from typing import Any, Dict,Optional,List
from uuid import UUID,uuid4


from sqlalchemy.ext.asyncio import AsyncSession

from agents.base.agent import BaseAgent
from agents.registration.state import (
    RegistrationAgentState,
    RegistrationStep,
)

import re
from dotenv import load_dotenv
from groq import Groq
import os
import random

load_dotenv()

from agents.doctor_assistance.agent import DoctorAssistanceAgent
from agents.doctor_assistance.state import DoctorAssistanceState

from services.patient_service import PatientService
from services.department_service import DepartmentService
from services.doctor_service import DoctorService
from services.visit_service import VisitService

from services.llm.symptom_summarizer import SymptomSummarizerService
from services.llm.department_resolver import DepartmentResolverService


CONFIDENCE_THRESHOLD = 0.75



def classify_department_with_llm(symptoms: str, departments: Dict[str, str],age:int) -> Optional[str]:
    """
    Uses Groq LLM ONLY as a fallback classifier.
    """


    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    department_list = ", ".join(departments.keys())

    prompt = f"""
        You are a medical department classifier based on the given symptoms of the patient.
        IMPORTANT: If patient age below 18, suggest Pediatrics.
        Choose ONLY ONE department from the list below.
        Do NOT explain.
        Do NOT add extra text.

        Departments:
        {department_list}

        Symptoms:
        {symptoms}

        Patient Age: {age}
        """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You classify symptoms into hospital departments."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    result = response.choices[0].message.content.strip()

    return result if result in departments else None


def handoff_to_doctor_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends visit context to Doctor Assistance Agent.
    """
    state = DoctorAssistanceState(**payload)
    agent = DoctorAssistanceAgent(state)
    return agent.handle()


class RegistrationAgent(BaseAgent[RegistrationAgentState]):
    """
    Registration Agent orchestrates patient registration
    using a deterministic, step-based workflow.
    """

    # ------------------------------------------------------------------
    # Allowed step transitions (STRICT FLOW CONTROL)
    # ------------------------------------------------------------------
    allowed_transitions = {
        RegistrationStep.COLLECT_PHONE: [
            RegistrationStep.PATIENT_LOOKUP
        ],
        RegistrationStep.PATIENT_LOOKUP: [
            RegistrationStep.COLLECT_PATIENT_DETAILS,
            RegistrationStep.COLLECT_SYMPTOMS,
        ],
        RegistrationStep.COLLECT_PATIENT_DETAILS: [
            RegistrationStep.COLLECT_SYMPTOMS
        ],
        RegistrationStep.COLLECT_SYMPTOMS: [
            RegistrationStep.RESOLVE_DEPARTMENT
        ],
        RegistrationStep.RESOLVE_DEPARTMENT: [
            RegistrationStep.SELECT_DOCTOR
        ],
        RegistrationStep.SELECT_DOCTOR: [
            RegistrationStep.CREATE_VISIT
        ],
        RegistrationStep.CREATE_VISIT: [
            RegistrationStep.HANDOFF_COMPLETE
        ],
    }

    def __init__(self, state: RegistrationAgentState, db: AsyncSession):
        super().__init__(state)
        self.db = db

    # ------------------------------------------------------------------
    # Main entrypoint
    # ------------------------------------------------------------------
    async def handle(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Entry point for each user interaction.
        Routes execution based on the current agent step.
        """
        step = self.state.step

        if step == RegistrationStep.COLLECT_PHONE:
            return await self._handle_collect_phone(input_data)

        if step == RegistrationStep.PATIENT_LOOKUP:
            return await self._handle_patient_lookup(input_data)

        if step == RegistrationStep.COLLECT_PATIENT_DETAILS:
            return await self._handle_collect_patient_details(input_data)

        if step == RegistrationStep.COLLECT_SYMPTOMS:
            return await self._handle_collect_symptoms(input_data)

        if step == RegistrationStep.RESOLVE_DEPARTMENT:
            return await self._handle_resolve_department(input_data)

        if step == RegistrationStep.SELECT_DOCTOR:
            return await self._handle_select_doctor(input_data)

        if step == RegistrationStep.CREATE_VISIT:
            return await self._handle_create_visit()

        if step == RegistrationStep.HANDOFF_COMPLETE:
            return await self._handle_handoff()

        raise ValueError(f"Unhandled registration step: {step}")

    # ------------------------------------------------------------------
    # STEP 1: COLLECT_PHONE
    # ------------------------------------------------------------------
    async def _handle_collect_phone(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        phone = input_data.get("phone_number")

        if not phone or not re.fullmatch(r"\d{10}", phone):
            return {"message": "Please enter a valid 10-digit phone number."}

        self.update_state(phone_number=phone)
        self.transition_to(RegistrationStep.PATIENT_LOOKUP)

        return await self.handle({})

    # ------------------------------------------------------------------
    # STEP 2: PATIENT_LOOKUP
    # ------------------------------------------------------------------

    async def _handle_patient_lookup(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        patient = await PatientService.get_by_phone(
            self.db,
            self.state.phone_number,
        )

        if patient:
            self.update_state(
                patient_id=patient.id,
                full_name=patient.full_name,
                age=patient.age,
                is_existing_patient=True,
            )
            self.transition_to(RegistrationStep.COLLECT_SYMPTOMS)
            return {"message": "Please describe your symptoms."}

        self.update_state(is_existing_patient=False)
        self.transition_to(RegistrationStep.COLLECT_PATIENT_DETAILS)
        return {"message": "Please provide your full name and age."}

    

    async def _handle_collect_patient_details(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        full_name = input_data.get("full_name")
        age = input_data.get("age")

        if not full_name or not isinstance(age, int):
            return {"message": "Invalid name or age."}

        patient = await PatientService.create(
            self.db,
            full_name=full_name,
            age=age,
            contact_number=self.state.phone_number,
        )

        self.update_state(
            patient_id=patient.id,
            full_name=patient.full_name,
            age=patient.age,
            is_existing_patient=False,
        )

        self.transition_to(RegistrationStep.COLLECT_SYMPTOMS)
        return {"message": "Please describe your symptoms."}

    async def _handle_collect_symptoms(self, input_data):
        raw = input_data.get("symptoms")
        if not raw or len(raw.strip()) < 5:
            return {"message": "Please describe your symptoms clearly."}

        summary = SymptomSummarizerService.summarize(raw)

        self.update_state(
            symptoms_raw=raw,
            symptoms_summary=summary,
        )

        self.transition_to(RegistrationStep.RESOLVE_DEPARTMENT)
        return await self.handle({})

    async def _handle_resolve_department(self, input_data: Dict[str, Any]):

        # 0️⃣ Load departments ONCE
        departments = await DepartmentService.list_all(self.db)
        dept_names = [d.name for d in departments]

        def _find_department_id(name: str):
            return next(
                (d.id for d in departments if d.name.lower() == name.lower()),
                None,
            )

        # 1️⃣ User CONFIRMS suggested department ✅ (FIX)
        if input_data.get("confirm") is True and self.state.department_suggested:
            dept_id = _find_department_id(self.state.department_suggested)
            self.update_state(
                department_final=self.state.department_suggested,
                department_id=dept_id,
                department_overridden=False,
            )
            self.transition_to(RegistrationStep.SELECT_DOCTOR)
            return await self.handle({})

        # 2️⃣ User OVERRIDES department
        if "department_override" in input_data:
            override_name = input_data["department_override"]
            dept_id = _find_department_id(override_name)
            self.update_state(
                department_final=override_name,
                department_id=dept_id,
                department_overridden=True,
            )
            self.transition_to(RegistrationStep.SELECT_DOCTOR)
            return await self.handle({})

        # 3️⃣ Hard rule: Pediatrics
        if self.state.age is not None and self.state.age < 18:
            pediatrics_id = _find_department_id("Pediatrics")
            self.update_state(
                department_final="Pediatrics",
                department_id=pediatrics_id,
                department_confidence=1.0,
                department_reasoning=["Patient is under 18"],
            )
            self.transition_to(RegistrationStep.SELECT_DOCTOR)
            return await self.handle({})

        # 4️⃣ LLM-based resolution
        result = DepartmentResolverService.resolve(
            symptom_summary=self.state.symptoms_summary,
            age=self.state.age,
            allowed_departments=dept_names,
        )

        if not result:
            return {
                "message": "Please select a department.",
                "departments": dept_names,
            }

        dept_id = _find_department_id(result["department"])
        self.update_state(
            department_suggested=result["department"],
            department_confidence=result["confidence"],
            department_reasoning=result["reasoning"],
            department_id=dept_id,
        )

        if result["confidence"] >= CONFIDENCE_THRESHOLD:
            return {
                "message": f"We recommend {result['department']}. Do you want to proceed?",
                "suggested_department": result["department"],
                "confidence": result["confidence"],
                "reasoning": result["reasoning"],
                "expected_input": ["confirm", "department_override"],
            }

        return {
            "message": "Please confirm or select a department.",
            "suggested_department": result["department"],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"],
            "departments": dept_names,
        }


    async def _handle_select_doctor(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        doctors = await DoctorService.list_available_by_department(
            self.db,
            self.state.department_id,
        )

        if not doctors:
            return {
                "message": f"No doctors available in {self.state.department_id}."
            }

        doctor_id = input_data.get("doctor_id")

        if not doctor_id:
            return {
                "message": "Please select a doctor.",
                "doctors": [
                    {
                        "id": str(d.id),
                        "name": d.name,
                        "specialization": d.specialization,
                    }
                    for d in doctors
                ],
            }

        selected = next((d for d in doctors if str(d.id) == doctor_id), None)

        if not selected:
            return {
                "message": "Invalid doctor selection.",
            }

        self.update_state(doctor_id=selected.id)
        self.transition_to(RegistrationStep.CREATE_VISIT)

        return await self.handle({})

    async def _handle_create_visit(self) -> Dict[str, Any]:
        visit = await VisitService.create_with_token(
            self.db,
            patient_id=self.state.patient_id,
            doctor_id=self.state.doctor_id,
            symptoms_summary=self.state.symptoms_summary,
        )

        self.update_state(
            visit_id=visit.id,
            token_number=visit.token_number,
        )

        self.transition_to(RegistrationStep.HANDOFF_COMPLETE)

        return {
            "message": f"Visit registered successfully. Token number: {visit.token_number}",
            "token_number": visit.token_number,
        }

    async def _handle_handoff(self) -> Dict[str, Any]:
        payload = {
            "visit_id": self.state.visit_id,
            "patient_id": self.state.patient_id,
            "doctor_id": self.state.doctor_id,
            "department": self.state.department_final,  # ✅ FINAL, authoritative
            "symptoms_summary": self.state.symptoms_summary,
            "token_number": self.state.token_number,

            
            "department_suggested": self.state.department_suggested,
            "department_confidence": self.state.department_confidence,
            "department_reasoning": self.state.department_reasoning,
            "department_overridden": self.state.department_overridden,
        }

        result = handoff_to_doctor_agent(payload)

        return {
            "message": "You have been successfully registered. "
                    "Please proceed to the consultation.",
            "handoff_status": result,
        }
