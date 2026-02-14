"""Application configuration via pydantic-settings.

Loads settings from environment variables and .env files.
Uses @lru_cache for singleton access throughout the application.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application configuration.

    All values can be overridden via environment variables or .env file.
    Thresholds and limits are configurable to support tuning without code changes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "AI Clinical Chatbot MVP"
    app_version: str = "0.1.0"
    app_env: str = "development"
    app_port: int = 8000
    debug: bool = True
    log_level: str = "INFO"

    # LLM Provider
    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_model: str = "gpt-4"
    llm_max_tokens: int = 300
    llm_temperature: float | None = None

    # Risk assessment thresholds (0-100 scale)
    risk_threshold_high: int = 60
    risk_threshold_critical: int = 80

    # Session limits
    session_max_messages_before_checkin: int = 15
    max_session_duration_minutes: int = 60

    # Data file paths
    risk_keywords_path: str = "app/data/risk_keywords.json"
    crisis_resources_path: str = "app/data/crisis_resources.json"

    # CORS
    frontend_url: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    """Return cached singleton Settings instance.

    Returns:
        Settings: Application configuration loaded from environment.
    """
    return Settings()
