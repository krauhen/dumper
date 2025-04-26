"""Settings configuration for the dumper tool.

This module manages configuration settings using environment variables.
Primarily focused on settings necessary for interacting with OpenAI services.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the dumper application."""

    model_config = SettingsConfigDict(env_file=(".env",), env_file_encoding="utf-8")
    openai_api_key: str = Field(description="OpenAI API key")


def get_settings() -> Settings:
    """Retrieve settings for the application.

    Returns:
        Settings: An instance of the Settings object.
    """
    return Settings()
