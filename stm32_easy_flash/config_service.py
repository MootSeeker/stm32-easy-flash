"""Configuration service – loads and persists settings from a JSON file next to the executable."""

import json
import sys
from pathlib import Path

CONFIG_FILENAME = "stm32_easy_flash.config.json"


def _default_cli_path() -> str:
    if sys.platform == "darwin":
        return (
            "/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer"
            "/STM32CubeProgrammer.app/Contents/MacOs/bin/STM32_Programmer_CLI"
        )
    if sys.platform.startswith("linux"):
        return "/usr/local/bin/STM32_Programmer_CLI"
    # Windows
    return r"C:\ST\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe"


def _default_hotkey() -> str:
    # macOS convention: cmd instead of ctrl
    if sys.platform == "darwin":
        return "cmd+shift+f12"
    return "ctrl+shift+f12"


DEFAULTS = {
    "CLI_PATH": _default_cli_path(),
    "FIRMWARE_PATH": "",
    "PORT": "SWD",
    "HOTKEY": _default_hotkey(),
}


class ConfigService:
    """Read / write application configuration as JSON next to the executable."""

    def __init__(self):
        self._config: dict[str, str] = dict(DEFAULTS)
        self._config_path = self._resolve_config_path()

    # -- path resolution -----------------------------------------------------

    @staticmethod
    def _resolve_config_path() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent / CONFIG_FILENAME
        return Path(__file__).resolve().parent.parent / CONFIG_FILENAME

    @property
    def config_path(self) -> Path:
        return self._config_path

    # -- property accessors --------------------------------------------------

    @property
    def cli_path(self) -> str:
        return self._config["CLI_PATH"]

    @cli_path.setter
    def cli_path(self, value: str):
        self._config["CLI_PATH"] = value

    @property
    def firmware_path(self) -> str:
        return self._config["FIRMWARE_PATH"]

    @firmware_path.setter
    def firmware_path(self, value: str):
        self._config["FIRMWARE_PATH"] = value

    @property
    def port(self) -> str:
        return self._config["PORT"]

    @port.setter
    def port(self, value: str):
        self._config["PORT"] = value

    @property
    def hotkey(self) -> str:
        return self._config["HOTKEY"]

    @hotkey.setter
    def hotkey(self, value: str):
        self._config["HOTKEY"] = value

    # -- persistence ---------------------------------------------------------

    def load(self) -> None:
        """Load configuration from the JSON file (if it exists)."""
        if not self._config_path.exists():
            return
        try:
            with self._config_path.open("r", encoding="utf-8") as fh:
                loaded = json.load(fh)
                if isinstance(loaded, dict):
                    for key in DEFAULTS:
                        if key in loaded:
                            self._config[key] = loaded[key]
        except (OSError, json.JSONDecodeError):
            pass

    def save(self) -> bool:
        """Persist the current configuration to JSON. Returns *True* on success."""
        try:
            with self._config_path.open("w", encoding="utf-8") as fh:
                json.dump(self._config, fh, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False
