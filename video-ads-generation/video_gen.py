import os
from typing import Any, Dict, Optional

import requests


DEFAULT_GEMINI_MODEL = "gemini-1.5-flash"


def _get_api_key() -> Optional[str]:
    """Return the configured Gemini API key with backwards compatibility."""
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("KIE_API_TOKEN")
        or os.getenv("KIE_API_KEY")
    )


def _normalise_model(model: Optional[str]) -> str:
    """Map legacy model names to Gemini equivalents."""
    if not model:
        return DEFAULT_GEMINI_MODEL

    mapping = {
        "veo3_fast": "gemini-1.5-flash",
        "veo3": "gemini-1.5-pro",
    }
    return mapping.get(model, model)


def start_video_generation(prompt: str, aspect_ratio: str, model: Optional[str] = None) -> Dict[str, Any]:
    """Generate a video storyboard using Gemini."""
    api_key = _get_api_key()
    if not api_key:
        return {
            "status": "failed",
            "error": "Missing Gemini API key. Set GEMINI_API_KEY or KIE_API_TOKEN.",
        }

    target_model = _normalise_model(model)
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent"

    system_instruction = (
        "You are an award-winning video director. Given a creative brief, craft a detailed "
        "storyboard for an AI-generated marketing video. Include shot structure, camera "
        "movement, visual details, and narration so another model can later render the video."
    )

    user_prompt = (
        "Create a cinematic marketing video plan using the following prompt inspiration.\n\n"
        f"Aspect ratio: {aspect_ratio}\n"
        "Deliver the response as JSON with the following schema:\n"
        "{\n"
        "  \"overview\": \"Short summary of the video concept\",\n"
        "  \"shots\": [\n"
        "    {\n"
        "      \"timestamp\": \"0s-2s\",\n"
        "      \"visuals\": \"Visual description\",\n"
        "      \"camera\": \"Camera movements or lens notes\",\n"
        "      \"narration\": \"On-screen text or voiceover\"\n"
        "    }\n"
        "  ],\n"
        "  \"call_to_action\": \"Closing message\"\n"
        "}\n\n"
        "Prompt inspiration:\n"
        f"{prompt}"
    )

    payload: Dict[str, Any] = {
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
            "temperature": 0.7,
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
    text_response = _extract_text_from_response(data)
    if not text_response:
        return {
            "status": "failed",
            "error": "Gemini response did not include any text output.",
            "details": data,
        }

    return {
        "status": "completed",
        "response": {
            "text": text_response,
            "raw": data,
        },
    }


def _extract_text_from_response(data: Dict[str, Any]) -> str:
    candidates = data.get("candidates", [])
    for candidate in candidates:
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        lines = []
        for part in parts:
            text = part.get("text")
            if text:
                lines.append(text)
        if lines:
            return "\n".join(lines).strip()
    return ""
