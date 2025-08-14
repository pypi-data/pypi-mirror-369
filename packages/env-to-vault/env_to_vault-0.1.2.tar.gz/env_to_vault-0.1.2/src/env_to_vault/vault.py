"""Vault client for Secret Engine integration."""

import logging
from typing import Dict, List, Optional

import hvac
from pydantic import BaseModel, Field

from .config import VaultConfig

logger = logging.getLogger(__name__)


class VaultSecret(BaseModel):
    """Model for Vault secret data."""

    path: str = Field(..., description="Secret path in Vault")
    data: Dict[str, str] = Field(..., description="Secret data")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="Secret metadata")


class VaultResponse(BaseModel):
    """Model for Vault operation response."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict] = Field(default=None, description="Response data")


class VaultClient:
    """Client for HashiCorp Vault Secret Engine operations."""

    def __init__(self, config: VaultConfig):
        """Initialize Vault client with configuration."""
        self.config = config
        self.client = hvac.Client(
            url=str(config.url),
            token=config.token,
        )
        self._validate_connection()

    def _validate_connection(self) -> None:
        """Validate Vault connection and authentication."""
        try:
            if not self.client.is_authenticated():
                raise ValueError("Failed to authenticate with Vault")
            
            # Test connection by reading sys/health
            health = self.client.sys.read_health_status()
            if not health:
                raise ValueError("Failed to connect to Vault")
                
            logger.info("Successfully connected to Vault")
            
        except Exception as e:
            raise ValueError(f"Vault connection failed: {e}")

    def write_secret(self, path: str, data: Dict[str, str], metadata: Optional[Dict[str, str]] = None) -> VaultResponse:
        """Write secret to Vault Secret Engine."""
        try:
            # Path should be: {path_prefix}/{path} under the secret engine
            full_path = f"{self.config.path_prefix}/{path}"
            
            # Write to Vault
            response = self.client.secrets.kv.v2.create_or_update_secret(
                path=full_path,
                secret=data,
                mount_point=self.config.secret_engine,
            )
            
            if response and response.get("data", {}).get("version"):
                logger.info(f"Successfully wrote secret to {full_path}")
                return VaultResponse(
                    success=True,
                    message=f"Secret written to {full_path}",
                    data=response,
                )
            else:
                raise ValueError("Unexpected response from Vault")
                
        except Exception as e:
            logger.error(f"Failed to write secret to {path}: {e}")
            return VaultResponse(
                success=False,
                message=f"Failed to write secret: {e}",
            )

    def read_secret(self, path: str) -> Optional[Dict[str, str]]:
        """Read secret from Vault Secret Engine."""
        try:
            full_path = f"{self.config.path_prefix}/{path}"
            
            response = self.client.secrets.kv.v2.read_secret_version(
                path=full_path,
                mount_point=self.config.secret_engine,
            )
            
            if response and "data" in response:
                return response["data"]["data"]
            else:
                logger.warning(f"Secret not found at {full_path}")
                return None
                
        except hvac.exceptions.InvalidPath:
            logger.warning(f"Secret not found at {path}")
            return None
        except Exception as e:
            logger.error(f"Failed to read secret from {path}: {e}")
            return None

    def delete_secret(self, path: str) -> VaultResponse:
        """Delete secret from Vault Secret Engine."""
        try:
            full_path = f"{self.config.path_prefix}/{path}"
            
            response = self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=full_path,
                mount_point=self.config.secret_engine,
            )
            
            logger.info(f"Successfully deleted secret from {full_path}")
            return VaultResponse(
                success=True,
                message=f"Secret deleted from {full_path}",
                data=response,
            )
            
        except Exception as e:
            logger.error(f"Failed to delete secret from {path}: {e}")
            return VaultResponse(
                success=False,
                message=f"Failed to delete secret: {e}",
            )

    def list_secrets(self, path: str = "") -> List[str]:
        """List secrets in Vault Secret Engine."""
        try:
            full_path = f"{self.config.path_prefix}/{path}"
            
            response = self.client.secrets.kv.v2.list_secrets(
                path=full_path,
                mount_point=self.config.secret_engine,
            )
            
            if response and "data" in response:
                return response["data"]["keys"]
            else:
                return []
                
        except hvac.exceptions.InvalidPath:
            return []
        except Exception as e:
            logger.error(f"Failed to list secrets: {e}")
            return []

    def write_environment_variables(self, variables: Dict[str, str], metadata: Optional[Dict[str, str]] = None) -> VaultResponse:
        """Write all environment variables as a single secret to Vault."""
        try:
            # Add metadata about the environment file
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "type": "environment_variables",
                "count": str(len(variables)),
                "source": "env-to-vault",
            })
            
            # Write all variables as a single secret
            response = self.write_secret(
                path="environment",
                data=variables,
                metadata=metadata,
            )
            
            if response.success:
                logger.info(f"Successfully wrote {len(variables)} environment variables to Vault")
            else:
                logger.error("Failed to write environment variables to Vault")
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to write environment variables: {e}")
            return VaultResponse(
                success=False,
                message=f"Failed to write environment variables: {e}",
            )

    def write_environment_file(self, variables: Dict[str, str], file_name: str = "env") -> VaultResponse:
        """Write all environment variables as a single secret file."""
        try:
            # Add file metadata
            metadata = {
                "source_file": file_name,
                "type": "environment_variables",
                "count": str(len(variables)),
            }
            
            return self.write_secret(
                path=file_name,
                data=variables,
                metadata=metadata,
            )
            
        except Exception as e:
            logger.error(f"Failed to write environment file: {e}")
            return VaultResponse(
                success=False,
                message=f"Failed to write environment file: {e}",
            )

    def test_connection(self) -> bool:
        """Test Vault connection and authentication."""
        try:
            return self.client.is_authenticated()
        except Exception:
            return False

    def get_secret_engine_info(self) -> Optional[Dict]:
        """Get information about the configured secret engine."""
        try:
            response = self.client.sys.read_mount_configuration(
                path=self.config.secret_engine,
            )
            return response
        except Exception as e:
            logger.error(f"Failed to get secret engine info: {e}")
            return None
