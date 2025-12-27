import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import asyncio

class SymptomSummarizerService:

    MODEL = "llama-3.1-8b-instant"

    @staticmethod
    def _summarize_sync(symptoms_raw: str) -> str:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
            Summarize the following patient symptoms clearly and concisely.
            Do NOT diagnose.
            Do NOT suggest departments.
            Do NOT give medical advice.

            Symptoms:
            {symptoms_raw}
            """

        response = client.chat.completions.create(
            model=SymptomSummarizerService.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a clinical note summarizer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content.strip()
    
    @staticmethod
    async def summarize(symptoms_raw: str) -> str:
        # ✅ Async-safe wrapper
        return await asyncio.to_thread(
            SymptomSummarizerService._summarize_sync,
            symptoms_raw,
        )
        
