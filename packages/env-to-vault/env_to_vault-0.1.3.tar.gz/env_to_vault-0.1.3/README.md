# Env-to-Vault

A tool to convert environment variables from ENV files to HashiCorp Vault Secret Engine format, with automatic key case conversion (uppercase to lowercase) and robust configuration management using Pydantic.

## Features

- 🔄 Convert ENV files to Vault Secret Engine format
- 🔤 Automatic uppercase to lowercase key conversion
- ⚙️ Robust configuration management with Pydantic
- 🔐 Secure Vault integration with multiple authentication methods
- 🛠️ Command-line interface with validation and dry-run modes

## Installation

### Prerequisites

- Python 3.8+
- HashiCorp Vault server/cloud
- uv (recommended) or pip

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd env-to-vault

# Install dependencies
uv sync

# Install the package in development mode
uv pip install -e .
```

### Using pip

```bash
pip install env-to-vault
```

## Quick Start

1. **Create a configuration file** (`config.yaml`):

```yaml
vault:
  url: "http://localhost:8200"
  token: "your-vault-token"
  secret_engine: "secret"
  path_prefix: "env"

env_file:
  path: ".env"
  encoding: "utf-8"
```

2. **Run the conversion**:

```bash
env-to-vault convert --config config.yaml
```

## Configuration

### Vault Configuration

- `url`: Vault server URL
- `token`: Vault authentication token
- `secret_engine`: Secret engine name (default: "secret")
- `path_prefix`: Path prefix for secrets in Vault

### Environment File Configuration

- `path`: Path to the ENV file
- `encoding`: File encoding (default: "utf-8")

## Usage Examples

### Basic Conversion

```bash
# Convert .env file to Vault
env-to-vault convert --env-file .env --vault-url http://localhost:8200 --vault-token your-token
```

### Using Configuration File

```bash
# Use configuration file
env-to-vault convert --config config.yaml
```

### Validation Mode

```bash
# Validate configuration without making changes
env-to-vault validate --config config.yaml
```

### Verbose Output

```bash
# Show detailed output
env-to-vault convert --config config.yaml --verbose
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Run linting
uv run black src tests
uv run flake8 src tests

# Run type checking
uv run mypy src
```

### Project Structure

```
env-to-vault/
├── src/
│   └── env_to_vault/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── parser.py
│       └── vault.py
├── tests/
├── examples/
├── pyproject.toml
└── README.md
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
