"""
gemini_client.py
Google Gemini AI Integration for AgriVoice.
Uses Gemini 2.5/1.5 Flash to augment crop diagnosis and agricultural reasoning
in the farmer's exact detected language (Telugu, Hindi, or English).
"""

import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

class GeminiClient:
    """Interface to Google Gemini Generative AI for Agricultural Reasoning."""

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    MODEL_NAME = "gemini-2.5-flash"

    @classmethod
    def is_available(cls) -> bool:
        return bool(cls.GEMINI_API_KEY)

    @classmethod
    def generate_agricultural_advice(
        cls,
        crop: str,
        symptoms: str,
        duration: str,
        severity: str,
        language: str = "te"
    ) -> Optional[str]:
        """
        Calls Gemini API to generate concise, spoken-audio friendly agricultural diagnosis
        in the farmer's target language (Telugu, Hindi, or English).
        """
        if not cls.GEMINI_API_KEY:
            return None

        lang_instructions = {
            "te": "Respond strictly in warm, colloquial North Andhra Telugu (Srikakulam/Anakapalli yaasa). Keep sentences short and easy to understand over a phone speaker.",
            "hi": "Respond strictly in simple, respectful rural Hindi (किसान भाई शैली). Keep sentences clear for a phone call.",
            "en": "Respond in simple Indian English, clear and concise for spoken audio."
        }

        lang_prompt = lang_instructions.get(language, lang_instructions["te"])

        system_instruction = (
            "You are an empathetic, highly experienced AI Agricultural Doctor on a rural telephone helpline. "
            "You are advising a smallholder farmer over a 2G keypad phone. "
            f"{lang_prompt} "
            "Include: 1) Identified disease name. 2) Exact chemical spray dosage per 16-liter knapsack pump. "
            "3) Simple organic remedy. 4) Weather precaution. Do not use bullet points or markdown formatting—write natural spoken sentences."
        )

        user_content = (
            f"Farmer Crop: {crop}\n"
            f"Observed Symptoms: {symptoms}\n"
            f"Disease Duration: {duration}\n"
            f"Severity/Spread: {severity}\n"
            "Provide the immediate treatment prescription in under 4 sentences."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{cls.MODEL_NAME}:generateContent?key={cls.GEMINI_API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_instruction}\n\n{user_content}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 250
            }
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception as e:
            # Silently fall back to built-in expert state machine
            pass

        return None
