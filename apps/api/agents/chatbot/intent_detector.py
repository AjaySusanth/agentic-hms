import os
import json
from typing import Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


async def detect_intent(user_message: str) -> Dict[str, Any]:
    """
    Uses Groq LLM to classify user intent from their message.
    
    Returns:
        {
            "intent": "medical" | "hotel_booking" | "general_query",
            "department_hint": "Cardiology" | None,
            "confidence": 0.0-1.0,
            "reasoning": "..."
        }
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are an intent classifier for a multi-hospital management system chatbot.

Classify the user's message into one of these intents:
1. "medical" - The user needs medical help, wants to see a doctor, has symptoms, or wants to book an appointment.
2. "hotel_booking" - The user needs accommodation/hotel near a hospital.
3. "general_query" - General questions about hospitals, directions, timings, etc.

Also, if the intent is "medical", try to suggest a likely medical department:
- General Medicine (fever, cold, general health)
- Cardiology (chest pain, heart issues)
- Orthopedics (bone, joint, muscle issues)
- Pediatrics (child under 18)
- Dermatology (skin issues)
- ENT (ear, nose, throat)
- Neurology (headache, brain, nerves)

User message: "{user_message}"

Respond ONLY with valid JSON (no markdown):
{{"intent": "medical", "department_hint": "Cardiology", "confidence": 0.9, "reasoning": "User mentions chest pain"}}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a JSON-only intent classifier. Always return valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=200,
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: if LLM doesn't return valid JSON
        result = {
            "intent": "medical",
            "department_hint": None,
            "confidence": 0.5,
            "reasoning": "Could not parse LLM response, defaulting to medical",
        }

    return result
