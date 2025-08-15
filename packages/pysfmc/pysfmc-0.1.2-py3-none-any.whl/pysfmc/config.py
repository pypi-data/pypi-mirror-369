"""Configuration management for SFMC client."""

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientConfig(BaseModel):
    """HTTP client configuration settings."""

    timeout: float = Field(30.0, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of retry attempts")
    retry_backoff_factor: float = Field(0.5, description="Backoff factor for retries")
    max_connections: int = Field(
        100, description="Maximum number of connections in pool"
    )
    max_keepalive_connections: int = Field(
        20, description="Maximum number of keep-alive connections"
    )


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""

    enabled: bool = Field(True, description="Enable rate limiting")
    requests_per_minute: int = Field(2500, description="Max requests per minute")
    burst_limit: int = Field(100, description="Burst request limit")


class SFMCConfig(BaseSettings):
    """Complete SFMC client configuration."""

    # HTTP client settings
    client: ClientConfig = Field(default_factory=ClientConfig)

    # Rate limiting settings
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)

    # Logging settings
    log_requests: bool = Field(False, description="Log HTTP requests")
    log_responses: bool = Field(False, description="Log HTTP responses")
    log_level: str = Field("INFO", description="Logging level")

    # Debug settings
    debug: bool = Field(False, description="Enable debug mode")

    model_config = SettingsConfigDict(
        env_prefix="SFMC_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",  # For nested config like SFMC_CLIENT__TIMEOUT
    )
