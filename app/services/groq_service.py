import json
from typing import Any
from groq import Groq

from app.core.config import settings
from app.prompts import (
    RESUME_ANALYSIS_SYSTEM_PROMPT,
    get_resume_analysis_user_prompt,
)


class GroqService:
    # llama-3.3-70b-versatile is the best model on Groq for high-accuracy JSON extraction & reasoning
    MODEL_NAME = "llama-3.3-70b-versatile"

    @classmethod
    def get_client(cls) -> Groq:
        """Grabs the Groq client using the API key from .env."""
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set in your .env file! Please add it to analyze resumes."
            )
        return Groq(api_key=settings.GROQ_API_KEY)

    @classmethod
    def analyze_resume(cls, resume_text: str) -> dict[str, Any]:
        """
        Sends raw resume text to Groq, forces JSON output, and returns
        the parsed candidate profile dict matching the ResumeAnalysis schema.
        """
        client = cls.get_client()

        # Call Groq's chat completion with JSON object enforcement
        response = client.chat.completions.create(
            model=cls.MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": RESUME_ANALYSIS_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": get_resume_analysis_user_prompt(resume_text),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,  # low temperature keeps facts strict and prevents hallucinations
        )

        raw_content = response.choices[0].message.content or "{}"

        try:
            parsed_data = json.loads(raw_content)
        except json.JSONDecodeError:
            parsed_data = {}

        return parsed_data