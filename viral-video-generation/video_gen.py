import os
from typing import Any, Dict, Optional

import requests


DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"


def _get_api_key() -> Optional[str]:
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("KIE_API_TOKEN")
        or os.getenv("KIE_API_KEY")
    )


def start_video_generation(prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
    """Generate a storyboard using Gemini for the supplied prompt."""
    api_key = _get_api_key()
    if not api_key:
        return {
            "status": "failed",
            "error": "Missing Gemini API key. Set GEMINI_API_KEY or KIE_API_TOKEN.",
        }

    target_model = model or DEFAULT_GEMINI_MODEL
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent"

    system_instruction = (
        "You are an AI creative director specialising in viral short-form videos."
        " Produce a JSON storyboard with time-coded shots, visuals, camera notes,"
        " and narration that can be handed to a video generation model."
    )

    user_prompt = (
        "Create a viral short-form video plan using this generated prompt:\n\n"
        f"{prompt}"
    )

    payload = {
        "systemInstruction": {
            "role": "system",
            "parts": [{"text": system_instruction}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        ],
        "generationConfig": {
            "temperature": 0.9,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 2048,
        },
    }

    try:
        response = requests.post(
            endpoint,
            params={"key": api_key},
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        return {
            "status": "failed",
            "error": f"Gemini request failed: {exc}",
        }

    if response.status_code != 200:
        return {
            "status": "failed",
            "error": f"Gemini API error {response.status_code}",
            "details": response.text,
        }

    data = response.json()
    storyboard = _extract_text_from_response(data)

    if not storyboard:
        return {
            "status": "failed",
            "error": "Gemini response did not include any text output.",
            "details": data,
        }

    return {
        "status": "completed",
        "response": {
            "text": storyboard,
            "raw": data,
        },
    }


def _extract_text_from_response(data: Dict[str, Any]) -> str:
    candidates = data.get("candidates", [])
    for candidate in candidates:
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        text_output = []
        for part in parts:
            text = part.get("text")
            if text:
                text_output.append(text)
        if text_output:
            return "\n".join(text_output).strip()
    return ""
