import json
from typing import Any
from groq import Groq

from app.core.config import settings
from app.prompts import (
    RESUME_ANALYSIS_SYSTEM_PROMPT,
    get_resume_analysis_user_prompt,
)


class GroqService:
    MODEL_NAME = "openai/gpt-oss-20b"

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

    @classmethod
    def analyze_job_expectations_and_dsa(
        cls, title: str, company: str, description: str
    ) -> dict[str, Any]:
        """
        Analyzes an internship or job posting to evaluate:
        1. DSA requirement level ('Low', 'Moderate', 'Heavy')
        2. DSA requirement rationale
        3. Real job expectations (what the intern will build)
        4. Brief intelligence on what the company builds
        """
        if not settings.GROQ_API_KEY:
            return {
                "dsa_level": "Moderate",
                "dsa_reason": "Standard engineering assessment with basic problem solving.",
                "expectations": ["Assist with code development and testing", "Collaborate with senior engineers"],
                "company_intel": f"{company} is hiring for {title}.",
            }

        client = cls.get_client()

        system_prompt = (
            "You are a technical career advisor analyzing tech internships and junior developer jobs in India and globally. "
            "Given a job title, company name, and description, you must evaluate the DSA (Data Structures & Algorithms) expectation:\n"
            "- 'Low': Focuses primarily on development, frameworks (React, Django, FastAPI, Node), projects, REST APIs, or take-home tasks. Little to no LeetCode rounds.\n"
            "- 'Moderate': Involves standard problem solving (arrays, strings, basic hashmaps, sorting, basic SQL) along with practical questions.\n"
            "- 'Heavy': Demanding algorithmic rounds (LeetCode medium/hard, Trees, Graphs, Dynamic Programming). Common in Big Tech and elite product companies.\n\n"
            "Return valid JSON matching this schema:\n"
            "{\n"
            '  "dsa_level": "Low" | "Moderate" | "Heavy",\n'
            '  "dsa_reason": "1 short sentence explaining why this level is expected",\n'
            '  "expectations": ["bullet 1", "bullet 2", "bullet 3"],\n'
            '  "company_intel": "1-2 sentences summarizing what the company builds or does"\n'
            "}"
        )

        user_content = f"Title: {title}\nCompany: {company}\n\nJob Description:\n{description[:2500]}"

        try:
            response = client.chat.completions.create(
                model=cls.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw = response.choices[0].message.content or "{}"
            data = json.loads(raw)
            dsa = data.get("dsa_level", "Moderate")
            if dsa not in ["Low", "Moderate", "Heavy"]:
                dsa = "Moderate"
            return {
                "dsa_level": dsa,
                "dsa_reason": data.get("dsa_reason", "Standard problem solving and development skills expected."),
                "expectations": data.get("expectations", ["Build and maintain features", "Write clean testable code"]),
                "company_intel": data.get("company_intel", f"{company} provides technology solutions."),
            }
        except Exception as e:
            return {
                "dsa_level": "Moderate",
                "dsa_reason": "Standard problem solving and development skills expected.",
                "expectations": ["Build and maintain features", "Write clean testable code"],
                "company_intel": f"{company} is hiring for {title}.",
            }

