"""Typed configuration loader.

@dataclass(frozen=True)rom a JSON file (default `config.json`) and overriding
values from environment variables using the FEDI_CLEANER_* prefix.

Example env: FEDI_CLEANER_ACCESS_TOKEN, FEDI_CLEANER_DRY_RUN
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, fields, MISSING
from typing import Optional
import os
import json


@dataclass(frozen=True)
class Settings:
    access_token: str
    api_base_url: str
    dry_run: bool = True
    clean_following: bool = True
    clean_followers: bool = True
    clean_mutuals: bool = False
    clean_lists: bool = True
    clean_blocks: bool = True
    clean_mutes: bool = True
    clean_dead_accounts: bool = True
    clean_inactive_accounts: bool = False
    clean_migrated_accounts: bool = False
    inactive_days: int = 30


def load_settings(path: Optional[str] = None) -> Settings:
    """Load settings from JSON file + environment overrides.

    Order of precedence: environment variables > JSON file > defaults.
    """
    path = path or os.getenv("FEDI_CLEANER_CONFIG", "config.json")

    # Load JSON config if it exists
    data: dict = {}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as exc:
            raise RuntimeError(f"Failed to read config file {path}: {exc}")

    def get_value(field_name: str, default_value):
        """Get value with environment override > JSON > default precedence."""
        # 1. Check environment variable first (FEDI_CLEANER_FIELD_NAME)
        env_key = f"FEDI_CLEANER_{field_name.upper()}"
        env_val = os.getenv(env_key)
        if env_val is not None:
            return _convert_type(env_val, default_value, env_key)

        # 2. Check JSON config (field_name in lowercase)
        json_val = data.get(field_name)
        if json_val is not None:
            return _convert_type(json_val, default_value)

        # 3. Use default value
        return default_value

    def _convert_type(value, default_value, source_name=None):
        """Convert string values to the appropriate type based on default_value."""
        if isinstance(default_value, bool):
            if isinstance(value, str):
                return value.strip().lower() in ("1", "true", "yes", "y", "on")
            return bool(value)

        if isinstance(default_value, int):
            try:
                return int(value)
            except (ValueError, TypeError):
                source = f" from {source_name}" if source_name else ""
                raise ValueError(f"Invalid integer value{source}: {value}")

        return str(value)

    # Build settings from dataclass fields
    field_values = {}
    for field in fields(Settings):
        # Handle required fields (those without defaults)
        if field.default is MISSING:
            default_val = ""  # Required fields get empty string default
        else:
            default_val = field.default
        field_values[field.name] = get_value(field.name, default_val)

    # Validate required fields
    if not field_values["access_token"]:
        raise ValueError(
            "access_token must be set via config.json or FEDI_CLEANER_ACCESS_TOKEN environment variable"
        )
    if not field_values["api_base_url"]:
        raise ValueError(
            "api_base_url must be set via config.json or FEDI_CLEANER_API_BASE_URL environment variable"
        )

    return Settings(**field_values)


def create_example_config(path: str = "config.json") -> None:
    """Create an example configuration file.

    Args:
        path: Path where to create the config file (default: config.json)
    """
    # Create a Settings instance with default values and empty required fields
    default_settings = Settings(access_token="", api_base_url="")

    # Convert to dict - field names are already lowercase
    example_config = {}
    for key, value in asdict(default_settings).items():
        example_config[key] = value

    if os.path.exists(path):
        response = input(f"Config file '{path}' already exists. Overwrite? (y/N): ")
        if response.lower() not in ("y", "yes"):
            print(f"Skipped creating config file at '{path}'")
            return

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(example_config, f, indent=2)
        print(f"Example config created at '{path}'")
        print("\nPlease edit the config file and set:")
        print("- access_token: Your Mastodon access token")
        print(
            "- api_base_url: Your Mastodon instance URL (e.g., https://mastodon.social)"
        )
        print("- Other settings as needed")
    except Exception as exc:
        raise RuntimeError(f"Failed to create config file {path}: {exc}")
