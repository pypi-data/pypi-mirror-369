# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Asset management commands for registry-mgmt CLI."""

import sys
import shutil
import tempfile
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

from azureml.registry.data.validate_model_schema import validate_model_schema
from azureml.registry.data.validate_model_variant_schema import validate_model_variant_schema
from azureml.registry.mgmt.registry_config import RegistryConfig

# Windows compatibility patch - must be applied before importing azureml.assets
from subprocess import run


def patched_run_command(cmd: List[str]):
    """Run command with shell=True for Windows compatibility."""
    result = run(cmd, capture_output=True, encoding=sys.stdout.encoding, errors="ignore", shell=True)
    return result


# Apply patch before importing azureml.assets
import azureml.assets.publish_utils as publish_utils  # noqa: E402
publish_utils.run_command = patched_run_command

import azureml.assets as assets  # noqa: E402
import azureml.assets.util as util  # noqa: E402
from azureml.assets.config import AssetConfig, AssetType, AzureBlobstoreAssetPath  # noqa: E402
from azureml.assets.publish_utils import create_asset  # noqa: E402
from azureml.assets.validate_assets import validate_assets  # noqa: E402


def validate_model(asset_path: Path, allow_additional_properties: bool = False) -> bool:
    """Validate model.

    Args:
        asset_path (Path): Path to the asset folder to validate
        allow_additional_properties (bool): Whether to allow additional properties not defined in schema

    Returns:
        bool: True if validation passes, False otherwise
    """
    errors = 0

    print("⚙️ [VALIDATION #1]: Validate assets...")
    if not validate_assets(asset_path, assets.DEFAULT_ASSET_FILENAME):
        print("❌ [FAILED] Validation #1: validate_assets\n\n")
        errors += 1
    else:
        print("✅ [PASSED] Validation #1: validate_assets passed\n")

    # Model variant schema validation
    model_variant_schema_file = Path(__file__).parent.parent / "data" / "model-variant.schema.json"

    print("⚙️ [VALIDATION #2]: Validating model variant schema...")
    if not validate_model_variant_schema(input_dirs=[asset_path], model_variant_schema_file=model_variant_schema_file,
                                         asset_config_filename=assets.DEFAULT_ASSET_FILENAME):
        print("❌ [FAILED] Validation #2: validate_model_variant_schema\n")
        errors += 1
    else:
        print("✅ [PASSED] Validation #2: validate_model_variant_schema passed\n")

    # Model schema validation
    model_schema_file = Path(__file__).parent.parent / "data" / "model.schema.json"

    print("⚙️ [VALIDATION #3]: Validating model schema...")
    if not validate_model_schema(input_dirs=[asset_path], schema_file=model_schema_file,
                                 asset_config_filename=assets.DEFAULT_ASSET_FILENAME,
                                 allow_additional_properties=allow_additional_properties):
        print("❌ [FAILED] Validation #3: validate_model_schema\n")
        errors += 1
    else:
        print("✅ [PASSED] Validation #3: validate_model_schema passed\n")

    if errors != 0:
        return False

    print("🎉 [VALIDATION COMPLETE] All validations passed!\n")
    return True


def set_storage_and_sas(asset: AssetConfig, storage_config: dict):
    """Use storage configuration and generate/set SAS token.

    Args:
        asset (AssetConfig): Asset configuration object to modify
        storage_config (dict): Storage configuration dictionary
    """
    if not storage_config:
        # No storage overrides provided, skip storage configuration
        return

    print("Overriding storage configuration with provided values...")
    extra_config = asset.extra_config_as_object()
    extra_config._path = AzureBlobstoreAssetPath(
        storage_name=storage_config["storage_name"],
        container_name=storage_config["container_name"],
        container_path=storage_config["container_path"]
    )
    _ = extra_config.path.get_uri(token_expiration=timedelta(hours=1))


def build_mutable_asset(base_asset: AssetConfig, mutable_asset_dir: str, storage_overrides_exist: bool = False) -> AssetConfig:
    """Build a mutable copy of the asset in a temporary directory.

    Args:
        base_asset (AssetConfig): Base asset configuration to copy
        mutable_asset_dir (str): Directory path for the mutable asset copy
        storage_overrides_exist (bool, optional): If True, model config will be modified to set type to custom_model.

    Returns:
        AssetConfig: Mutable asset configuration object
    """
    common_dir, _ = util.find_common_directory(base_asset.release_paths)

    # Convert string paths to Path objects and ensure they're absolute
    common_dir = Path(common_dir).resolve()
    mutable_asset_dir = Path(mutable_asset_dir).resolve()
    base_asset_file = base_asset.file_name_with_path.resolve()
    base_spec_file = base_asset.spec_with_path.resolve()
    base_model_file = base_asset.extra_config_with_path.resolve()

    shutil.copytree(common_dir, mutable_asset_dir, dirs_exist_ok=True)

    # Reference asset files in mutable directory
    asset_config_file = mutable_asset_dir / base_asset_file.relative_to(common_dir)
    spec_config_file = mutable_asset_dir / base_spec_file.relative_to(common_dir)
    model_config_file = mutable_asset_dir / base_model_file.relative_to(common_dir)

    # Autoincrement version for mutable asset
    with open(spec_config_file, "r") as f:
        spec_config = yaml.safe_load(f)
        spec_config["version"] = datetime.now().strftime("%Y%m%d%H%M%S")

    with open(spec_config_file, "w") as f:
        yaml.dump(spec_config, f)

    # If storage overrides are provided, default set model type to custom_model
    if storage_overrides_exist:
        print("Storage overrides provided, default setting model type to custom_model")
        with open(model_config_file, "r") as f:
            model_config = yaml.safe_load(f)
            model_config["publish"]["type"] = "custom_model"

        with open(model_config_file, "w") as f:
            yaml.dump(model_config, f)

    mutable_asset = AssetConfig(asset_config_file)

    return mutable_asset


def create_or_update_asset(readonly_asset: AssetConfig, config: RegistryConfig):
    """Create or update an asset in the AzureML registry.

    Args:
        readonly_asset (AssetConfig): Asset configuration to create or update
        config (RegistryConfig): Registry configuration settings
    """
    print("[CREATING/UPDATING ASSET]")
    print(f"Using registry configuration from: {config.config_path}")
    # Create ML client
    ml_client = MLClient(
        subscription_id=config.subscription_id,
        resource_group_name=config.resource_group,
        registry_name=config.registry_name,
        credential=DefaultAzureCredential(),
    )

    with tempfile.TemporaryDirectory() as mutable_asset_dir:
        mutable_asset = build_mutable_asset(base_asset=readonly_asset, mutable_asset_dir=mutable_asset_dir, storage_overrides_exist=bool(config.storage_config))
        # autoincrement version
        try:
            set_storage_and_sas(mutable_asset, config.storage_config)
            success = create_asset(mutable_asset, config.registry_name, ml_client)
        except Exception as e:
            print(f"Failed to create/update asset: {e}")
            raise

        if not success:
            print(f"Failed to create/update asset: create_asset 'success' returned {success}")
            raise

        print("\n[VALIDATE YOUR ASSET IN THE UI HERE]")
        print(f" - Model Catalog link: https://ai.azure.com/explore/models/{mutable_asset.name}/version/{mutable_asset.version}/registry/{config.registry_name}?tid={config.tenant_id}")
        print(f" - Azure Portal link: https://ml.azure.com/registries/{config.registry_name}/models/{mutable_asset.name}/version/{mutable_asset.version}?tid={config.tenant_id}")


def asset_validate(asset_path: Path, dry_run: bool = False, allow_additional_properties: bool = False) -> bool:
    """Validate an asset at the specified path.

    Args:
        asset_path (Path): Path to the asset folder to validate
        dry_run (bool): If True, perform a dry run without side effects
        allow_additional_properties (bool): Whether to allow additional properties not defined in schema

    Returns:
        bool: True if validation passes, False otherwise
    """
    if dry_run:
        print(f"[DRY RUN] Would validate asset at: {asset_path}")
        return True

    asset_path = asset_path.resolve()
    print(f"[VALIDATION] Begin validating for asset at: {asset_path}...")

    # Check if asset path exists
    if not asset_path.exists():
        print(f"❌ [ERROR]: Asset path {asset_path} does not exist")
        return False

    # Check for exactly one asset
    asset_count = len(util.find_assets([asset_path], assets.DEFAULT_ASSET_FILENAME))
    if asset_count != 1:
        print(f"❌ [ERROR]: Expected exactly one asset in {asset_path}, found {asset_count}")
        return False

    # Load asset configuration
    readonly_asset = assets.AssetConfig(asset_path / assets.DEFAULT_ASSET_FILENAME)

    # Check asset type
    if readonly_asset.type != AssetType.MODEL:
        print(f"❌ [ERROR]: Asset type {readonly_asset.type} is not supported for validation. "
              f"Only models are currently supported.")
        return False

    # Perform validation
    return validate_model(readonly_asset.file_path, allow_additional_properties)


def asset_deploy(asset_path: Path, config_path: Path, dry_run: bool = False) -> bool:
    """Deploy an asset using configuration file.

    Args:
        asset_path (Path): Path to the asset folder to deploy
        config_path (Path): Path to configuration file
        dry_run (bool): If True, perform a dry run without deploying

    Returns:
        bool: True if deployment succeeds, False otherwise
    """
    try:
        config = RegistryConfig(config_path)
    except Exception as e:
        print(f"❌ [ERROR]: Configuration validation failed: {e}")
        return False

    if dry_run:
        print(f"[DRY RUN] Would deploy asset at {asset_path} to registry {config.registry_name}")
        return True

    asset_path = asset_path.resolve()

    # Validate asset before deployment
    if not asset_validate(asset_path, dry_run=False):
        print("❌ [ERROR]: Asset validation failed. Asset deployment aborted.")
        return False

    # Load asset configuration
    readonly_asset = assets.AssetConfig(asset_path / assets.DEFAULT_ASSET_FILENAME)

    try:
        create_or_update_asset(readonly_asset, config)
        return True
    except Exception as e:
        print(f"❌ [ERROR]: Failed to deploy asset: {e}")
        return False
