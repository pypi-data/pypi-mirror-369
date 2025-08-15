from __future__ import annotations

import os
from typing import Any, Dict, List


class Strategy:
    def select(self, members: List[Dict[str, Any]], route_row: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class PrimaryBackupStrategy(Strategy):
    def select(self, members: List[Dict[str, Any]], route_row: Dict[str, Any]) -> Dict[str, Any]:
        # Members already sorted by priority ASC
        return members[0]


class RoundRobinStrategy(Strategy):
    def select(self, members: List[Dict[str, Any]], route_row: Dict[str, Any]) -> Dict[str, Any]:
        project = route_row.get("project_name", "p")
        route_key = route_row.get("route_key", "r")
        key = f"AI_RR_{project}_{route_key}"
        try:
            idx = int(os.environ.get(key, "-1"))
        except ValueError:
            idx = -1
        idx = (idx + 1) % len(members)
        os.environ[key] = str(idx)
        return members[idx]


def get_strategy(name: str) -> Strategy:
    name = (name or "primary_backup").lower()
    if name == "round_robin":
        return RoundRobinStrategy()
    return PrimaryBackupStrategy()

