"""Environment variable parser with key case conversion."""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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
    """Parser for environment files with key case conversion."""

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
        
        with open(self.file_path, "r", encoding=self.encoding) as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                
                # Parse variable
                var = self._parse_line(line, line_number)
                if var:
                    self._variables.append(var)

        return self._variables

    def _parse_line(self, line: str, line_number: int) -> Optional[EnvVariable]:
        """Parse a single line and return EnvVariable if valid."""
        # Match key=value pattern
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
        if not match:
            return None

        original_key, value = match.groups()
        
        # Handle quoted values
        value = self._unquote_value(value)
        
        try:
            return EnvVariable(
                key=original_key,
                value=value,
                original_key=original_key,
                line_number=line_number,
            )
        except ValueError as e:
            # Log warning for invalid variables but continue parsing
            print(f"Warning: Invalid variable at line {line_number}: {e}")
            return None

    def _unquote_value(self, value: str) -> str:
        """Remove quotes from value if present."""
        value = value.strip()
        
        # Handle single quotes
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        
        # Handle double quotes
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        
        return value

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
