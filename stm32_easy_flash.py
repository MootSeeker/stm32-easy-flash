"""STM32 Easy Flash - Hotkey-triggered firmware flashing via STM32CubeProgrammer CLI."""

import subprocess
import sys
import time

import keyboard

# ==========================================
# CONFIGURATION - PLEASE ADJUST!
# ==========================================

# Path to STM32 Programmer CLI (default path on Windows)
CLI_PATH = r"C:\ST\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe"

# Path to your firmware file
FIRMWARE_PATH = r"C:\path\to\your\firmware.hex"

# Connection type (e.g. "SWD" for ST-LINK, "USB1" for DFU, "COM3" for UART)
PORT = "SWD"

# ==========================================


def flash_mcu():
    """Erase and flash the STM32 target using STM32_Programmer_CLI."""
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
    print("Waiting for 'ctrl + shift + f12'... (Exit with Ctrl+C)")


# Main program
if __name__ == "__main__":
    print("STM32 Easy Flash started.")
    print(f"Configured port: {PORT}")
    print(f"Firmware: {FIRMWARE_PATH}")
    print("\nWaiting for 'ctrl + shift + f12'... (Exit with Ctrl+C in terminal)")

    try:
        # Register hotkey. Pressing ctrl+shift+f12 will trigger flash_mcu()
        keyboard.add_hotkey('ctrl+shift+f12', flash_mcu)

        # Keep the script alive so the hotkey listener remains active.
        # Press Ctrl+C in the terminal to exit cleanly.
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nScript terminated by user.")
        sys.exit(0)
