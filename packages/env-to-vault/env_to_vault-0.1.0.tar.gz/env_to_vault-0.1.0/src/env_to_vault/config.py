"""Configuration models using Pydantic for validation."""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class VaultConfig(BaseModel):
    """Configuration for Vault connection and settings."""

    url: HttpUrl = Field(..., description="Vault server URL")
    token: str = Field(..., description="Vault authentication token")
    secret_engine: str = Field(default="secret", description="Secret engine name")
    path_prefix: str = Field(default="env", description="Path prefix for secrets")

    @validator("secret_engine")
    def validate_secret_engine(cls, v: str) -> str:
        """Validate secret engine name."""
        if not v or not v.strip():
            raise ValueError("Secret engine name cannot be empty")
        return v.strip()

    @validator("path_prefix")
    def validate_path_prefix(cls, v: str) -> str:
        """Validate path prefix."""
        if not v or not v.strip():
            raise ValueError("Path prefix cannot be empty")
        return v.strip()


class EnvFileConfig(BaseModel):
    """Configuration for environment file settings."""

    path: Path = Field(..., description="Path to the ENV file")
    encoding: str = Field(default="utf-8", description="File encoding")

    @validator("path")
    def validate_path(cls, v: Path) -> Path:
        """Validate that the file exists."""
        if not v.exists():
            raise ValueError(f"ENV file does not exist: {v}")
        if not v.is_file():
            raise ValueError(f"Path is not a file: {v}")
        return v

    @validator("encoding")
    def validate_encoding(cls, v: str) -> str:
        """Validate encoding."""
        valid_encodings = ["utf-8", "utf-16", "ascii", "latin-1"]
        if v.lower() not in valid_encodings:
            raise ValueError(f"Unsupported encoding: {v}. Supported: {valid_encodings}")
        return v.lower()


class Config(BaseModel):
    """Main application configuration."""

    vault: VaultConfig = Field(..., description="Vault configuration")
    env_file: EnvFileConfig = Field(..., description="Environment file configuration")
    verbose: bool = Field(default=False, description="Enable verbose logging")
    dry_run: bool = Field(default=False, description="Dry run mode (no changes made)")

    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from YAML file."""
        import yaml

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        return cls(**config_data)

    @classmethod
    def from_env_vars(cls) -> "Config":
        """Load configuration from environment variables."""
        import os

        vault_url = os.getenv("VAULT_URL")
        vault_token = os.getenv("VAULT_TOKEN")
        vault_secret_engine = os.getenv("VAULT_SECRET_ENGINE", "secret")
        vault_path_prefix = os.getenv("VAULT_PATH_PREFIX", "env")
        env_file_path = os.getenv("ENV_FILE_PATH", ".env")
        env_file_encoding = os.getenv("ENV_FILE_ENCODING", "utf-8")

        if not vault_url or not vault_token:
            raise ValueError(
                "VAULT_URL and VAULT_TOKEN environment variables are required"
            )

        return cls(
            vault=VaultConfig(
                url=vault_url,
                token=vault_token,
                secret_engine=vault_secret_engine,
                path_prefix=vault_path_prefix,
            ),
            env_file=EnvFileConfig(
                path=Path(env_file_path),
                encoding=env_file_encoding,
            ),
        )
