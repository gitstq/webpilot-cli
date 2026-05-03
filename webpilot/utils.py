"""
Utility functions for WebPilot-CLI.

Provides URL validation/normalization, file path handling,
a simple YAML parser (no PyYAML dependency), and progress bar display.
"""

import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# URL utilities
# ---------------------------------------------------------------------------

def validate_url(url: str) -> bool:
    """Validate whether a string is a well-formed HTTP/HTTPS URL.

    Args:
        url: The URL string to validate.

    Returns:
        True if the URL is valid, False otherwise.
    """
    pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:\S+(?::\S*)?@)?"  # optional user:pass@
        r"(?:"
        r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"  # IP address
        r"\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])"
        r"\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])"
        r"\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])"
        r"|"
        r"(?:[a-zA-Z\u00a1-\uffff0-9]-?)*[a-zA-Z\u00a1-\uffff0-9]+"  # domain
        r"(?:\.(?:[a-zA-Z\u00a1-\uffff0-9]-?)*[a-zA-Z\u00a1-\uffff0-9]+)*"
        r"\.(?:[a-zA-Z\u00a1-\uffff]{2,})"  # TLD
        r")"
        r"(?::\d{2,5})?"  # optional port
        r"(?:/[^\s]*)?"  # optional path
        r"(?:\?[^\s]*)?"  # optional query string
        r"$",  # end of string
        re.UNICODE,
    )
    return bool(pattern.match(url))


def normalize_url(url: str) -> str:
    """Normalize a URL by ensuring it has a scheme and removing fragments.

    Args:
        url: The URL string to normalize.

    Returns:
        The normalized URL string.
    """
    url = url.strip()
    # Add https:// if no scheme is present
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    # Remove trailing fragment
    url = re.sub(r"#.*$", "", url)
    return url


def extract_domain(url: str) -> str:
    """Extract the domain name from a URL.

    Args:
        url: The URL string.

    Returns:
        The domain name (e.g. 'www.example.com').
    """
    match = re.search(r"https?://([^/]+)", url)
    if match:
        return match.group(1)
    return url


# ---------------------------------------------------------------------------
# File path utilities
# ---------------------------------------------------------------------------

def ensure_dir(filepath: str) -> str:
    """Ensure the parent directory of a file path exists.

    Args:
        filepath: Path to a file.

    Returns:
        The same filepath (unchanged).
    """
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    return filepath


def safe_filename(name: str, max_length: int = 200) -> str:
    """Convert a string to a safe filename by removing invalid characters.

    Args:
        name: The desired filename.
        max_length: Maximum allowed length.

    Returns:
        A safe filename string.
    """
    # Replace invalid characters with underscores
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    # Remove leading/trailing dots and spaces
    safe = safe.strip(". ")
    # Truncate to max length
    if len(safe) > max_length:
        safe = safe[:max_length]
    # Fallback if empty
    if not safe:
        safe = "unnamed"
    return safe


def get_file_extension(url: str, default: str = ".html") -> str:
    """Extract a likely file extension from a URL path.

    Args:
        url: The URL string.
        default: Default extension if none found.

    Returns:
        The file extension including the dot (e.g. '.html').
    """
    path = re.sub(r"\?.*$", "", url)  # remove query string
    match = re.search(r"(\.\w{1,5})$", path)
    if match:
        ext = match.group(1).lower()
        # Only return common web extensions
        if ext in (".html", ".htm", ".css", ".js", ".json", ".xml", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".svg"):
            return ext
    return default


# ---------------------------------------------------------------------------
# Simple YAML parser (no PyYAML dependency)
# ---------------------------------------------------------------------------

def _strip_inline_comment(text: str) -> str:
    """Remove an inline YAML comment (# ...) from a value string.

    Handles quoted strings so that '#' inside quotes is not treated as a comment.
    """
    in_single = False
    in_double = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '#' and not in_single and not in_double:
            # Check if preceded by whitespace (YAML comment rule)
            if i == 0 or text[i - 1] in (' ', '\t'):
                return text[:i].rstrip()
        i += 1
    return text


def parse_yaml(text: str) -> Any:
    """Parse a simple YAML document into Python objects.

    Supports:
    - Mappings (key: value)
    - Sequences (- item)
    - Scalars (strings, numbers, booleans, null)
    - Multi-line strings (| or >)
    - Nested structures via indentation
    - Inline comments

    Note: This is a simplified parser and does not support the full YAML spec.
    Features like anchors, aliases, tags, and complex flow syntax are not supported.

    Args:
        text: The YAML document as a string.

    Returns:
        Parsed Python object (dict, list, or scalar).
    """
    lines = text.split("\n")
    # Remove leading/trailing empty lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return {}

    result, _ = _parse_yaml_lines(lines, 0, 0)
    return result


def _get_indent(line: str) -> int:
    """Return the number of leading spaces in a line."""
    return len(line) - len(line.lstrip(" "))


def _parse_yaml_lines(
    lines: List[str], start: int, base_indent: int
) -> tuple:
    """Recursively parse YAML lines starting from *start* at *base_indent*.

    Returns:
        A tuple of (parsed_value, next_line_index).
    """
    if start >= len(lines):
        return None, start

    # Determine the type of the first content line
    first_line = lines[start]
    stripped = first_line.strip()

    # Skip empty lines and comments
    if not stripped or stripped.startswith("#"):
        return _parse_yaml_lines(lines, start + 1, base_indent)

    first_indent = _get_indent(first_line)

    # Sequence detection: a line starting with '- '
    if stripped.startswith("- "):
        return _parse_sequence(lines, start, first_indent)

    # Mapping detection: a line containing ': '
    if ": " in stripped or stripped.endswith(":"):
        return _parse_mapping(lines, start, first_indent)

    # Scalar value
    return _parse_scalar(stripped), start + 1


def _parse_sequence(
    lines: List[str], start: int, base_indent: int
) -> tuple:
    """Parse a YAML sequence (list) starting at *start*."""
    result: List[Any] = []
    i = start

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = _get_indent(line)

        # End of sequence if indentation decreases
        if indent < base_indent:
            break

        if indent == base_indent and stripped.startswith("- "):
            # List item
            item_value = stripped[2:].strip()

            if not item_value:
                # Could be a nested structure on next lines
                i += 1
                if i < len(lines):
                    next_indent = _get_indent(lines[i])
                    if next_indent > base_indent:
                        nested, i = _parse_yaml_lines(lines, i, next_indent)
                        result.append(nested)
                        continue
                result.append(None)
            elif ": " in item_value or item_value.endswith(":"):
                # Inline mapping start - collect all continuation lines
                # that belong to this list item
                item_indent = indent + 2  # content after '- '
                i += 1
                # Collect subsequent lines that are indented deeper than base_indent
                cont_lines = ["  " + item_value]
                while i < len(lines):
                    cl = lines[i]
                    cl_stripped = cl.strip()
                    if not cl_stripped or cl_stripped.startswith("#"):
                        i += 1
                        continue
                    cl_indent = _get_indent(cl)
                    if cl_indent > base_indent:
                        # Re-indent relative to the mapping level
                        cont_lines.append("  " + cl_stripped)
                        i += 1
                    else:
                        break
                nested, _ = _parse_yaml_lines(cont_lines, 0, 2)
                result.append(nested)
            elif item_value.startswith("- "):
                # Inline sequence
                nested_text = "  " + item_value
                nested, _ = _parse_yaml_lines([nested_text], 0, 2)
                result.append(nested)
                i += 1
            else:
                scalar = _parse_scalar(_strip_inline_comment(item_value))
                result.append(scalar)
                i += 1
        elif indent > base_indent:
            # Continuation of previous item (shouldn't normally happen here)
            i += 1
        else:
            break

    return result, i


def _parse_mapping(
    lines: List[str], start: int, base_indent: int
) -> tuple:
    """Parse a YAML mapping (dict) starting at *start*."""
    result: Dict[str, Any] = {}
    i = start

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        indent = _get_indent(line)

        # End of mapping if indentation decreases
        if indent < base_indent:
            break

        if indent == base_indent:
            # Check if this is a mapping entry
            if ": " in stripped:
                colon_pos = stripped.index(": ")
                key = stripped[:colon_pos].strip()
                value_str = stripped[colon_pos + 2:].strip()
            elif stripped.endswith(":"):
                key = stripped[:-1].strip()
                value_str = ""
            else:
                break

            # Remove surrounding quotes from key
            key = _strip_quotes(key)

            # Strip inline comment from value
            value_str = _strip_inline_comment(value_str)

            if not value_str:
                # Value is on subsequent lines
                i += 1
                if i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.strip()
                    next_indent = _get_indent(next_line)

                    if next_indent > base_indent:
                        # Nested structure
                        nested, i = _parse_yaml_lines(lines, i, next_indent)
                        result[key] = nested
                        continue
                    elif next_stripped.startswith("|") or next_stripped.startswith(">"):
                        # Multi-line string
                        multiline, i = _parse_multiline_string(lines, i, next_indent)
                        result[key] = multiline
                        continue

                result[key] = None
            elif value_str.startswith("|") or value_str.startswith(">"):
                # Multi-line string indicator on same line
                i += 1
                if i < len(lines):
                    multiline, i = _parse_multiline_string(lines, i, base_indent + 2)
                    result[key] = multiline
                    continue
                result[key] = ""
            elif value_str.startswith("- "):
                # Inline sequence start
                nested_text = "  " + value_str
                # Collect continuation lines at higher indent
                i += 1
                cont_lines = [nested_text]
                while i < len(lines):
                    cl = lines[i]
                    if _get_indent(cl) > base_indent and cl.strip():
                        cont_lines.append("  " + cl.strip())
                        i += 1
                    else:
                        break
                nested, _ = _parse_yaml_lines(cont_lines, 0, 2)
                result[key] = nested
            elif ": " in value_str or value_str.endswith(":"):
                # Inline nested mapping
                nested_text = "  " + value_str
                nested, _ = _parse_yaml_lines([nested_text], 0, 2)
                result[key] = nested
                i += 1
            else:
                result[key] = _parse_scalar(value_str)
                i += 1
        else:
            # Indentation is deeper than expected; skip
            i += 1

    return result, i


def _parse_multiline_string(
    lines: List[str], start: int, base_indent: int
) -> tuple:
    """Parse a multi-line YAML string block (| or >)."""
    text_lines: List[str] = []
    i = start

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            text_lines.append("")
            i += 1
            continue

        indent = _get_indent(line)
        if indent < base_indent:
            break

        # Remove the base indentation
        text_lines.append(line[base_indent:] if len(line) >= base_indent else line.lstrip())
        i += 1

    # Remove trailing empty lines
    while text_lines and not text_lines[-1]:
        text_lines.pop()

    return "\n".join(text_lines), i


def _parse_scalar(value: str) -> Any:
    """Parse a YAML scalar value into the appropriate Python type."""
    if not value:
        return ""

    # Remove surrounding quotes
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    # Boolean
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False

    # Null
    if value.lower() in ("null", "~", ""):
        return None

    # Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Float
    try:
        return float(value)
    except ValueError:
        pass

    return value


def _strip_quotes(s: str) -> str:
    """Remove surrounding quotes from a string if present."""
    if len(s) >= 2:
        if (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"):
            return s[1:-1]
    return s


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------

class ProgressBar:
    """A simple terminal progress bar.

    Args:
        total: Total number of steps.
        prefix: Text prefix shown before the bar.
        width: Character width of the progress bar itself.
        fill_char: Character used to fill the progress portion.
        empty_char: Character used for the empty portion.
    """

    def __init__(
        self,
        total: int,
        prefix: str = "",
        width: int = 40,
        fill_char: str = "=",
        empty_char: str = "-",
    ) -> None:
        self.total = total
        self.prefix = prefix
        self.width = width
        self.fill_char = fill_char
        self.empty_char = empty_char
        self._current = 0
        self._start_time = time.time()

    def update(self, step: int = 1) -> None:
        """Advance the progress bar by *step* increments."""
        self._current += step
        if self._current > self.total:
            self._current = self.total
        self._render()

    def set(self, value: int) -> None:
        """Set the progress bar to an absolute *value*."""
        self._current = min(value, self.total)
        self._render()

    def _render(self) -> None:
        """Render the progress bar to stderr."""
        if self.total <= 0:
            return
        ratio = self._current / self.total
        filled = int(self.width * ratio)
        bar = self.fill_char * filled + self.empty_char * (self.width - filled)
        elapsed = time.time() - self._start_time
        sys.stderr.write(
            f"\r{self.prefix} [{bar}] {self._current}/{self.total} "
            f"({elapsed:.1f}s)"
        )
        sys.stderr.flush()

    def finish(self) -> None:
        """Complete the progress bar and print a newline."""
        self._current = self.total
        self._render()
        sys.stderr.write("\n")
        sys.stderr.flush()


# ---------------------------------------------------------------------------
# Miscellaneous helpers
# ---------------------------------------------------------------------------

def truncate(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to *max_length* characters, appending *suffix* if truncated.

    Args:
        text: The input text.
        max_length: Maximum allowed length.
        suffix: Suffix to append when truncated.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def count_words(text: str) -> int:
    """Count the number of words in a text string.

    Args:
        text: The input text.

    Returns:
        Word count.
    """
    return len(text.split())
