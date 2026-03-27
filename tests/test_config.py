# tests/test_config.py
import pytest
import json
from pathlib import Path
from src.config import load_config, ConfigError

def test_load_config_from_file(tmp_path):
    """Test loading config from existing file."""
    config_path = tmp_path / "config.json"
    config_data = {
        "imap_server": "imap.test.com",
        "imap_port": 993,
        "email": "test@test.com",
        "password": "test-pass"
    }
    config_path.write_text(json.dumps(config_data))

    config = load_config(str(config_path))
    assert config["imap_server"] == "imap.test.com"
    assert config["imap_port"] == 993
    assert config["email"] == "test@test.com"
    assert config["password"] == "test-pass"

def test_load_config_missing_file(tmp_path):
    """Test error when config file is missing."""
    config_path = tmp_path / "nonexistent.json"
    with pytest.raises(ConfigError, match="Config file not found"):
        load_config(str(config_path))

def test_load_config_invalid_json(tmp_path):
    """Test error when config file is invalid JSON."""
    config_path = tmp_path / "invalid.json"
    config_path.write_text("not valid json")

    with pytest.raises(ConfigError, match="Invalid JSON"):
        load_config(str(config_path))

def test_load_config_missing_required_fields(tmp_path):
    """Test error when required fields are missing."""
    config_path = tmp_path / "incomplete.json"
    config_path.write_text('{"imap_server": "imap.test.com"}')

    with pytest.raises(ConfigError, match="Missing required field"):
        load_config(str(config_path))
