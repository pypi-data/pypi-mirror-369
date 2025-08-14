"""Environment variable parser with key case conversion."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import dotenv_values
from pydantic import BaseModel, Field, validator


class EnvVariable(BaseModel):
    """Model for environment variable with validation."""

    key: str = Field(..., description="Environment variable key (converted to lowercase)")
    value: str = Field(..., description="Environment variable value")
    original_key: str = Field(..., description="Original key before conversion")
    line_number: int = Field(..., description="Line number in the file")

    @validator("key")
    def validate_key(cls, v: str) -> str:
        """Validate and convert key to lowercase."""
        if not v or not v.strip():
            raise ValueError("Environment variable key cannot be empty")
        
        # Convert to lowercase as per requirements
        return v.strip().lower()

    @validator("value")
    def validate_value(cls, v: str) -> str:
        """Validate value."""
        return v.strip()

    @property
    def was_converted(self) -> bool:
        """Check if the key was converted from uppercase to lowercase."""
        return self.original_key != self.key


class EnvParser:
    """Parser for environment files with key case conversion using python-dotenv."""

    def __init__(self, file_path: Path, encoding: str = "utf-8"):
        """Initialize parser with file path and encoding."""
        self.file_path = file_path
        self.encoding = encoding
        self._variables: List[EnvVariable] = []

    def parse(self) -> List[EnvVariable]:
        """Parse the environment file and return variables."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Environment file not found: {self.file_path}")

        self._variables = []
        
        # Store original environment to detect new variables
        original_env = set(os.environ.keys())
        
        # Use python-dotenv to load environment variables
        # This handles multi-line strings, comments, and other edge cases properly
        vaules = dotenv_values(self.file_path, encoding=self.encoding)
        
        # Get all environment variables that were loaded from the file
        for key, value in vaules.items():
            # Only include variables that were loaded from the file
            var = EnvVariable(
                key=key,
                value=value,
                original_key=key,
                line_number=0,  # python-dotenv doesn't provide line numbers
            )
            self._variables.append(var)


        return self._variables

    def get_variables_dict(self) -> Dict[str, str]:
        """Get variables as a dictionary with lowercase keys."""
        return {var.key: var.value for var in self._variables}

    def get_converted_variables(self) -> List[Tuple[str, str]]:
        """Get list of variables that were converted from uppercase to lowercase."""
        return [
            (var.original_key, var.key) 
            for var in self._variables 
            if var.was_converted
        ]

    def validate_variables(self) -> List[str]:
        """Validate all variables and return list of errors."""
        errors = []
        
        for var in self._variables:
            # Check for duplicate keys (after conversion)
            duplicates = [v for v in self._variables if v.key == var.key]
            if len(duplicates) > 1:
                error = f"Duplicate key '{var.key}' found at lines: {[v.line_number for v in duplicates]}"
                errors.append(error)
        
        return errors

    @property
    def variables(self) -> List[EnvVariable]:
        """Get parsed variables."""
        return self._variables.copy()

    @property
    def count(self) -> int:
        """Get number of parsed variables."""
        return len(self._variables)

    @property
    def converted_count(self) -> int:
        """Get number of variables that were converted from uppercase to lowercase."""
        return len([var for var in self._variables if var.was_converted])
