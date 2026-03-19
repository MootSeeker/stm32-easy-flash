"""Tests for HotkeyService – format conversion and availability check."""

from stm32_easy_flash.hotkey_service import (
    HotkeyService,
    to_pynput_format,
    from_pynput_format,
)


def test_to_pynput_format_basic():
    assert to_pynput_format("ctrl+shift+f12") == "<ctrl>+<shift>+<f12>"


def test_to_pynput_format_single_char():
    assert to_pynput_format("ctrl+a") == "<ctrl>+a"


def test_to_pynput_format_cmd():
    assert to_pynput_format("cmd+shift+f12") == "<cmd>+<shift>+<f12>"


def test_from_pynput_format():
    assert from_pynput_format("<ctrl>+<shift>+<f12>") == "ctrl+shift+f12"


def test_from_pynput_format_single_char():
    assert from_pynput_format("<ctrl>+a") == "ctrl+a"


def test_roundtrip():
    original = "ctrl+shift+f12"
    assert from_pynput_format(to_pynput_format(original)) == original


def test_is_available():
    """pynput should be importable in the test environment."""
    assert HotkeyService.is_available() is True


def test_unregister_without_register():
    """Calling unregister without a prior register should not raise."""
    svc = HotkeyService()
    svc.unregister()
