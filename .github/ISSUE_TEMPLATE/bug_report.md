---
name: Bug Report
about: Report a bug or unexpected behaviour
title: '[Bug] Built executable is flagged as a virus / malware by Windows Defender or macOS Gatekeeper'
labels: bug
assignees: ''
---

## Bug Report

---

### Description

The pre-built `stm32_easy_flash.exe` (Windows) and the macOS binary
(`stm32_easy_flash_macos.zip`) distributed via GitHub Releases are incorrectly
flagged as malware or a virus by security software such as:

- **Windows Defender** (SmartScreen / real-time protection)
- **macOS Gatekeeper** / XProtect
- Various third-party antivirus engines (e.g. Avast, AVG, Kaspersky, ESET, …)

As a result, users cannot download, install, or launch the application without
manually adding a security exception — or the operating system silently deletes
the file.

---

### Steps to Reproduce

1. Download `stm32_easy_flash.exe` from the latest
   [GitHub Release](https://github.com/MootSeeker/stm32-easy-flash/releases/latest).
2. Attempt to open the file on a **Windows** machine with Windows Defender
   enabled (default installation).
3. Observe the SmartScreen warning *"Windows protected your PC"* or an
   automatic quarantine/deletion by the AV engine.

*(Identical behaviour on macOS: Gatekeeper blocks the unsigned binary with
"Apple cannot check it for malicious software".)*

---

### Expected Behaviour

The executable can be downloaded, launched, and used without any security
warnings.

---

### Actual Behaviour

The operating system or antivirus software:

- displays a warning and refuses to execute the file, **or**
- silently quarantines / deletes the file immediately after download.

---

### Root Cause Analysis

The false-positive detections are caused by a combination of factors typical
for **PyInstaller**-packaged applications:

| Factor | Why it triggers AV heuristics |
|--------|-------------------------------|
| **UPX compression** (`upx=True` in `stm32_easy_flash.spec`) | UPX-packed executables are a common obfuscation technique used by malware; many AV engines flag any UPX-packed binary as suspicious by default. |
| **PyInstaller bootloader** | The bootloader self-extracts a Python runtime to `%TEMP%` at startup — a behaviour pattern associated with droppers and self-extracting malware. |
| **No code-signing certificate** | Both Windows SmartScreen and macOS Gatekeeper require a valid, trusted code-signing certificate; unsigned binaries receive an automatic reputation penalty. |
| **`pynput` (global keyboard/mouse hook)** | The library installs system-wide input hooks, which is a capability strongly associated with keyloggers and spyware. |

---

### Environment

| Field | Value |
|-------|-------|
| OS | Windows 10 / 11 and macOS 13+ |
| AV / Security Software | Windows Defender, macOS Gatekeeper |
| Application version | latest release |
| Build tool | PyInstaller (see `stm32_easy_flash.spec`) |

---

### Suggested Fixes / Workarounds

**Short-term workarounds for end users:**

1. Add a manual Windows Defender exclusion for the downloaded file or folder.
2. On macOS: right-click → *Open* → confirm in the dialog, then allow access
   under *System Settings → Privacy & Security → Accessibility*.

**Longer-term fixes for maintainers:**

1. **Disable UPX compression** — set `upx=False` in `stm32_easy_flash.spec`.
   This is the single most effective measure to reduce false-positive rates with
   most AV engines.
2. **Sign the Windows executable** — obtain an EV or standard
   Authenticode certificate and add a signing step to the CI workflow (e.g.
   using `signtool.exe` or the
   [`signtool-action`](https://github.com/dlemstra/code-sign-action)).
3. **Notarise the macOS binary** — sign with an Apple Developer certificate and
   submit for notarisation via `xcrun notarytool` so Gatekeeper trusts the app.
4. **Add a VirusTotal scan step** to CI to catch regressions early and track
   the false-positive rate across releases.

---

### Additional Context

- This is a **false positive**. The source code is open and available for
  inspection in this repository; the binary contains no malicious code.
- PyInstaller false-positives are a
  [well-documented, widespread issue](https://github.com/pyinstaller/pyinstaller/wiki/FAQ#antivirus-false-positives).
- Submitting the binary to AV vendors for whitelisting
  ([Windows Defender submission](https://www.microsoft.com/en-us/wdsi/filesubmission))
  can help but requires repeated re-submission after every new build.
