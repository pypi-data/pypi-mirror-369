# Env-to-Vault Project Task Breakdown

## Project Overview
A tool to convert environment variables from ENV files to HashiCorp Vault Secret Engine format, with automatic key case conversion (uppercase to lowercase) and robust configuration management using Pydantic.

## Phase 1: Project Setup

### 1.1 Project Structure
- [x] Create `src/` directory for source code
- [x] Create `tests/` directory for test files
- [x] Create `examples/` directory for usage examples

### 1.2 Configuration Files
- [x] Create `pyproject.toml` for Python project configuration with uv
- [x] Create `README.md` with project description and usage instructions
- [x] Create `.env.example` for environment variable examples
- [x] Set up uv for dependency management and virtual environment

## Phase 2: Core Functionality Development

### 2.1 Environment Variable Parsing
- [x] Implement `.env` file parser using python-dotenv
- [x] **CRITICAL: Implement uppercase to lowercase key conversion**
- [x] Handle different variable types (string, number, boolean)
- [x] Add validation for environment variable names

### 2.2 Vault Integration
- [x] Implement HashiCorp Vault client integration using hvac
- [x] **CRITICAL: Add support for Vault Secret Engine (KV v1/v2)**
- [x] Support Vault authentication (token-based)
- [x] Implement error handling for Vault operations

### 2.3 Data Transformation
- [x] Create mapping logic from env vars to Vault paths
- [x] **CRITICAL: Ensure all keys are converted to lowercase before storing**
- [x] Implement hierarchical secret organization in Secret Engine

### 2.4 CLI Interface
- [x] Create command-line interface using click or typer
- [x] Implement subcommands (convert, validate)
- [x] Add configuration file support (YAML/JSON)
- [x] Add verbose/debug logging options


## Phase 3: Configuration and Data Validation

### 3.1 Pydantic Configuration Management
- [x] **CRITICAL: Implement Pydantic models for configuration validation**
- [x] Create `Config` model for application settings
- [x] Create `VaultConfig` model for Vault connection settings
- [x] Create `EnvFileConfig` model for environment file settings
- [x] Implement configuration file loading and validation

### 3.2 Data Models and Validation
- [x] Create Pydantic models for environment variables
- [x] Implement validation for Vault paths and secret names
- [x] Create models for Vault responses and operations

## Phase 4: Testing

### 4.1 Unit Testing
- [x] Write unit tests for core parsing functions
- [x] Test Vault client integration
- [x] Test data transformation logic
- [x] Test CLI interface
- [x] **CRITICAL: Test uppercase to lowercase key conversion**
- [x] Test Pydantic configuration validation

### 4.2 Integration Testing
- [ ] Test with real Vault instance
- [ ] Test error scenarios and edge cases
- [ ] **CRITICAL: Test uppercase to lowercase key conversion**
- [ ] Test Pydantic configuration validation


## Success Criteria
- [ ] **CRITICAL: Successfully convert ENV file key-value pairs to Vault Secret Engine**
- [ ] **CRITICAL: Convert all uppercase keys to lowercase before storing in Vault**
- [ ] **CRITICAL: Use Pydantic for robust configuration validation**
- [ ] Support multiple input/output formats
- [ ] Maintain security best practices
- [ ] Provide comprehensive documentation
- [ ] Achieve good test coverage
- [ ] Support multiple platforms
- [ ] Have clear error handling and logging
