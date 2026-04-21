"""Application settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    host: str = Field(default="db", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="workmate_db", description="Database name")
    user: str = Field(default="workmate", description="Database user")
    password: str = Field(default="workmate123", description="Database password")
    database_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "database_url"),
        description="Full database URL override",
    )

    @property
    def url(self) -> str:
        """Get database URL."""
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """Redis configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    db: int = Field(default=0, description="Redis database number")
    password: str | None = Field(default=None, description="Redis password")

    @property
    def url(self) -> str:
        """Get Redis URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class SMTPSettings(BaseSettings):
    """SMTP configuration."""

    model_config = SettingsConfigDict(
        env_prefix="SMTP_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )
    host: str = Field(default="localhost", description="SMTP host")
    port: int = Field(default=1025, description="SMTP port")
    user: str | None = Field(default=None, description="SMTP user")
    password: str | None = Field(default=None, description="SMTP password")
    sender_email: str = Field(default="noreply@workmate.local", description="From email address")
    sender_name: str = Field(default="Workmate", description="From display name")
    use_tls: bool = Field(default=False, description="Use implicit TLS")
    use_starttls: bool = Field(default=False, description="Upgrade plain SMTP with STARTTLS")
    timeout_seconds: float = Field(default=10.0, description="SMTP connection timeout in seconds")

    @property
    def url(self) -> str:
        """Get SMTP URL."""
        auth = f"{self.user}:{self.password}@" if self.user and self.password else ""
        return f"smtp://{auth}{self.host}:{self.port}"


class APISettings(BaseSettings):
    """API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    title: str = Field(default="Workmate API", description="API title")
    description: str = Field(default="Workmate API", description="API description")
    version: str = Field(default="0.1.0", description="API version")
    docs_url: str = Field(default="/docs", description="API docs URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")


class CloudinarySettings(BaseSettings):
    """Cloudinary configuration."""

    model_config = SettingsConfigDict(
        env_prefix="CLOUDINARY_",
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    cloud_name: str = Field(default="", description="Cloudinary cloud name")
    api_key: str = Field(default="", description="Cloudinary API key")
    api_secret: str = Field(default="", description="Cloudinary API secret")
    secure: bool = Field(default=True, description="Use HTTPS")
    
    def is_configured(self) -> bool:
        """Check if Cloudinary is configured."""
        return bool(self.cloud_name and self.api_key and self.api_secret)


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")
    secret_key: str = Field(default="", description="JWT secret key")
    frontend_url: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("FRONTEND_URL", "frontend_url"),
        description="Frontend base URL for app links",
    )

    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    api: APISettings = Field(default_factory=APISettings)
    smtp: SMTPSettings = Field(default_factory=SMTPSettings)
    cloudinary: CloudinarySettings = Field(default_factory=CloudinarySettings)  

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() in ("development", "dev", "local")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() in ("production", "prod")

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug(cls, value: object) -> bool | object:
        """Accept legacy shell values like DEBUG=release."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod", "false", "0", "off", "no"}:
                return False
            if normalized in {"debug", "development", "dev", "true", "1", "on", "yes"}:
                return True
        return value


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
