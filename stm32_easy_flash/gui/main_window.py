"""Main application window – configuration fields, buttons, terminal, hotkey."""

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from stm32_easy_flash.config_service import ConfigService
from stm32_easy_flash.flash_service import FlashService
from stm32_easy_flash.gui.terminal_widget import TerminalWidget
from stm32_easy_flash.hotkey_service import HotkeyService

# Fixed port presets shown at the top of the combo box
_FIXED_PORTS = ["SWD", "JTAG", "USB1"]


def _detect_com_ports() -> list[str]:
    """Return a list of available COM / serial ports (requires *pyserial*)."""
    try:
        import serial.tools.list_ports
        return sorted(p.device for p in serial.tools.list_ports.comports())
    except ImportError:
        return []


class _HotkeyBridge(QObject):
    """Thread-safe bridge: emitted from hotkey thread, received in GUI thread."""
    triggered = Signal()


class MainWindow(QMainWindow):
    """STM32 Easy Flash – Hauptfenster."""

    def __init__(self):
        super().__init__()

        self._config = ConfigService()
        self._config.load()

        self._hotkey_bridge = _HotkeyBridge()
        self._hotkey_bridge.triggered.connect(self._on_flash)
        self._hotkey_svc = HotkeyService()

        self._setup_ui()
        self._load_config_to_ui()
        self._register_hotkey()

    # -- UI setup ------------------------------------------------------------

    def _setup_ui(self):
        self.setWindowTitle("STM32 Easy Flash")
        self.setMinimumSize(750, 520)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # --- Configuration fields ---
        grid = QGridLayout()

        # CLI path
        grid.addWidget(QLabel("STM32CubeProgrammer CLI:"), 0, 0)
        self._cli_edit = QLineEdit()
        grid.addWidget(self._cli_edit, 0, 1)
        cli_browse = QPushButton("...")
        cli_browse.setFixedWidth(40)
        cli_browse.clicked.connect(self._browse_cli)
        grid.addWidget(cli_browse, 0, 2)

        # Firmware path
        grid.addWidget(QLabel("Firmware:"), 1, 0)
        self._fw_edit = QLineEdit()
        grid.addWidget(self._fw_edit, 1, 1)
        fw_browse = QPushButton("...")
        fw_browse.setFixedWidth(40)
        fw_browse.clicked.connect(self._browse_firmware)
        grid.addWidget(fw_browse, 1, 2)

        # Port (editable combo + refresh)
        grid.addWidget(QLabel("Port:"), 2, 0)
        self._port_combo = QComboBox()
        self._port_combo.setEditable(True)
        self._refresh_ports()
        grid.addWidget(self._port_combo, 2, 1)
        port_refresh = QPushButton("\u21bb")  # ↻
        port_refresh.setFixedWidth(40)
        port_refresh.clicked.connect(self._refresh_ports)
        grid.addWidget(port_refresh, 2, 2)

        # Hotkey
        grid.addWidget(QLabel("Hotkey:"), 3, 0)
        self._hotkey_edit = QLineEdit()
        grid.addWidget(self._hotkey_edit, 3, 1)

        main_layout.addLayout(grid)

        # --- Action buttons ---
        btn_layout = QHBoxLayout()

        self._save_btn = QPushButton("Speichern")
        self._save_btn.clicked.connect(self._save_config)
        btn_layout.addWidget(self._save_btn)

        self._flash_btn = QPushButton("Programm")
        self._flash_btn.clicked.connect(self._on_flash)
        btn_layout.addWidget(self._flash_btn)

        btn_layout.addStretch()

        self._close_btn = QPushButton("Schliessen")
        self._close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self._close_btn)

        main_layout.addLayout(btn_layout)

        # --- Terminal ---
        self._terminal = TerminalWidget()
        self._terminal.process_finished.connect(self._on_flash_finished)
        main_layout.addWidget(self._terminal, stretch=1)

        # --- Status bar ---
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Bereit")

    # -- file dialogs --------------------------------------------------------

    def _browse_cli(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "STM32CubeProgrammer CLI auswaehlen", "",
            "Executable (*.exe);;Alle Dateien (*)",
        )
        if path:
            self._cli_edit.setText(path)

    def _browse_firmware(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Firmware-Datei auswaehlen", "",
            "Firmware (*.hex *.bin *.elf);;Alle Dateien (*)",
        )
        if path:
            self._fw_edit.setText(path)

    # -- port helpers --------------------------------------------------------

    def _refresh_ports(self):
        current = self._port_combo.currentText()
        self._port_combo.clear()
        self._port_combo.addItems(_FIXED_PORTS)

        com_ports = _detect_com_ports()
        if com_ports:
            self._port_combo.insertSeparator(len(_FIXED_PORTS))
            self._port_combo.addItems(com_ports)

        # Restore previous selection
        idx = self._port_combo.findText(current)
        if idx >= 0:
            self._port_combo.setCurrentIndex(idx)
        elif current:
            self._port_combo.setEditText(current)

    # -- config <-> UI -------------------------------------------------------

    def _load_config_to_ui(self):
        self._cli_edit.setText(self._config.cli_path)
        self._fw_edit.setText(self._config.firmware_path)

        port = self._config.port
        idx = self._port_combo.findText(port)
        if idx >= 0:
            self._port_combo.setCurrentIndex(idx)
        else:
            self._port_combo.setEditText(port)

        self._hotkey_edit.setText(self._config.hotkey)

    def _save_config(self):
        self._config.cli_path = self._cli_edit.text()
        self._config.firmware_path = self._fw_edit.text()
        self._config.port = self._port_combo.currentText()
        self._config.hotkey = self._hotkey_edit.text()

        if self._config.save():
            self._status.showMessage("Konfiguration gespeichert", 3000)
        else:
            self._status.showMessage("Fehler beim Speichern der Konfiguration")

        # Re-register hotkey with (possibly) new value
        self._register_hotkey()

    # -- hotkey management ---------------------------------------------------

    def _register_hotkey(self):
        if not HotkeyService.is_available():
            self._status.showMessage(
                "Hotkey nicht verfuegbar – pynput nicht installiert"
            )
            return

        hotkey = self._hotkey_edit.text().strip()
        if not hotkey:
            self._hotkey_svc.unregister()
            return

        ok, error = self._hotkey_svc.register(
            hotkey, self._hotkey_bridge.triggered.emit
        )
        if ok:
            self._status.showMessage(f"Hotkey '{hotkey}' registriert", 3000)
        else:
            self._status.showMessage(f"Hotkey-Fehler: {error}")

    # -- flash action --------------------------------------------------------

    @Slot()
    def _on_flash(self):
        if self._terminal.is_running():
            self._status.showMessage("Flash-Vorgang laeuft bereits...")
            return

        cli = self._cli_edit.text()
        firmware = self._fw_edit.text()
        port = self._port_combo.currentText()

        service = FlashService(cli, firmware, port)
        ok, error = service.validate()
        if not ok:
            self._status.showMessage(f"Fehler: {error}")
            self._terminal.append_info(f"Fehler: {error}")
            return

        self._flash_btn.setEnabled(False)
        self._status.showMessage("Flashen laeuft...")
        self._terminal.run_process(service.build_command())

    @Slot(int)
    def _on_flash_finished(self, exit_code: int):
        self._flash_btn.setEnabled(True)
        if exit_code == 0:
            self._status.showMessage("Flashen erfolgreich abgeschlossen")
        else:
            self._status.showMessage(f"Flashen fehlgeschlagen (Code {exit_code})")

    # -- cleanup -------------------------------------------------------------

    def closeEvent(self, event):
        self._hotkey_svc.unregister()
        event.accept()
