from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Protocol


class RouteProvider(Protocol):
    def resolve(self, project: str, route_key: str, *, runtime_variables: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, str], Dict[str, Any], Dict[str, Any]]:
        """Return (url, headers, body, meta) for a route.

        meta should minimally include {"config_key": str}.
        """


class CredentialProvider(Protocol):
    def get(self, config_key: str) -> Tuple[str, str]:
        """Return (base_url, api_key_or_token) for a given config key."""


class LoggerHook(Protocol):
    def before_call(self, event: Dict[str, Any]) -> None: ...
    def after_call(self, event: Dict[str, Any]) -> None: ...


class DefaultRouteProvider:
    """Default adapter that delegates to the existing core.resolve_route.

    This keeps backward-compatibility while allowing users to inject their own
    providers without importing DB/Web in the core runner.
    """

    def resolve(self, project: str, route_key: str, *, runtime_variables: Optional[Dict[str, Any]] = None):
        from .core.routing import resolve_route  # local import to avoid hard deps in import graph

        return resolve_route(project, route_key, runtime_variables=runtime_variables)


class NoopLogger:
    def before_call(self, event: Dict[str, Any]) -> None:
        return

    def after_call(self, event: Dict[str, Any]) -> None:
        return

