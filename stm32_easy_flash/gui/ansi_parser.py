"""Lightweight ANSI-escape-code → HTML converter for terminal widget rendering."""

import re

# SGR foreground colour codes → CSS colour values
_ANSI_COLORS: dict[int, str] = {
    30: "black",
    31: "#cd3131",      # red
    32: "#0dbc79",      # green
    33: "#e5e510",      # yellow
    34: "#2472c8",      # blue
    35: "#bc3fbc",      # magenta
    36: "#11a8cd",      # cyan
    37: "#e5e5e5",      # white
    90: "#666666",      # bright black (gray)
    91: "#f14c4c",      # bright red
    92: "#23d18b",      # bright green
    93: "#f5f543",      # bright yellow
    94: "#3b8eea",      # bright blue
    95: "#d670d6",      # bright magenta
    96: "#29b8db",      # bright cyan
    97: "#e5e5e5",      # bright white
}

_ANSI_RE = re.compile(r"\x1b\[([0-9;]*)m")


def ansi_to_html(text: str) -> str:
    """Convert ANSI SGR colour sequences in *text* to ``<span>`` elements."""
    parts: list[str] = []
    open_spans = 0
    last = 0

    for match in _ANSI_RE.finditer(text):
        # Text before match
        before = text[last:match.start()]
        if before:
            parts.append(_escape_html(before))

        codes_str = match.group(1)
        if not codes_str or codes_str == "0":
            # Reset
            parts.append("</span>" * open_spans)
            open_spans = 0
        else:
            for code_str in codes_str.split(";"):
                try:
                    code = int(code_str)
                except ValueError:
                    continue
                if code in _ANSI_COLORS:
                    parts.append(f'<span style="color:{_ANSI_COLORS[code]}">')
                    open_spans += 1
                elif code == 1:
                    parts.append('<span style="font-weight:bold">')
                    open_spans += 1

        last = match.end()

    # Remaining text after last match
    remaining = text[last:]
    if remaining:
        parts.append(_escape_html(remaining))

    # Close any open spans
    parts.append("</span>" * open_spans)
    return "".join(parts)


def strip_ansi(text: str) -> str:
    """Remove all ANSI escape sequences from *text*."""
    return _ANSI_RE.sub("", text)


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
