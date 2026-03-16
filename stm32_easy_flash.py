"""STM32 Easy Flash - Hotkey-triggered firmware flashing via STM32CubeProgrammer CLI."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import keyboard

# ==========================================
# CONFIGURATION - PLEASE ADJUST!
# ==========================================

# Path to STM32 Programmer CLI (default path on Windows)
DEFAULT_CLI_PATH = r"C:\ST\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe"

# Path to your firmware file
DEFAULT_FIRMWARE_PATH = r"C:\path\to\your\firmware.hex"

# Connection type (e.g. "SWD" for ST-LINK, "USB1" for DFU, "COM3" for UART)
DEFAULT_PORT = "SWD"

# Global hotkey to trigger flashing
DEFAULT_HOTKEY = "ctrl+shift+f12"

CONFIG_FILENAME = "stm32_easy_flash.config.json"

CLI_PATH = DEFAULT_CLI_PATH
FIRMWARE_PATH = DEFAULT_FIRMWARE_PATH
PORT = DEFAULT_PORT
HOTKEY = DEFAULT_HOTKEY

# ==========================================


def _runtime_directory():
    """Return the directory where config should be loaded from."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def load_runtime_config():
    """Load runtime configuration from JSON file and environment variables."""
    global CLI_PATH, FIRMWARE_PATH, PORT, HOTKEY

    config_path = _runtime_directory() / CONFIG_FILENAME
    file_config = {}

    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as file_handle:
                loaded = json.load(file_handle)
                if isinstance(loaded, dict):
                    file_config = loaded
                else:
                    print("Warning: Config file does not contain a JSON object. Using defaults.")
        except (OSError, json.JSONDecodeError) as error:
            print(f"Warning: Could not read config file '{config_path}': {error}")

    CLI_PATH = os.getenv("STM32_EASY_FLASH_CLI_PATH", file_config.get("CLI_PATH", DEFAULT_CLI_PATH))
    FIRMWARE_PATH = os.getenv("STM32_EASY_FLASH_FIRMWARE_PATH", file_config.get("FIRMWARE_PATH", DEFAULT_FIRMWARE_PATH))
    PORT = os.getenv("STM32_EASY_FLASH_PORT", file_config.get("PORT", DEFAULT_PORT))
    HOTKEY = os.getenv("STM32_EASY_FLASH_HOTKEY", file_config.get("HOTKEY", DEFAULT_HOTKEY))

    return config_path


def validate_configuration():
    """Validate required runtime settings before attempting to flash."""
    if not Path(CLI_PATH).is_file():
        print(f"\nError: CLI executable not found at '{CLI_PATH}'.")
        print("Update CLI_PATH in config/env before flashing.")
        return False

    if not Path(FIRMWARE_PATH).is_file():
        print(f"\nError: Firmware file not found at '{FIRMWARE_PATH}'.")
        print("Update FIRMWARE_PATH in config/env before flashing.")
        return False

    return True


def flash_mcu():
    """Erase and flash the STM32 target using STM32_Programmer_CLI."""
    if not validate_configuration():
        print("Waiting for a valid configuration...")
        return

    print("\n" + "-"*40)
    print("▶ Hotkey detected! Starting flash process...")

    # Build command:
    # -c port=... : Establish connection
    # -e all      : Full chip erase
    # -w <path>   : Write firmware
    # -v          : Verify (check write operation)
    # -rst        : Reset after flashing
    command = [
        CLI_PATH,
        "-c", f"port={PORT}",
        "-e", "all",
        "-w", FIRMWARE_PATH,
        "-v",
        "-rst"
    ]

    try:
        # Run the CLI. stdout and stderr are forwarded directly to the console
        # so that progress output is visible in real time.
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True) as process:
            for line in process.stdout:
                print(line, end="")

        if process.returncode == 0:
            print("\n✅ Successfully erased and flashed!")
        else:
            print(f"\n❌ Flash error! Return code: {process.returncode}")

    except FileNotFoundError:
        print(f"\n❌ Error: '{CLI_PATH}' not found. Please check CLI_PATH!")
    except OSError as e:
        print(f"\n❌ An unexpected error occurred: {e}")

    print("-" * 40)
    print(f"Waiting for '{HOTKEY}'... (Exit with Ctrl+C)")


# Main program
if __name__ == "__main__":
    config_file_path = load_runtime_config()

    print("STM32 Easy Flash started.")
    print(f"Config file: {config_file_path}")
    print(f"Configured hotkey: {HOTKEY}")
    print(f"Configured port: {PORT}")
    print(f"Firmware: {FIRMWARE_PATH}")
    print(f"\nWaiting for '{HOTKEY}'... (Exit with Ctrl+C in terminal)")

    try:
        # Register hotkey from config/env; default remains ctrl+shift+f12.
        keyboard.add_hotkey(HOTKEY, flash_mcu)

        # Keep the script alive so the hotkey listener remains active.
        # Press Ctrl+C in the terminal to exit cleanly.
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nScript terminated by user.")
        sys.exit(0)
