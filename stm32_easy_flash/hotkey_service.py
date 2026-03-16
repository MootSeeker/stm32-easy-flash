"""Cross-platform global hotkey service using pynput.

On macOS:  requires Accessibility permission
           (Systemeinstellungen → Datenschutz & Sicherheit → Bedienungshilfen)
On Windows: no special permissions needed
"""

import re
import threading
from typing import Callable

try:
    from pynput import keyboard as _pynput_kb
    _PYNPUT_AVAILABLE = True
except ImportError:
    _pynput_kb = None
    _PYNPUT_AVAILABLE = False


# Keys that pynput wraps in <...>
_SPECIAL_KEYS = {
    "ctrl", "shift", "alt", "cmd", "meta", "super",
    "f1", "f2", "f3", "f4", "f5", "f6",
    "f7", "f8", "f9", "f10", "f11", "f12",
    "space", "enter", "return", "tab", "backspace", "delete",
    "up", "down", "left", "right",
    "page_up", "page_down", "home", "end",
    "insert", "escape", "caps_lock", "num_lock", "scroll_lock",
    "print_screen", "pause",
}


def to_pynput_format(hotkey: str) -> str:
    """Convert ``ctrl+shift+f12`` notation to pynput ``<ctrl>+<shift>+<f12>``."""
    parts = [p.strip().lower() for p in hotkey.split("+")]
    converted = []
    for part in parts:
        if part in _SPECIAL_KEYS:
            converted.append(f"<{part}>")
        else:
            converted.append(part)
    return "+".join(converted)


def from_pynput_format(hotkey: str) -> str:
    """Convert pynput ``<ctrl>+<shift>+<f12>`` back to ``ctrl+shift+f12``."""
    return re.sub(r"<([^>]+)>", r"\1", hotkey)


class HotkeyService:
    """Register / unregister a single global hotkey using pynput."""

    def __init__(self):
        self._listener: "_pynput_kb.GlobalHotKeys | None" = None
        self._lock = threading.Lock()

    @staticmethod
    def is_available() -> bool:
        return _PYNPUT_AVAILABLE

    def register(self, hotkey: str, callback: Callable[[], None]) -> tuple[bool, str]:
        """Register *hotkey* and call *callback* when it is pressed.

        Returns *(True, "")* on success or *(False, error_message)*.
        """
        if not _PYNPUT_AVAILABLE:
            return False, "pynput ist nicht installiert. Hotkeys sind nicht verfuegbar."

        self.unregister()

        pynput_key = to_pynput_format(hotkey)
        try:
            self._listener = _pynput_kb.GlobalHotKeys(
                {pynput_key: callback}
            )
            self._listener.start()
            return True, ""
        except OSError as exc:
            self._listener = None
            return False, str(exc)
        except Exception as exc:  # pynput raises various undocumented errors
            self._listener = None
            return False, str(exc)

    def unregister(self) -> None:
        """Stop the active hotkey listener if one is running."""
        with self._lock:
            if self._listener is not None:
                try:
                    self._listener.stop()
                except Exception:  # pynput stop() can raise on some platforms
                    pass
                self._listener = None
