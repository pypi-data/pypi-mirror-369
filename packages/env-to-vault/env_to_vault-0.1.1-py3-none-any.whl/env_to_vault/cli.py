"""Command-line interface for env-to-vault."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .config import Config
from .parser import EnvParser
from .vault import VaultClient


def setup_logging(verbose: bool) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """Convert environment variables from ENV files to HashiCorp Vault Secret Engine format."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    setup_logging(verbose)


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--env-file", "-e", type=click.Path(exists=True), help="Environment file path")
@click.option("--vault-url", help="Vault server URL")
@click.option("--vault-token", help="Vault authentication token")
@click.option("--vault-secret-engine", default="secret", help="Vault secret engine name")
@click.option("--vault-path-prefix", default="env", help="Path prefix for secrets")
@click.option("--dry-run", is_flag=True, help="Dry run mode (no changes made)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def convert(
    config: Optional[str],
    env_file: Optional[str],
    vault_url: Optional[str],
    vault_token: Optional[str],
    vault_secret_engine: str,
    vault_path_prefix: str,
    dry_run: bool,
    verbose: bool,
) -> None:
    """Convert environment variables from ENV file to Vault Secret Engine."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        if config:
            config_obj = Config.from_file(Path(config))
        elif vault_url and vault_token:
            # Create config from command line arguments
            from .config import VaultConfig, EnvFileConfig
            
            vault_config = VaultConfig(
                url=vault_url,
                token=vault_token,
                secret_engine=vault_secret_engine,
                path_prefix=vault_path_prefix,
            )
            
            env_file_config = EnvFileConfig(
                path=Path(env_file) if env_file else Path(".env"),
                encoding="utf-8",
            )
            
            config_obj = Config(
                vault=vault_config,
                env_file=env_file_config,
                dry_run=dry_run,
                verbose=verbose,
            )
        else:
            # Try to load from environment variables
            config_obj = Config.from_env_vars()
            config_obj.dry_run = dry_run
            config_obj.verbose = verbose

        logger.info("Configuration loaded successfully")

        # Parse environment file
        parser = EnvParser(config_obj.env_file.path, config_obj.env_file.encoding)
        variables = parser.parse()
        
        logger.info(f"Parsed {len(variables)} environment variables")
        
        # Check for converted variables
        converted = parser.get_converted_variables()
        if converted:
            logger.info(f"Converted {len(converted)} variables from uppercase to lowercase:")
            for original, converted_key in converted:
                logger.info(f"  {original} -> {converted_key}")

        # Validate variables
        errors = parser.validate_variables()
        if errors:
            logger.error("Validation errors found:")
            for error in errors:
                logger.error(f"  {error}")
            sys.exit(1)

        # Get variables as dictionary
        variables_dict = parser.get_variables_dict()
        
        if config_obj.dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
            logger.info("Variables that would be written to Vault:")
            for key, value in variables_dict.items():
                logger.info(f"  {key}: {value}")
            return

        # Initialize Vault client
        vault_client = VaultClient(config_obj.vault)
        logger.info("Connected to Vault successfully")

        # Write variables to Vault
        logger.info("Writing environment variables to Vault...")
        responses = vault_client.write_environment_variables(variables_dict)
        
        # Check results
        successful = sum(1 for r in responses if r.success)
        failed = len(responses) - successful
        
        logger.info(f"Conversion completed: {successful} successful, {failed} failed")
        
        if failed > 0:
            logger.error("Some variables failed to write to Vault")
            sys.exit(1)
        else:
            logger.info("All environment variables successfully written to Vault")

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--env-file", "-e", type=click.Path(exists=True), help="Environment file path")
@click.option("--vault-url", help="Vault server URL")
@click.option("--vault-token", help="Vault authentication token")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def validate(
    config: Optional[str],
    env_file: Optional[str],
    vault_url: Optional[str],
    vault_token: Optional[str],
    verbose: bool,
) -> None:
    """Validate configuration and environment file without making changes."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        if config:
            config_obj = Config.from_file(Path(config))
        elif vault_url and vault_token:
            # Create config from command line arguments
            from .config import VaultConfig, EnvFileConfig
            
            vault_config = VaultConfig(
                url=vault_url,
                token=vault_token,
                secret_engine="secret",
                path_prefix="env",
            )
            
            env_file_config = EnvFileConfig(
                path=Path(env_file) if env_file else Path(".env"),
                encoding="utf-8",
            )
            
            config_obj = Config(
                vault=vault_config,
                env_file=env_file_config,
                verbose=verbose,
            )
        else:
            # Try to load from environment variables
            config_obj = Config.from_env_vars()
            config_obj.verbose = verbose

        logger.info("✅ Configuration loaded successfully")

        # Validate environment file
        parser = EnvParser(config_obj.env_file.path, config_obj.env_file.encoding)
        variables = parser.parse()
        
        logger.info(f"✅ Environment file parsed successfully: {len(variables)} variables")

        # Check for converted variables
        converted = parser.get_converted_variables()
        if converted:
            logger.info(f"ℹ️  {len(converted)} variables will be converted from uppercase to lowercase:")
            for original, converted_key in converted:
                logger.info(f"    {original} -> {converted_key}")

        # Validate variables
        errors = parser.validate_variables()
        if errors:
            logger.error("❌ Validation errors found:")
            for error in errors:
                logger.error(f"    {error}")
            sys.exit(1)
        else:
            logger.info("✅ Environment variables validation passed")

        # Test Vault connection
        vault_client = VaultClient(config_obj.vault)
        if vault_client.test_connection():
            logger.info("✅ Vault connection successful")
        else:
            logger.error("❌ Vault connection failed")
            sys.exit(1)

        # Get secret engine info
        engine_info = vault_client.get_secret_engine_info()
        if engine_info:
            logger.info("✅ Secret engine configuration valid")
        else:
            logger.warning("⚠️  Could not retrieve secret engine information")

        logger.info("✅ All validations passed successfully")

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--vault-url", help="Vault server URL")
@click.option("--vault-token", help="Vault authentication token")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def list_secrets(
    config: Optional[str],
    vault_url: Optional[str],
    vault_token: Optional[str],
    verbose: bool,
) -> None:
    """List secrets in Vault Secret Engine."""
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        if config:
            config_obj = Config.from_file(Path(config))
        elif vault_url and vault_token:
            # Create config from command line arguments
            from .config import VaultConfig, EnvFileConfig
            
            vault_config = VaultConfig(
                url=vault_url,
                token=vault_token,
                secret_engine="secret",
                path_prefix="env",
            )
            
            env_file_config = EnvFileConfig(
                path=Path(".env"),
                encoding="utf-8",
            )
            
            config_obj = Config(
                vault=vault_config,
                env_file=env_file_config,
                verbose=verbose,
            )
        else:
            # Try to load from environment variables
            config_obj = Config.from_env_vars()
            config_obj.verbose = verbose

        # Initialize Vault client
        vault_client = VaultClient(config_obj.vault)
        
        # List secrets
        secrets = vault_client.list_secrets()
        
        if secrets:
            logger.info(f"Found {len(secrets)} secrets in Vault:")
            for secret in sorted(secrets):
                logger.info(f"  {secret}")
        else:
            logger.info("No secrets found in Vault")

    except Exception as e:
        logger.error(f"Failed to list secrets: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
