class AiRunnerError(Exception):
    """Base error for ai-runner-hjy."""


class ConfigError(AiRunnerError):
    """Configuration invalid or missing required fields."""


class AiConnectionError(AiRunnerError):
    """Database connectivity or authentication error."""


class ProviderError(AiRunnerError):
    """Downstream AI provider error or non-retriable HTTP error."""


class SchemaError(AiRunnerError):
    """Response schema/JSON validation error."""


def human_hint(exc: Exception) -> str:
    """Return a human-friendly hint for common error types."""
    if isinstance(exc, ConfigError):
        return "配置缺失或不合法，请补齐必填项（MYSQL_* 与 AI_PEPPER），或使用 init({...}) 显式注入。"
    if isinstance(exc, AiConnectionError):
        return "检查 DB 主机/端口/白名单与账号权限（至少 SELECT），可运行 'ai-runner doctor' 辅助排查。"
    if isinstance(exc, ProviderError):
        return "检查下游提供商状态与 API Key，必要时降低速率或稍后重试。"
    if isinstance(exc, SchemaError):
        return "确保启用 JSON 输出（response_format 或 JSON_SCHEMA_ENFORCE），并调整 Prompt 约束。"
    return "请参考 README 的 FAQ 与 'ai-runner doctor'。"


