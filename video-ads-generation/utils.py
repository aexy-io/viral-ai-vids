import asyncio
import json
import os
from datetime import datetime
from typing import Any, Optional, Type

import pandas as pd
import requests


# Excel file for logging
EXCEL_LOG_FILE = "ad_videos.xlsx"

DEFAULT_LLM_MODEL = "gemini-1.5-pro"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


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
        return DEFAULT_LLM_MODEL

    mapping = {
        "gpt-4.1": "gemini-1.5-pro",
        "gpt-4.1-mini": "gemini-1.5-flash",
        "gpt-3.5": "gemini-1.5-flash",
    }
    return mapping.get(model, model)


def _build_payload(system_prompt: str, user_message: str, temperature: float) -> dict[str, Any]:
    """Construct the Gemini request payload."""
    return {
        "systemInstruction": {
            "role": "system",
            "parts": [{"text": system_prompt}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_message}],
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 2048,
        },
    }


def _make_gemini_request(model: str, api_key: str, payload: dict[str, Any]) -> str:
    endpoint = f"{GEMINI_API_BASE}/{model}:generateContent"
    try:
        response = requests.post(
            endpoint,
            params={"key": api_key},
            json=payload,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise ValueError(f"Gemini request failed: {exc}") from exc

    if response.status_code != 200:
        raise ValueError(f"Gemini API error {response.status_code}: {response.text}")

    data = response.json()
    text_output = _extract_text_from_response(data)
    if not text_output:
        raise ValueError("Gemini response did not include any text output.")

    return text_output


def _extract_text_from_response(data: dict[str, Any]) -> str:
    candidates = data.get("candidates", [])
    for candidate in candidates:
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        lines: list[str] = []
        for part in parts:
            text = part.get("text")
            if text:
                lines.append(text)
        if lines:
            return "\n".join(lines).strip()
    return ""


def _coerce_structured_output(raw_text: str, response_format: Type[Any]):
    """Attempt to parse Gemini text into the requested structured type."""
    cleaned = _strip_code_fence(raw_text)

    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("Gemini response was not valid JSON for the requested structure") from exc

    # Pydantic v2
    if hasattr(response_format, "model_validate_json"):
        return response_format.model_validate_json(cleaned)

    # Pydantic v1 compatibility
    if hasattr(response_format, "parse_obj"):
        return response_format.parse_obj(payload)

    # TypedDicts or other callables
    try:
        return response_format(**payload)  # type: ignore[misc]
    except Exception:
        return payload


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped

    lines = stripped.splitlines()
    if not lines:
        return stripped

    if lines[0].startswith("```"):
        lines = lines[1:]

    # Drop closing fence if present
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()

async def ainvoke_llm(
    model,
    system_prompt,
    user_message,
    response_format=None,
    temperature=0.1,
):
    """Invoke Gemini asynchronously and optionally coerce to structured output."""

    api_key = _get_api_key()
    if not api_key:
        raise ValueError("Missing Gemini API key. Set GEMINI_API_KEY or KIE_API_TOKEN.")

    target_model = _normalise_model(model)
    payload = _build_payload(system_prompt, user_message, temperature)

    response_text = await asyncio.to_thread(
        _make_gemini_request,
        target_model,
        api_key,
        payload,
    )

    if response_format is None:
        return response_text

    return _coerce_structured_output(response_text, response_format)

def log_to_excel(data, row_index=None):
    """
    Log video generation data to Excel file.
    If row_index is provided, updates an existing row instead of creating a new one.
    Returns the DataFrame index of the entry (new or updated).
    """
    expected_columns = [
        'title', 'prompt',
        'status', 'task_id', 'video_url', 'gemini_output', 'error', 'created_at'
    ]

    if os.path.exists(EXCEL_LOG_FILE):
        df = pd.read_excel(EXCEL_LOG_FILE)
        # Ensure all expected columns are present for backwards compatibility
        for column in expected_columns:
            if column not in df.columns:
                df[column] = ""
    else:
        df = pd.DataFrame(columns=expected_columns)
    
    if row_index is not None and 0 <= row_index < len(df):
        # Update existing row
        for key, value in data.items():
            df.loc[row_index, key] = value
    else:
        # Create new row
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        row_index = len(df) - 1  # Get the index of the newly added row
    
    # Save to Excel
    df.to_excel(EXCEL_LOG_FILE, index=False)
    return row_index
