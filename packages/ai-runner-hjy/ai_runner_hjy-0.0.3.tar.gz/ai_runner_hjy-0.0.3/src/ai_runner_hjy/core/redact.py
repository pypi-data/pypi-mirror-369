from __future__ import annotations

import re
from typing import Dict, Any


def mask_api_key(value: str) -> str:
    if not value:
        return value
    return re.sub(r".+", "****MASKED", value)


def redact_url(url: str) -> str:
    if not isinstance(url, str):
        return url
    # strip query string and fragment
    url = url.split("?", 1)[0].split("#", 1)[0]
    return url


def demo_response_shape(resp: Dict[str, Any]) -> Dict[str, Any]:
    # deep copy shape but replace content with demo text
    import copy
    out = copy.deepcopy(resp) if isinstance(resp, dict) else {"object": "chat.completion"}
    try:
        choices = out.get("choices") or []
        if choices and isinstance(choices[0], dict):
            msg = choices[0].get("message") or {}
            msg["content"] = "{\"result\":\"【仅供展示】示例输出结构\",\"tags\":[\"demo\",\"structure\"],\"score\":0.98}"
            choices[0]["message"] = msg
            out["choices"] = choices
    except Exception:
        out["choices"] = [{"message": {"content": "{\"result\":\"【仅供展示】示例输出结构\"}"}}]
    return out


