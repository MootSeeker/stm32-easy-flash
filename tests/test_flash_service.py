"""Tests for FlashService – command builder and validation logic."""

from stm32_easy_flash.flash_service import FlashService


def test_build_command():
    """build_command returns the expected argument list."""
    svc = FlashService(
        cli_path="/usr/bin/STM32_Programmer_CLI",
        firmware_path="/tmp/firmware.hex",
        port="SWD",
    )
    cmd = svc.build_command()
    assert cmd[0] == "/usr/bin/STM32_Programmer_CLI"
    assert "-c" in cmd
    assert "port=SWD" in cmd
    assert "-w" in cmd
    assert "/tmp/firmware.hex" in cmd
    assert "-v" in cmd
    assert "-rst" in cmd


def test_validate_missing_cli_path():
    svc = FlashService(cli_path="", firmware_path="/tmp/fw.hex", port="SWD")
    ok, msg = svc.validate()
    assert not ok
    assert "CLI" in msg


def test_validate_missing_firmware_path():
    svc = FlashService(cli_path="/bin/sh", firmware_path="", port="SWD")
    ok, msg = svc.validate()
    assert not ok
    assert "Firmware" in msg


def test_validate_missing_port():
    svc = FlashService(cli_path="/bin/sh", firmware_path="/bin/sh", port="")
    ok, msg = svc.validate()
    assert not ok
    assert "Port" in msg


def test_validate_cli_not_found():
    svc = FlashService(
        cli_path="/nonexistent/path/cli",
        firmware_path="/bin/sh",
        port="SWD",
    )
    ok, msg = svc.validate()
    assert not ok
    assert "nicht gefunden" in msg


def test_validate_success(tmp_path):
    """Validation passes when both paths point to real files."""
    cli = tmp_path / "cli"
    fw = tmp_path / "fw.hex"
    cli.write_text("fake")
    fw.write_text("fake")
    svc = FlashService(cli_path=str(cli), firmware_path=str(fw), port="SWD")
    ok, msg = svc.validate()
    assert ok
    assert msg == ""
