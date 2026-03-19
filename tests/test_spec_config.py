"""Tests for the PyInstaller spec file – ensures UPX stays disabled."""

import ast
import re
from pathlib import Path

SPEC_PATH = Path(__file__).resolve().parent.parent / "stm32_easy_flash.spec"


def _read_spec() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def test_upx_is_disabled():
    """upx=True triggers AV false positives (see issue #11). Ensure it stays False."""
    content = _read_spec()
    # Match the upx keyword argument in the EXE() call
    match = re.search(r"\bupx\s*=\s*(True|False)", content)
    assert match is not None, "Could not find 'upx=...' in spec file"
    assert match.group(1) == "False", (
        f"upx must be False to avoid AV false positives, but found upx={match.group(1)}"
    )


def test_spec_file_exists():
    """The spec file must exist at the repository root."""
    assert SPEC_PATH.is_file(), f"Spec file not found: {SPEC_PATH}"


def test_exe_name():
    """Verify the executable is named 'stm32_easy_flash'."""
    content = _read_spec()
    assert "name='stm32_easy_flash'" in content
