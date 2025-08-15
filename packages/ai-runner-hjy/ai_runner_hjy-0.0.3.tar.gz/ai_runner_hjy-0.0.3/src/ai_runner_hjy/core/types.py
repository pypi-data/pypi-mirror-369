from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


@dataclass
class RunResult:
    status: int
    duration_ms: int
    trace_id: str
    response: Optional[Dict[str, Any]]
    error: Optional[Tuple[str, str]]
    meta: Dict[str, Any]
    usage: Optional[Dict[str, Any]] = None


