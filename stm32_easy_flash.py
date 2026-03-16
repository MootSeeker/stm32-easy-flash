import keyboard
import subprocess
import time
import sys

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
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            # Print CLI output line by line
            print(line, end="")
            
        process.wait()
        
        if process.returncode == 0:
            print("\n✅ Successfully erased and flashed!")
        else:
            print(f"\n❌ Flash error! Return code: {process.returncode}")
            
    except FileNotFoundError:
        print(f"\n❌ Error: '{CLI_PATH}' not found. Please check CLI_PATH!")
    except Exception as e:
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