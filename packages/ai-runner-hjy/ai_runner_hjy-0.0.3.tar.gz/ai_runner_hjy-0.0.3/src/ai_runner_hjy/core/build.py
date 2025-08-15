import json
import os
from typing import Any, Dict, Tuple, Optional

from .crypto_utils import decrypt_api_key
from .config import AppConfig


def apply_variables(messages: Any, variables: Dict[str, Any]) -> Any:
    def replace_in_str(s: str) -> str:
        out = s
        for k, v in variables.items():
            out = out.replace(f"{{{{{k}}}}}", str(v))
        return out

    def replace_in_obj(obj: Any) -> Any:
        if isinstance(obj, str):
            return replace_in_str(obj)
        if isinstance(obj, list):
            return [replace_in_obj(x) for x in obj]
        if isinstance(obj, dict):
            return {k: replace_in_obj(v) for k, v in obj.items()}
        return obj

    return replace_in_obj(messages)


def _validate_media_urls(messages: Any) -> None:
    """Strict check: if any media slot exists with empty/missing url, raise."""
    def walk(x: Any):
        if isinstance(x, list):
            for i in x:
                walk(i)
        elif isinstance(x, dict):
            t = x.get("type")
            if t == "image_url" and isinstance(x.get("image_url"), dict):
                url = x["image_url"].get("url")
                if url in (None, ""):
                    raise RuntimeError("MISSING_MEDIA_URL: image_url.url is empty after substitution")
            if t == "input_audio" and isinstance(x.get("input_audio"), dict):
                url = x["input_audio"].get("url")
                if url in (None, ""):
                    raise RuntimeError("MISSING_MEDIA_URL: input_audio.url is empty after substitution")
            for v in x.values():
                walk(v)
    walk(messages)


def build_request_from_row(row: Dict[str, Any], config: Optional[AppConfig] = None) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
    if not config:
        from .config import get_config
        config = get_config()

    url = row["base_url"]
    api_key_blob = json.loads(row["api_key_encrypted"]) if isinstance(row["api_key_encrypted"], str) else row["api_key_encrypted"]
    try:
        api_key = decrypt_api_key(api_key_blob, config.ai_pepper)  # do not log
    except Exception as exc:
        raise RuntimeError("DECRYPT_FAILED") from exc

    params = json.loads(row["params_json"]) if row.get("params_json") and isinstance(row["params_json"], str) else (row.get("params_json") or {})
    messages = json.loads(row["messages_json"]) if row.get("messages_json") and isinstance(row["messages_json"], str) else (row.get("messages_json") or [])
    rf = row.get("response_format_json")
    if isinstance(rf, str):
        rf = json.loads(rf)
    variables = json.loads(row["variables_json"]) if row.get("variables_json") and isinstance(row["variables_json"], str) else (row.get("variables_json") or {})

    if isinstance(variables, dict):
        messages = apply_variables(messages, {**params, **variables})
    else:
        messages = apply_variables(messages, params)

    # Strict validation – do not auto-fill
    _validate_media_urls(messages)

    body: Dict[str, Any] = {"model": row["model_name"]}
    if isinstance(messages, dict) and "messages" in messages:
        body.update(messages)
    else:
        body["messages"] = messages

    mapping = {
        "TEMPERATURE": "temperature",
        "TOP_P": "top_p",
        "MAX_TOKENS": "max_tokens",
        "STREAM": "stream",
        "STOP": "stop",
        "N": "n",
        "FREQUENCY_PENALTY": "frequency_penalty",
        "PRESENCE_PENALTY": "presence_penalty",
    }
    for k, v in params.items():
        if k in mapping:
            body[mapping[k]] = v

    if rf:
        body["response_format"] = rf
    elif params.get("JSON_SCHEMA_ENFORCE"):
        body["response_format"] = {"type": "json_object"}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return url, headers, body

