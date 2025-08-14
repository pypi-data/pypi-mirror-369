"""Test multi-line string parsing with python-dotenv."""

import tempfile
from pathlib import Path

import pytest

from env_to_vault.parser import EnvParser


class TestMultilineParser:
    """Test parser with multi-line strings."""

    def test_multiline_quoted_strings(self):
        """Test parsing multi-line quoted strings."""
        content = '''
APP_NAME=test-app

# Multi-line string with double quotes
MULTI_LINE_QUOTED="This is a multi-line
string with double quotes
that spans multiple lines"

# Multi-line string with single quotes
MULTI_LINE_SINGLE='This is another multi-line
string with single quotes
that also spans multiple lines'

DB_HOST=localhost
'''
        
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
        temp_file.write(content)
        temp_file.close()
        
        try:
            parser = EnvParser(Path(temp_file.name))
            variables = parser.parse()
            
            # Check that all variables were parsed
            assert len(variables) == 4
            
            # Check variable names (should be converted to lowercase)
            var_names = [var.key for var in variables]
            assert "app_name" in var_names
            assert "multi_line_quoted" in var_names
            assert "multi_line_single" in var_names
            assert "db_host" in var_names
            
            # Check multi-line quoted string
            multi_quoted = next(var for var in variables if var.key == "multi_line_quoted")
            expected_quoted = "This is a multi-line\nstring with double quotes\nthat spans multiple lines"
            assert multi_quoted.value == expected_quoted
            
            # Check multi-line single quoted string
            multi_single = next(var for var in variables if var.key == "multi_line_single")
            expected_single = "This is another multi-line\nstring with single quotes\nthat also spans multiple lines"
            assert multi_single.value == expected_single
            
        finally:
            Path(temp_file.name).unlink()

    def test_escaped_quotes(self):
        """Test parsing strings with escaped quotes."""
        content = '''
ESCAPED_QUOTES='This has "quotes" inside'
SIMPLE_VAR=simple_value
'''
        
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
        temp_file.write(content)
        temp_file.close()
        
        try:
            parser = EnvParser(Path(temp_file.name))
            variables = parser.parse()
            
            assert len(variables) == 2
            
            # Check escaped quotes
            escaped_var = next(var for var in variables if var.key == "escaped_quotes")
            assert escaped_var.value == 'This has "quotes" inside'
            
        finally:
            Path(temp_file.name).unlink()

    def test_comments_and_empty_lines(self):
        """Test parsing with comments and empty lines."""
        content = '''
# This is a comment

APP_NAME=test-app

# Another comment
DB_HOST=localhost

# Comment with # in it
API_KEY=secret-key
'''
        
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
        temp_file.write(content)
        temp_file.close()
        
        try:
            parser = EnvParser(Path(temp_file.name))
            variables = parser.parse()
            
            assert len(variables) == 3
            
            var_names = [var.key for var in variables]
            assert "app_name" in var_names
            assert "db_host" in var_names
            assert "api_key" in var_names
            
        finally:
            Path(temp_file.name).unlink()

    def test_variable_interpolation(self):
        """Test variable interpolation (if supported by python-dotenv)."""
        content = '''
BASE_URL=https://api.example.com
API_URL=${BASE_URL}/v1
VERSION=1.0.0
FULL_URL=${API_URL}?version=${VERSION}
'''
        
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
        temp_file.write(content)
        temp_file.close()
        
        try:
            parser = EnvParser(Path(temp_file.name))
            variables = parser.parse()
            
            # Should have all variables
            assert len(variables) == 4
            
            var_names = [var.key for var in variables]
            assert "base_url" in var_names
            assert "api_url" in var_names
            assert "version" in var_names
            assert "full_url" in var_names
            
        finally:
            Path(temp_file.name).unlink()

    def test_special_characters(self):
        """Test parsing with special characters."""
        content = '''
SPECIAL_CHARS="Line 1\nLine 2\tTabbed\nLine 3"
UNICODE_CHARS="Hello 世界 🌍"
'''
        
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False)
        temp_file.write(content)
        temp_file.close()
        
        try:
            parser = EnvParser(Path(temp_file.name))
            variables = parser.parse()
            
            assert len(variables) == 2
            
            # Check special chars
            special_var = next(var for var in variables if var.key == "special_chars")
            assert "Line 1" in special_var.value
            assert "Line 2" in special_var.value
            assert "Line 3" in special_var.value
            
            # Check unicode
            unicode_var = next(var for var in variables if var.key == "unicode_chars")
            assert "世界" in unicode_var.value
            assert "🌍" in unicode_var.value
            
        finally:
            Path(temp_file.name).unlink()
