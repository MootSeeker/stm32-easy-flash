"""Flash service – builds and validates the STM32CubeProgrammer CLI command."""

from pathlib import Path


class FlashService:
    """Encapsulates the flash-command logic without any GUI dependency."""

    def __init__(self, cli_path: str, firmware_path: str, port: str):
        self.cli_path = cli_path
        self.firmware_path = firmware_path
        self.port = port

    def validate(self) -> tuple[bool, str]:
        """Return *(True, "")* when the configuration is valid, else *(False, error)*."""
        if not self.cli_path:
            return False, "CLI-Pfad ist nicht gesetzt."
        if not Path(self.cli_path).is_file():
            return False, f"CLI nicht gefunden: '{self.cli_path}'"
        if not self.firmware_path:
            return False, "Firmware-Pfad ist nicht gesetzt."
        if not Path(self.firmware_path).is_file():
            return False, f"Firmware nicht gefunden: '{self.firmware_path}'"
        if not self.port:
            return False, "Port ist nicht gesetzt."
        return True, ""

    def build_command(self) -> list[str]:
        """Return the full CLI command as a list of arguments."""
        return [
            self.cli_path,
            "-c", f"port={self.port}",
            "-e", "all",
            "-w", self.firmware_path,
            "-v",
            "-rst",
        ]
