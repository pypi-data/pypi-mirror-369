"""Tests for the ENV parser with key case conversion."""

import tempfile
from pathlib import Path

import pytest

from env_to_vault.parser import EnvParser, EnvVariable


class TestEnvVariable:
    """Test EnvVariable model."""

    def test_env_variable_creation(self):
        """Test creating an EnvVariable."""
        var = EnvVariable(
            key="TEST_KEY",
            value="test_value",
            original_key="TEST_KEY",
            line_number=1,
        )
        
        assert var.key == "test_key"  # Should be converted to lowercase
        assert var.value == "test_value"
        assert var.original_key == "TEST_KEY"
        assert var.line_number == 1
        assert var.was_converted is True

    def test_env_variable_lowercase_key(self):
        """Test EnvVariable with already lowercase key."""
        var = EnvVariable(
            key="test_key",
            value="test_value",
            original_key="test_key",
            line_number=1,
        )
        
        assert var.key == "test_key"
        assert var.was_converted is False

    def test_env_variable_validation(self):
        """Test EnvVariable validation."""
        # Test empty key
        with pytest.raises(ValueError, match="Environment variable key cannot be empty"):
            EnvVariable(
                key="",
                value="test_value",
                original_key="",
                line_number=1,
            )

        # Test whitespace key
        with pytest.raises(ValueError, match="Environment variable key cannot be empty"):
            EnvVariable(
                key="   ",
                value="test_value",
                original_key="   ",
                line_number=1,
            )


class TestEnvParser:
    """Test EnvParser functionality."""

    def create_temp_env_file(self, content: str) -> Path:
        """Create a temporary ENV file for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
        temp_file.write(content)
        temp_file.close()
        return Path(temp_file.name)

    def test_parse_basic_env_file(self):
        """Test parsing a basic ENV file."""
        content = """
APP_NAME=my-app
DB_HOST=localhost
API_KEY=secret-key
"""
        env_file = self.create_temp_env_file(content)
        
        try:
            parser = EnvParser(env_file)
            variables = parser.parse()
            
            assert len(variables) == 3
            assert variables[0].key == "app_name"
            assert variables[0].value == "my-app"
            assert variables[0].original_key == "APP_NAME"
            assert variables[0].was_converted is True
            
            assert variables[1].key == "db_host"
            assert variables[1].value == "localhost"
            assert variables[1].original_key == "DB_HOST"
            
            assert variables[2].key == "api_key"
            assert variables[2].value == "secret-key"
            assert variables[2].original_key == "API_KEY"
        finally:
            env_file.unlink()

    def test_parse_with_comments_and_empty_lines(self):
        """Test parsing ENV file with comments and empty lines."""
        content = """
# This is a comment

APP_NAME=my-app
# Another comment
DB_HOST=localhost

API_KEY=secret-key
"""
        env_file = self.create_temp_env_file(content)
        
        try:
            parser = EnvParser(env_file)
            variables = parser.parse()
            
            assert len(variables) == 3
            assert variables[0].key == "app_name"
            assert variables[1].key == "db_host"
            assert variables[2].key == "api_key"
        finally:
            env_file.unlink()

    def test_parse_quoted_values(self):
        """Test parsing ENV file with quoted values."""
        content = """
APP_NAME="my-app"
DB_HOST='localhost'
API_KEY="secret-key"
"""
        env_file = self.create_temp_env_file(content)
        
        try:
            parser = EnvParser(env_file)
            variables = parser.parse()
            
            assert len(variables) == 3
            assert variables[0].value == "my-app"
            assert variables[1].value == "localhost"
            assert variables[2].value == "secret-key"
        finally:
            env_file.unlink()

    def test_parse_mixed_case_variables(self):
        """Test parsing ENV file with mixed case variables."""
        content = """
UPPERCASE_VAR=value1
lowercase_var=value2
MixedCase_Var=value3
"""
        env_file = self.create_temp_env_file(content)
        
        try:
            parser = EnvParser(env_file)
            variables = parser.parse()
            
            assert len(variables) == 3
            
            # Check conversion tracking
            converted = parser.get_converted_variables()
            assert len(converted) == 2  # UPPERCASE_VAR and MixedCase_Var
            
            # Check all keys are lowercase
            for var in variables:
                assert var.key == var.key.lower()
        finally:
            env_file.unlink()

    def test_get_variables_dict(self):
        """Test getting variables as dictionary."""
        content = """
APP_NAME=my-app
DB_HOST=localhost
API_KEY=secret-key
"""
        env_file = self.create_temp_env_file(content)
        
        try:
            parser = EnvParser(env_file)
            parser.parse()
            variables_dict = parser.get_variables_dict()
            
            expected = {
                "app_name": "my-app",
                "db_host": "localhost",
                "api_key": "secret-key",
            }
            assert variables_dict == expected
        finally:
            env_file.unlink()

    def test_validate_variables_duplicate_keys(self):
        """Test validation with duplicate keys (after conversion)."""
        content = """
APP_NAME=value1
app_name=value2
"""
        env_file = self.create_temp_env_file(content)
        
        try:
            parser = EnvParser(env_file)
            parser.parse()
            errors = parser.validate_variables()
            
            assert "Duplicate key 'app_name'" in errors[0]
        finally:
            env_file.unlink()

    def test_parse_nonexistent_file(self):
        """Test parsing a non-existent file."""
        parser = EnvParser(Path("/nonexistent/file.env"))
        
        with pytest.raises(FileNotFoundError):
            parser.parse()

    def test_parser_properties(self):
        """Test parser properties."""
        content = """
APP_NAME=my-app
DB_HOST=localhost
"""
        env_file = self.create_temp_env_file(content)
        
        try:
            parser = EnvParser(env_file)
            parser.parse()
            
            assert parser.count == 2
            assert parser.converted_count == 2
            assert len(parser.variables) == 2
        finally:
            env_file.unlink()
