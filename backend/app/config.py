"""
config.py - Application configuration and settings.
"""

from pathlib import Path
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """WindScope configuration settings."""
    app_name: str = Field(
        default="WindScope — UK Wind Forecast Intelligence Platform",
        validation_alias=AliasChoices("WINDSCOPE_APP_NAME", "APP_NAME", "app_name")
    )
    api_prefix: str = "/api"
    data_dir: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent / "data",
        validation_alias=AliasChoices("WINDSCOPE_DATA_DIR", "DATA_DIR", "data_dir")
    )
    default_cutoff_hour: int = Field(
        default=9,
        validation_alias=AliasChoices("WINDSCOPE_DEFAULT_CUTOFF_HOUR", "WINDSCOPE_CUTOFF_HOUR", "CUTOFF_HOUR", "default_cutoff_hour")
    )
    default_cutoff_minute: int = Field(
        default=0,
        validation_alias=AliasChoices("WINDSCOPE_DEFAULT_CUTOFF_MINUTE", "WINDSCOPE_CUTOFF_MINUTE", "CUTOFF_MINUTE", "default_cutoff_minute")
    )
    default_timezone: str = Field(
        default="Europe/London",
        validation_alias=AliasChoices("WINDSCOPE_DEFAULT_TIMEZONE", "WINDSCOPE_CUTOFF_TIMEZONE", "CUTOFF_TIMEZONE", "default_timezone")
    )
    cors_origins: list[str] = Field(
        default=["*"],
        validation_alias=AliasChoices("WINDSCOPE_CORS_ORIGINS", "CORS_ORIGINS", "cors_origins")
    )

    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()
