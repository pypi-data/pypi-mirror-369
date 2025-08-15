from .core.config import AppConfig, get_config, validate_required_fields
from .core.db import get_db_connection
from .run import run_once
from .route import run_route
from .core.oss import upload_file

__all__ = [
    "AppConfig",
    "get_config",
    "init",
    "validate_required_fields",
    "run_once",
    "run_route",
    "get_db_connection",
    "upload_file",
]


def init(config_dict: dict) -> AppConfig:
    """
    Create an AppConfig from a plain dict and validate required fields.

    This provides an explicit dict-driven initialization for consumers who
    prefer dependency injection over env-based loading.
    """
    cfg = AppConfig(_env_file=None, **config_dict)
    validate_required_fields(cfg)
    return cfg

