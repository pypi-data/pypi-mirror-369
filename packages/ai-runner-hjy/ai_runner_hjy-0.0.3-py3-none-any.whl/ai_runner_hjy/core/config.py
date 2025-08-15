from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional, List
import loguru
import sys
import os
from .errors import ConfigError

# Centralized logger
logger = loguru.logger
logger.remove()
logger.add(
    sys.stderr,
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
)

class AppConfig(BaseSettings):
    """
    Defines the application's configuration using Pydantic.
    It reads from environment variables and .env files.
    """
    model_config = SettingsConfigDict(
        env_file=(".env", "basic.env", "mysql.env", "oss.env", "ai.env"),
        env_file_encoding='utf-8',
        extra='ignore',
        populate_by_name=True,
    )

    # Project
    project_name: Optional[str] = Field("default_project", alias='PROJECT_NAME')

    # MySQL
    mysql_host: Optional[str] = Field(None, alias='MYSQL_HOST')
    mysql_user: Optional[str] = Field(None, alias='MYSQL_USER')
    mysql_password: Optional[str] = Field(None, alias='MYSQL_PASSWORD')
    mysql_port: Optional[int] = Field(3306, alias='MYSQL_PORT')
    mysql_ai_database: Optional[str] = Field(None, alias='MYSQL_AI_DATABASE')

    # OSS
    oss_access_key_id: Optional[str] = Field(None, alias='OSS_ACCESS_KEY_ID')
    oss_access_key_secret: Optional[str] = Field(None, alias='OSS_ACCESS_KEY_SECRET')
    oss_bucket_name: Optional[str] = Field(None, alias='OSS_BUCKET_NAME')
    oss_endpoint: Optional[str] = Field(None, alias='OSS_ENDPOINT')

    # AI / runtime
    ai_pepper: Optional[str] = Field(None, alias='AI_PEPPER')
    ai_timeout: int = Field(60, alias='AI_TIMEOUT')
    json_schema_enforce: bool = Field(True, alias='JSON_SCHEMA_ENFORCE')
    enforce_no_english: bool = Field(True, alias='ENFORCE_NO_ENGLISH')
    enable_oss_spillover: bool = Field(False, alias='ENABLE_OSS_SPILLOVER')

_config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    """
    Returns a singleton AppConfig instance.
    """
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def validate_required_fields(config: AppConfig) -> None:
    """
    Validate mandatory configuration at startup. Raise ValueError with a clear message if missing.

    Required fields:
    - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_AI_DATABASE
    - AI_PEPPER
    """
    missing: List[str] = []
    if not config.mysql_host:
        missing.append("MYSQL_HOST")
    if not config.mysql_user:
        missing.append("MYSQL_USER")
    if not config.mysql_password:
        missing.append("MYSQL_PASSWORD")
    if not config.mysql_ai_database:
        missing.append("MYSQL_AI_DATABASE")
    if not config.ai_pepper:
        missing.append("AI_PEPPER")

    if missing:
        raise ConfigError(f"Missing required configuration: {', '.join(missing)}")