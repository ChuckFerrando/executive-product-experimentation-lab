import json
import os
from typing import Optional


def _extract_text(response) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text.strip()

    parts = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def generate_text(
    developer_prompt: str,
    user_prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        chosen_model = model or os.getenv("OPENAI_MODEL", "gpt-5.4")

        response = client.responses.create(
            model=chosen_model,
            input=[
                {"role": "developer", "content": developer_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return _extract_text(response)
    except Exception:
        return None


def generate_json(
    developer_prompt: str,
    user_prompt: str,
    schema_name: str,
    schema: dict,
    model: Optional[str] = None,
) -> Optional[dict]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        chosen_model = model or os.getenv("OPENAI_MODEL", "gpt-5.4")

        response = client.responses.create(
            model=chosen_model,
            input=[
                {"role": "developer", "content": developer_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": schema,
                    "strict": True,
                }
            },
        )
        text = _extract_text(response)
        return json.loads(text) if text else None
    except Exception:
        return None
