# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""RegistryConfig class."""

import configparser
from pathlib import Path
from typing import Dict


class RegistryConfig:
    """RegistryConfig class."""

    def __init__(self, config_path: Path = None):
        """Registry config init.

        Args:
            config_path (Path, optional): Path to configuration file. Defaults to "registry-mgmt.cfg".
        """
        if config_path is None:
            print("No config path provided, using default 'registry-mgmt.cfg'.")
            config_path = Path("registry-mgmt.cfg")
        self.config_path = config_path
        if not self.config_path.is_file():
            raise FileNotFoundError(f"File '{self.config_path.resolve().as_posix()}' does not exist.")

        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        self._validate_schema()

    def _validate_schema(self) -> None:
        """Validate registry config schema."""
        config_file_name = str(self.config_path)

        if not self.config.has_section("registry"):
            raise Exception(f'"registry" section not found in config file {config_file_name}')

        # Validate registry section
        if not self.config.has_option("registry", "registry_name"):
            raise Exception(f'Key "registry_name" not found under "registry" section in config file {config_file_name}')
        if not self.config.has_option("registry", "tenant_id"):
            raise Exception(f'Key "tenant_id" not found under "registry" section in config file {config_file_name}')
        if not self.config.has_option("registry", "subscription_id"):
            raise Exception(f'Key "subscription_id" not found under "registry" section in config file {config_file_name}')
        if not self.config.has_option("registry", "resource_group"):
            raise Exception(f'Key "resource_group" not found under "registry" section in config file {config_file_name}')

        # Validate that values are not empty
        required_settings = ["registry_name", "tenant_id", "subscription_id", "resource_group"]
        for setting in required_settings:
            if not self.config.get("registry", setting).strip():
                raise Exception(f'Value for "{setting}" is empty in "registry" section in config file {config_file_name}')

        # Validate storage_overrides section (optional, but if present, validate its contents)
        if self.config.has_section("storage_overrides"):
            allowed_storage_keys = {"storage_name", "container_name", "container_path"}
            actual_storage_keys = set(self.config.options("storage_overrides"))

            # Check for unexpected keys
            unexpected_keys = actual_storage_keys - allowed_storage_keys
            if unexpected_keys:
                raise Exception(f'Unexpected keys {sorted(unexpected_keys)} found in "storage_overrides" section in config file {config_file_name}. Only {sorted(allowed_storage_keys)} are allowed.')

            # Check for required keys
            if not self.config.has_option("storage_overrides", "storage_name"):
                raise Exception(f'Key "storage_name" not found under "storage_overrides" section in config file {config_file_name}')
            if not self.config.has_option("storage_overrides", "container_name"):
                raise Exception(f'Key "container_name" not found under "storage_overrides" section in config file {config_file_name}')
            if not self.config.has_option("storage_overrides", "container_path"):
                raise Exception(f'Key "container_path" not found under "storage_overrides" section in config file {config_file_name}')

            # Validate that storage values are not empty
            required_storage_settings = ["storage_name", "container_name", "container_path"]
            for setting in required_storage_settings:
                if not self.config.get("storage_overrides", setting).strip():
                    raise Exception(f'Value for "{setting}" is empty in "storage_overrides" section in config file {config_file_name}')

    @property
    def registry_name(self) -> str:
        """Get registry name from config."""
        return self.config.get("registry", "registry_name")

    @property
    def tenant_id(self) -> str:
        """Get tenant ID from config."""
        return self.config.get("registry", "tenant_id")

    @property
    def subscription_id(self) -> str:
        """Get subscription ID from config."""
        return self.config.get("registry", "subscription_id")

    @property
    def resource_group(self) -> str:
        """Get resource group from config."""
        return self.config.get("registry", "resource_group")

    @property
    def storage_config(self) -> Dict[str, str]:
        """Get storage configuration."""
        if self.config.has_section("storage_overrides"):
            return dict(self.config["storage_overrides"])
        return {}


def create_registry_config(registry_name: str, subscription_id: str, resource_group: str, tenant_id: str,
                           config_file_path: Path, storage_name: str = None, container_name: str = None,
                           container_path: str = None):
    """Create registry config.

    Args:
        registry_name (str): Registry name.
        subscription_id (str): Registry subscription id.
        resource_group (str): Registry resource group.
        tenant_id (str): Tenant ID.
        config_file_path (Path): Path to config file.
        storage_name (str, optional): Storage account name for storage overrides. Defaults to None.
        container_name (str, optional): Container name for storage overrides. Defaults to None.
        container_path (str, optional): Container path for storage overrides. Defaults to None.
    """
    print("Creating registry config...")

    registry_config = configparser.ConfigParser()
    registry_config.add_section("registry")
    registry_config.set("registry", "registry_name", registry_name)
    registry_config.set("registry", "subscription_id", subscription_id)
    registry_config.set("registry", "resource_group", resource_group)
    registry_config.set("registry", "tenant_id", tenant_id)

    # Add storage overrides if provided
    if storage_name and container_name and container_path:
        registry_config.add_section("storage_overrides")
        registry_config.set("storage_overrides", "storage_name", storage_name)
        registry_config.set("storage_overrides", "container_name", container_name)
        registry_config.set("storage_overrides", "container_path", container_path)

    # Write to path
    if config_file_path is None:
        print('No config file path provided, using default "registry-mgmt.cfg"')
        config_file_path = Path("registry-mgmt.cfg")
    with open(config_file_path, "w") as config_file:
        registry_config.write(config_file)

    config_abs_path = Path(config_file_path).resolve().as_posix()

    print(f"Wrote registry config file to {config_abs_path}")
