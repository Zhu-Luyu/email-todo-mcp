# src/config.py
import json
from pathlib import Path

REQUIRED_FIELDS = ["imap_server", "imap_port", "email", "password"]


class ConfigError(Exception):
    """Configuration error."""
    pass


def load_config(config_path: str | None = None) -> dict:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to config file. If None, looks for config.json in project root.

    Returns:
        Configuration dictionary.

    Raises:
        ConfigError: If config file is missing, invalid, or incomplete.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise ConfigError(
            f"Config file not found: {config_path}\n"
            f"Please copy config.example.json to config.json and fill in your credentials."
        )

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {e}")

    # Check required fields
    missing = [field for field in REQUIRED_FIELDS if field not in config]
    if missing:
        raise ConfigError(f"Missing required field(s): {', '.join(missing)}")

    # Set defaults for optional fields
    config.setdefault("imap_port", 993)
    config.setdefault("llm_api_key", None)

    return config
