"""Tests for the Pydantic configuration models."""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from env_to_vault.config import Config, VaultConfig, EnvFileConfig


class TestVaultConfig:
    """Test VaultConfig model."""

    def test_vault_config_creation(self):
        """Test creating a VaultConfig."""
        config = VaultConfig(
            url="http://localhost:8200",
            token="test-token",
            secret_engine="secret",
            path_prefix="env",
        )
        
        assert str(config.url) == "http://localhost:8200/"
        assert config.token == "test-token"
        assert config.secret_engine == "secret"
        assert config.path_prefix == "env"

    def test_vault_config_defaults(self):
        """Test VaultConfig with default values."""
        config = VaultConfig(
            url="http://localhost:8200",
            token="test-token",
        )
        
        assert config.secret_engine == "secret"
        assert config.path_prefix == "env"

    def test_vault_config_validation(self):
        """Test VaultConfig validation."""
        # Test empty secret engine
        with pytest.raises(ValidationError):
            VaultConfig(
                url="http://localhost:8200",
                token="test-token",
                secret_engine="",
            )

        # Test whitespace secret engine
        with pytest.raises(ValidationError):
            VaultConfig(
                url="http://localhost:8200",
                token="test-token",
                secret_engine="   ",
            )

        # Test empty path prefix
        with pytest.raises(ValidationError):
            VaultConfig(
                url="http://localhost:8200",
                token="test-token",
                path_prefix="",
            )

        # Test whitespace path prefix
        with pytest.raises(ValidationError):
            VaultConfig(
                url="http://localhost:8200",
                token="test-token",
                path_prefix="   ",
            )

    def test_vault_config_trimming(self):
        """Test that whitespace is trimmed from string fields."""
        config = VaultConfig(
            url="http://localhost:8200",
            token="test-token",
            secret_engine="  secret  ",
            path_prefix="  env  ",
        )
        
        assert config.secret_engine == "secret"
        assert config.path_prefix == "env"


class TestEnvFileConfig:
    """Test EnvFileConfig model."""

    def create_temp_file(self) -> Path:
        """Create a temporary file for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        return Path(temp_file.name)

    def test_env_file_config_creation(self):
        """Test creating an EnvFileConfig."""
        temp_file = self.create_temp_file()
        
        try:
            config = EnvFileConfig(
                path=temp_file,
                encoding="utf-8",
            )
            
            assert config.path == temp_file
            assert config.encoding == "utf-8"
        finally:
            temp_file.unlink()

    def test_env_file_config_defaults(self):
        """Test EnvFileConfig with default encoding."""
        temp_file = self.create_temp_file()
        
        try:
            config = EnvFileConfig(path=temp_file)
            assert config.encoding == "utf-8"
        finally:
            temp_file.unlink()

    def test_env_file_config_validation(self):
        """Test EnvFileConfig validation."""
        # Test non-existent file
        with pytest.raises(ValidationError):
            EnvFileConfig(path=Path("/nonexistent/file.env"))

        # Test directory instead of file
        temp_dir = tempfile.mkdtemp()
        try:
            with pytest.raises(ValidationError):
                EnvFileConfig(path=Path(temp_dir))
        finally:
            import shutil
            shutil.rmtree(temp_dir)

        # Test invalid encoding
        temp_file = self.create_temp_file()
        try:
            with pytest.raises(ValidationError):
                EnvFileConfig(
                    path=temp_file,
                    encoding="invalid-encoding",
                )
        finally:
            temp_file.unlink()

    def test_env_file_config_encoding_case_insensitive(self):
        """Test that encoding is converted to lowercase."""
        temp_file = self.create_temp_file()
        
        try:
            config = EnvFileConfig(
                path=temp_file,
                encoding="UTF-8",
            )
            assert config.encoding == "utf-8"
        finally:
            temp_file.unlink()


class TestConfig:
    """Test Config model."""

    def create_temp_file(self) -> Path:
        """Create a temporary file for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        return Path(temp_file.name)

    def test_config_creation(self):
        """Test creating a Config."""
        temp_file = self.create_temp_file()
        
        try:
            vault_config = VaultConfig(
                url="http://localhost:8200",
                token="test-token",
            )
            
            env_file_config = EnvFileConfig(
                path=temp_file,
                encoding="utf-8",
            )
            
            config = Config(
                vault=vault_config,
                env_file=env_file_config,
                verbose=False,
                dry_run=False,
            )
            
            assert config.vault == vault_config
            assert config.env_file == env_file_config
            assert config.verbose is False
            assert config.dry_run is False
        finally:
            temp_file.unlink()

    def test_config_from_file(self):
        """Test loading Config from YAML file."""
        config_data = """
vault:
  url: "http://localhost:8200"
  token: "test-token"
  secret_engine: "secret"
  path_prefix: "env"

env_file:
  path: "test.env"
  encoding: "utf-8"

verbose: true
dry_run: false
"""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
        temp_file.write(config_data)
        temp_file.close()
        
        try:
            # Create the test.env file referenced in config
            test_env_file = Path("test.env")
            test_env_file.write_text("TEST=value")
            
            try:
                config = Config.from_file(Path(temp_file.name))
                
                assert str(config.vault.url) == "http://localhost:8200/"
                assert config.vault.token == "test-token"
                assert config.vault.secret_engine == "secret"
                assert config.vault.path_prefix == "env"
                assert config.env_file.path == Path("test.env")
                assert config.env_file.encoding == "utf-8"
                assert config.verbose is True
                assert config.dry_run is False
            finally:
                test_env_file.unlink()
        finally:
            Path(temp_file.name).unlink()

    def test_config_from_file_not_found(self):
        """Test loading Config from non-existent file."""
        with pytest.raises(FileNotFoundError):
            Config.from_file(Path("/nonexistent/config.yaml"))

    def test_config_from_env_vars(self, monkeypatch):
        """Test loading Config from environment variables."""
        # Set environment variables
        monkeypatch.setenv("VAULT_URL", "http://localhost:8200")
        monkeypatch.setenv("VAULT_TOKEN", "test-token")
        monkeypatch.setenv("VAULT_SECRET_ENGINE", "custom-secret")
        monkeypatch.setenv("VAULT_PATH_PREFIX", "custom-env")
        monkeypatch.setenv("ENV_FILE_PATH", "test.env")
        monkeypatch.setenv("ENV_FILE_ENCODING", "utf-8")
        
        # Create the test.env file
        test_env_file = Path("test.env")
        test_env_file.write_text("TEST=value")
        
        try:
            config = Config.from_env_vars()
            
            assert str(config.vault.url) == "http://localhost:8200/"
            assert config.vault.token == "test-token"
            assert config.vault.secret_engine == "custom-secret"
            assert config.vault.path_prefix == "custom-env"
            assert config.env_file.path == Path("test.env")
            assert config.env_file.encoding == "utf-8"
        finally:
            test_env_file.unlink()

    def test_config_from_env_vars_missing_required(self, monkeypatch):
        """Test loading Config from environment variables with missing required values."""
        # Only set some environment variables
        monkeypatch.setenv("VAULT_URL", "http://localhost:8200")
        # Missing VAULT_TOKEN
        
        with pytest.raises(ValueError, match="VAULT_URL and VAULT_TOKEN environment variables are required"):
            Config.from_env_vars()

    def test_config_from_env_vars_defaults(self, monkeypatch):
        """Test loading Config from environment variables with defaults."""
        # Set only required environment variables
        monkeypatch.setenv("VAULT_URL", "http://localhost:8200")
        monkeypatch.setenv("VAULT_TOKEN", "test-token")
        
        # Create the default .env file
        default_env_file = Path(".env")
        default_env_file.write_text("TEST=value")
        
        try:
            config = Config.from_env_vars()
            
            assert config.vault.secret_engine == "secret"  # default
            assert config.vault.path_prefix == "env"  # default
            assert config.env_file.path == Path(".env")  # default
            assert config.env_file.encoding == "utf-8"  # default
        finally:
            default_env_file.unlink()
