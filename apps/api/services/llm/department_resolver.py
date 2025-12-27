import os
import json
from typing import Dict, List, Optional
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


class DepartmentResolverService:
    """
    Uses gpt-oss-120b to suggest a department with confidence and reasoning.
    """

    MODEL = "openai/gpt-oss-120b"

    @staticmethod
    def resolve(
        *,
        symptom_summary: str,
        age: int | None,
        allowed_departments: List[str],
    ) -> Optional[Dict]:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        department_list = ", ".join(allowed_departments)

        prompt = f"""
You are a hospital triage assistant.

Choose ONE department from this list ONLY:
{department_list}

Return STRICT JSON in the following format:

{{
  "department": "<department name>",
  "confidence": <float between 0 and 1>,
  "reasoning": ["short bullet point", "short bullet point"]
}}

Rules:
- Do not diagnose
- Do not invent departments
- If age below 18, choose 'Pediatrics'
- If unsure, lower the confidence
- Max 3 reasoning bullets

Patient age: {age}
Symptoms:
{symptom_summary}
"""

        response = client.chat.completions.create(
            model=DepartmentResolverService.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You assist with hospital department routing."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
        )

        raw_output = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            return None

        # Strict validation
        if (
            not isinstance(parsed, dict)
            or parsed.get("department") not in allowed_departments
            or not isinstance(parsed.get("confidence"), (float, int))
            or not isinstance(parsed.get("reasoning"), list)
        ):
            return None

        parsed["confidence"] = float(parsed["confidence"])
        return parsed
