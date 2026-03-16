# stm32-easy-flash

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/powered-by-coffee.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
[![forthebadge](https://forthebadge.com/images/badges/open-source.svg)](https://forthebadge.com)

Simple flashing tool for the STM32 ecosystem.

Listens for a global hotkey (`Ctrl+Shift+F12`) and automatically flashes an STM32 device using **STM32CubeProgrammer CLI** — no need to open any GUI.

---

## Features

- One-keystroke flashing from anywhere on your desktop
- Full chip erase before programming
- Write & verify firmware
- Automatic reset after flashing
- Real-time CLI output in the terminal
- Supports SWD (ST-LINK), DFU (USB) and UART connections

---

## Requirements

- Python 3.8+
- [STM32CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html) installed (CLI must be accessible)
- Python packages:
  ```
  keyboard
  ```

Install the dependency with:

```bash
pip install keyboard
```

> **Note:** On Windows the script must be run with **administrator privileges** for the global hotkey listener to work reliably.

---

## Configuration

Open `stm32_easy_flash.py` and adjust the three constants at the top of the file:

```python
# Path to STM32 Programmer CLI (default path on Windows)
CLI_PATH = r"C:\ST\STM32CubeProgrammer\bin\STM32_Programmer_CLI.exe"

# Path to your firmware file (.hex, .bin, .elf, …)
FIRMWARE_PATH = r"C:\path\to\your\firmware.hex"

# Connection type: "SWD" for ST-LINK | "USB1" for DFU | "COM3" for UART
PORT = "SWD"
```

---

## Usage

```bash
python stm32_easy_flash.py
```

The script starts and waits in the background. Whenever you press **Ctrl+Shift+F12**, it:

1. Erases the entire chip
2. Writes the configured firmware
3. Verifies the written data
4. Resets the MCU

Stop the script at any time with **Ctrl+C** in the terminal.

---

## Supported Connection Types

| Value   | Interface        |
|---------|-----------------|
| `SWD`   | ST-LINK via SWD |
| `JTAG`  | ST-LINK via JTAG|
| `USB1`  | DFU over USB    |
| `COMx`  | UART bootloader |

---

## License

MIT © 2026 [MootSeeker](https://github.com/MootSeeker)
