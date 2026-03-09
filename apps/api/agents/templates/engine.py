"""
Template Engine — Generic Workflow Runner.

The heart of the Option B template system. Takes a workflow template
(the WHAT) and a client config (the WHERE), and runs the steps
deterministically.

Step types:
  - collect_input: Prompt user, store their answer, advance
  - api_call: Map fields, call external API, format response
"""

import os
import re
import httpx
from typing import Any, Dict, Optional

from agents.templates.schemas import IntegrationConfig, TemplateDefinition
from agents.templates.state import TemplateWorkflowState


class TemplateEngine:
    """
    Loads a workflow template + client config,
    runs the steps deterministically.
    """

    def __init__(
        self,
        template: TemplateDefinition,
        config: IntegrationConfig,
        state: TemplateWorkflowState,
    ):
        self.template = template
        self.config = config
        self.state = state

    async def handle(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main handler — called on each user interaction.
        Routes to the current step's handler.
        """
        step = self.template.get_step(self.state.current_step_id)

        if step is None:
            return self._reply("This session has already been completed.")

        if step.type == "collect_input":
            return await self._handle_collect_input(step, user_input)
        elif step.type == "api_call":
            return await self._handle_api_call(step, user_input)
        else:
            return self._reply(f"Unknown step type: {step.type}")

    # ── Step Handlers ───────────────────────────────────────────

    async def _handle_collect_input(self, step, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect input step: parse user's message, store fields, advance.
        If no message yet (first time hitting this step), show the prompt.
        """
        message = user_input.get("message", "").strip()

        # If no message, show the step's prompt
        if not message:
            return self._reply(step.prompt or "Please provide the required information.")

        # Parse and store fields based on the step
        self._extract_fields(step, message)

        # Advance to next step
        next_step_id = step.next
        if next_step_id == "completed":
            self.state.step = "completed"
            return self._reply("✅ All done! Thank you.")

        self.state.current_step_id = next_step_id
        next_step = self.template.get_step(next_step_id)

        # If next step is an API call, execute it immediately
        if next_step and next_step.type == "api_call":
            return await self._handle_api_call(next_step, {})

        # Otherwise, show the next step's prompt
        prompt = next_step.prompt if next_step else "Please continue."
        return self._reply(prompt)

    async def _handle_api_call(self, step, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        API call step: build request from collected_data, call external API,
        format response, and advance.
        """
        action = step.action
        if not action:
            return self._reply("Configuration error: API call step has no action defined.")

        try:
            result = await self._call_api(action)
        except Exception as e:
            return self._reply(f"Sorry, there was an error connecting to the service: {str(e)}")

        # Cache the result
        self.state.api_results[action] = result

        # Format the response
        formatted = self._format_api_result(action, result)

        # Build the prompt with results
        prompt = step.prompt or "{results}"
        response_text = prompt.replace("{results}", formatted)

        # Advance to next step
        next_step_id = step.next
        if next_step_id == "completed":
            self.state.step = "completed"
            return self._reply(response_text)

        self.state.current_step_id = next_step_id
        return self._reply(response_text)

    # ── API Calling ─────────────────────────────────────────────

    async def _call_api(self, action: str) -> Dict[str, Any]:
        """
        Make an HTTP call to the external API based on the config.
        Applies field_mappings before sending.
        """
        endpoint_spec = self.config.endpoints.get(action)
        if not endpoint_spec:
            raise ValueError(f"No endpoint configured for action: {action}")

        method, path = endpoint_spec.split(" ", 1)
        url = self.config.base_url.rstrip("/") + path

        # Map our field names to their field names
        mapped_data = self._map_fields(self.state.collected_data)

        # Build auth headers
        headers = {"Content-Type": "application/json"}
        if self.config.auth.type == "api_key" and self.config.auth.header:
            api_key = os.getenv(self.config.auth.value_env or "", "")
            headers[self.config.auth.header] = api_key
        elif self.config.auth.type == "bearer" and self.config.auth.value_env:
            token = os.getenv(self.config.auth.value_env, "")
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            if method.upper() == "GET":
                # For GET, send mapped data as query params
                resp = await client.get(url, params=mapped_data, headers=headers)
            elif method.upper() == "POST":
                # For POST, send as JSON body
                resp = await client.post(url, json=mapped_data, headers=headers)
            elif method.upper() == "DELETE":
                resp = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        resp.raise_for_status()
        return resp.json()

    # ── Field Mapping ───────────────────────────────────────────

    def _map_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply field_mappings from config: our field name → their field name."""
        mappings = self.config.field_mappings
        mapped = {}
        for our_key, value in data.items():
            their_key = mappings.get(our_key, our_key)
            mapped[their_key] = value
        return mapped

    # ── Field Extraction ────────────────────────────────────────

    def _extract_fields(self, step, message: str):
        """
        Parse user message and store values for the step's expected fields.
        Uses simple pattern matching — can be enhanced with LLM later.
        """
        fields = step.fields

        if step.id == "collect_date_time":
            # Try to extract date and time from natural language
            self.state.collected_data["reservation_date"] = self._extract_date(message)
            self.state.collected_data["reservation_time"] = self._extract_time(message)

        elif step.id == "collect_party_size":
            # Extract number from message
            numbers = re.findall(r'\d+', message)
            self.state.collected_data["party_size"] = int(numbers[0]) if numbers else 2

        elif step.id == "select_table":
            # User picks a table by number from the list
            numbers = re.findall(r'\d+', message)
            if numbers:
                choice_idx = int(numbers[0]) - 1  # 1-indexed to 0-indexed
                tables = self.state.api_results.get("search_tables", {}).get("tables", [])
                if 0 <= choice_idx < len(tables):
                    selected = tables[choice_idx]
                    self.state.collected_data["selected_table_id"] = selected["id"]
                    self.state.collected_data["_selected_table"] = selected  # for display
                else:
                    # Default to first table
                    if tables:
                        self.state.collected_data["selected_table_id"] = tables[0]["id"]
                        self.state.collected_data["_selected_table"] = tables[0]

        elif step.id == "collect_guest_details":
            # Try to extract name and phone
            parts = re.split(r'[,\n]+', message)
            if len(parts) >= 2:
                self.state.collected_data["guest_name"] = parts[0].strip()
                # Extract phone from second part
                phone_match = re.findall(r'\d{10,}', parts[1])
                self.state.collected_data["phone"] = phone_match[0] if phone_match else parts[1].strip()
            else:
                # Single input — treat as name, ask phone later or use placeholder
                self.state.collected_data["guest_name"] = message.strip()
                self.state.collected_data["phone"] = "0000000000"

        else:
            # Generic: if single field, store the whole message
            if len(fields) == 1:
                self.state.collected_data[fields[0]] = message
            else:
                # Multi-field: try comma-separated
                parts = re.split(r'[,\n]+', message)
                for i, field in enumerate(fields):
                    if i < len(parts):
                        self.state.collected_data[field] = parts[i].strip()

    # ── Date/Time Parsing ───────────────────────────────────────

    def _extract_date(self, message: str) -> str:
        """
        Extract a date from natural language, returning YYYY-MM-DD.
        Simple pattern matching — can be replaced with LLM or dateparser.
        """
        # Try common formats: "March 15th", "15th March", "2026-03-15", "03/15/2026"

        # ISO format
        iso_match = re.search(r'(\d{4}-\d{2}-\d{2})', message)
        if iso_match:
            return iso_match.group(1)

        # "Month Day" pattern
        months = {
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12",
        }
        for month_name, month_num in months.items():
            pattern = rf'{month_name}\s+(\d{{1,2}})'
            match = re.search(pattern, message.lower())
            if match:
                day = match.group(1).zfill(2)
                return f"2026-{month_num}-{day}"

        # Fallback: return as-is
        return message.strip()

    def _extract_time(self, message: str) -> str:
        """
        Extract time from natural language, returning HH:MM.
        """
        # "7 PM", "7:00 PM", "19:00"
        time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm|AM|PM)', message)
        if time_match:
            hour = int(time_match.group(1))
            minutes = time_match.group(2) or "00"
            period = time_match.group(3).lower()
            if period == "pm" and hour != 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
            return f"{hour:02d}:{minutes}"

        # 24-hour format
        time_24 = re.search(r'(\d{1,2}):(\d{2})', message)
        if time_24:
            return f"{int(time_24.group(1)):02d}:{time_24.group(2)}"

        # Fallback
        return "19:00"

    # ── Result Formatting ───────────────────────────────────────

    def _format_api_result(self, action: str, result: Dict[str, Any]) -> str:
        """Format API response for display to the user."""
        if action == "search_tables":
            tables = result.get("tables", [])
            if not tables:
                return "No tables available for the selected date, time, and party size."

            lines = []
            for i, t in enumerate(tables, 1):
                lines.append(
                    f"  {i}. **Table {t['table_number']}** — "
                    f"{t['capacity']} seats, {t['location']}"
                    f"{' — ' + t.get('description', '') if t.get('description') else ''}"
                )
            return "\n".join(lines)

        elif action == "create_reservation":
            return (
                f"📋 **Reservation Details:**\n"
                f"  • **Restaurant**: {self.config.service_name}\n"
                f"  • **Date**: {self.state.collected_data.get('reservation_date', 'N/A')}\n"
                f"  • **Time**: {self.state.collected_data.get('reservation_time', 'N/A')}\n"
                f"  • **Guests**: {self.state.collected_data.get('party_size', 'N/A')}\n"
                f"  • **Name**: {self.state.collected_data.get('guest_name', 'N/A')}\n"
                f"  • **Confirmation ID**: {result.get('id', 'N/A')}"
            )

        else:
            # Generic JSON dump
            import json
            return f"```\n{json.dumps(result, indent=2)}\n```"

    # ── Reply Helper ────────────────────────────────────────────

    def _reply(self, message: str) -> Dict[str, Any]:
        """Build a standard reply dict."""
        self.state.messages.append({"role": "bot", "content": message})
        self.state.last_bot_message = message
        return {
            "message": message,
            "step": self.state.current_step_id,
            "workflow_status": self.state.step,
            "service_name": self.config.service_name,
        }
