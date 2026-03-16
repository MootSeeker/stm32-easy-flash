"""Integrated terminal widget – streams QProcess output in real time."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, QProcess, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from stm32_easy_flash.gui.ansi_parser import ansi_to_html

MAX_SCROLLBACK_LINES = 500


class TerminalWidget(QWidget):
    """Read-only terminal pane with QProcess-based real-time streaming."""

    process_finished = Signal(int)  # emits exit code

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process: Optional[QProcess] = None
        self._auto_scroll = True
        self._appending = False
        self._stdout_buf = ""
        self._stderr_buf = ""
        self._setup_ui()

    # -- UI setup ------------------------------------------------------------

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Terminal text area
        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setMaximumBlockCount(MAX_SCROLLBACK_LINES)
        self._text.setUndoRedoEnabled(False)

        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        self._text.setFont(font)

        self._text.setStyleSheet(
            "QPlainTextEdit { background-color: #1e1e1e; color: #cccccc; }"
        )

        # Scroll tracking
        self._text.verticalScrollBar().valueChanged.connect(self._on_scroll)

        # Context menu
        self._text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._text.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self._text)

        # Button bar
        btn_layout = QHBoxLayout()
        self._clear_btn = QPushButton("Leeren")
        self._clear_btn.clicked.connect(self.clear)
        btn_layout.addWidget(self._clear_btn)

        self._copy_btn = QPushButton("Kopieren")
        self._copy_btn.clicked.connect(self.copy_all)
        btn_layout.addWidget(self._copy_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    # -- scroll management ---------------------------------------------------

    def _on_scroll(self, value: int):
        if self._appending:
            return
        sb = self._text.verticalScrollBar()
        self._auto_scroll = value >= sb.maximum() - 10

    def _scroll_to_bottom(self):
        sb = self._text.verticalScrollBar()
        sb.setValue(sb.maximum())

    # -- context menu --------------------------------------------------------

    def _show_context_menu(self, pos):
        menu = self._text.createStandardContextMenu()
        copy_all_action = QAction("Alles kopieren", self)
        copy_all_action.triggered.connect(self.copy_all)
        menu.addSeparator()
        menu.addAction(copy_all_action)
        menu.exec(self._text.mapToGlobal(pos))

    # -- public helpers ------------------------------------------------------

    def append_line(self, text: str, *, is_stderr: bool = False):
        """Append a single output line with timestamp and optional colour."""
        ts = datetime.now().strftime("%H:%M:%S")
        escaped = ansi_to_html(text)
        if is_stderr:
            html = (
                f'<span style="color:#888888">[{ts}]</span> '
                f'<span style="color:#f14c4c">{escaped}</span>'
            )
        else:
            html = f'<span style="color:#888888">[{ts}]</span> {escaped}'

        self._appending = True
        self._text.appendHtml(html)
        if self._auto_scroll:
            self._scroll_to_bottom()
        self._appending = False

    def append_info(self, text: str):
        """Append an informational message (blue)."""
        ts = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<span style="color:#888888">[{ts}]</span> '
            f'<span style="color:#3b8eea">{text}</span>'
        )
        self._appending = True
        self._text.appendHtml(html)
        if self._auto_scroll:
            self._scroll_to_bottom()
        self._appending = False

    def clear(self):
        self._text.clear()

    def copy_all(self):
        QApplication.clipboard().setText(self._text.toPlainText())

    def is_running(self) -> bool:
        return (
            self._process is not None
            and self._process.state() != QProcess.ProcessState.NotRunning
        )

    # -- process management --------------------------------------------------

    def run_process(self, command: list[str]) -> bool:
        """Start *command* asynchronously. Returns False if busy."""
        if self.is_running():
            self.append_info("Ein Prozess laeuft bereits.")
            return False

        self._stdout_buf = ""
        self._stderr_buf = ""

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        program = command[0]
        args = command[1:]

        self.append_info(f"Starte: {program} {' '.join(args)}")
        self._process.start(program, args)
        return True

    # -- QProcess slots ------------------------------------------------------

    def _on_stdout(self):
        data = self._process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self._stdout_buf += data
        while "\n" in self._stdout_buf:
            line, self._stdout_buf = self._stdout_buf.split("\n", 1)
            self.append_line(line)

    def _on_stderr(self):
        data = self._process.readAllStandardError().data().decode("utf-8", errors="replace")
        self._stderr_buf += data
        while "\n" in self._stderr_buf:
            line, self._stderr_buf = self._stderr_buf.split("\n", 1)
            self.append_line(line, is_stderr=True)

    def _on_finished(self, exit_code: int, _exit_status):
        # Flush remaining buffer content
        if self._stdout_buf.strip():
            self.append_line(self._stdout_buf)
            self._stdout_buf = ""
        if self._stderr_buf.strip():
            self.append_line(self._stderr_buf, is_stderr=True)
            self._stderr_buf = ""

        self.append_info(f"[Prozess beendet mit Code {exit_code}]")
        self.process_finished.emit(exit_code)
