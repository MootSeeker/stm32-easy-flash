"""Tests for ConfigService – defaults, load, save, and path resolution."""

import json
import sys

from stm32_easy_flash.config_service import ConfigService, DEFAULTS


def test_defaults():
    """A fresh ConfigService should use the defined defaults."""
    svc = ConfigService()
    assert svc.cli_path == DEFAULTS["CLI_PATH"]
    assert svc.firmware_path == DEFAULTS["FIRMWARE_PATH"]
    assert svc.port == DEFAULTS["PORT"]
    assert svc.hotkey == DEFAULTS["HOTKEY"]


def test_save_and_load(tmp_path, monkeypatch):
    """Round-trip: save config then load it back."""
    config_file = tmp_path / "stm32_easy_flash.config.json"

    svc = ConfigService()
    monkeypatch.setattr(svc, "_config_path", config_file)

    svc.cli_path = "/custom/cli"
    svc.firmware_path = "/custom/fw.hex"
    svc.port = "USB1"
    svc.hotkey = "ctrl+f5"

    assert svc.save()
    assert config_file.exists()

    svc2 = ConfigService()
    monkeypatch.setattr(svc2, "_config_path", config_file)
    svc2.load()

    assert svc2.cli_path == "/custom/cli"
    assert svc2.firmware_path == "/custom/fw.hex"
    assert svc2.port == "USB1"
    assert svc2.hotkey == "ctrl+f5"


def test_load_missing_file(tmp_path, monkeypatch):
    """Loading from a nonexistent file should leave defaults intact."""
    svc = ConfigService()
    monkeypatch.setattr(svc, "_config_path", tmp_path / "missing.json")
    svc.load()
    assert svc.port == DEFAULTS["PORT"]


def test_load_corrupt_json(tmp_path, monkeypatch):
    """A corrupt JSON file should not crash; defaults should remain."""
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{invalid json", encoding="utf-8")

    svc = ConfigService()
    monkeypatch.setattr(svc, "_config_path", bad_file)
    svc.load()
    assert svc.port == DEFAULTS["PORT"]


def test_load_partial_config(tmp_path, monkeypatch):
    """A config file with only some keys should fill the rest from defaults."""
    partial = tmp_path / "partial.json"
    partial.write_text(json.dumps({"PORT": "JTAG"}), encoding="utf-8")

    svc = ConfigService()
    monkeypatch.setattr(svc, "_config_path", partial)
    svc.load()

    assert svc.port == "JTAG"
    assert svc.hotkey == DEFAULTS["HOTKEY"]
