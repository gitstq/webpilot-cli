"""
Output formatter for WebPilot-CLI.

Provides formatting utilities for JSON, Markdown, plain text, and
colored terminal output.
"""

import json
import sys
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# ANSI color codes
# ---------------------------------------------------------------------------

class Colors:
    """ANSI escape codes for terminal colors."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class NoColors:
    """Placeholder class when colors are disabled."""

    RESET = ""
    BOLD = ""
    DIM = ""
    UNDERLINE = ""
    BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
    BG_BLACK = BG_RED = BG_GREEN = BG_YELLOW = BG_BLUE = BG_MAGENTA = BG_CYAN = BG_WHITE = ""


# ---------------------------------------------------------------------------
# Formatter base
# ---------------------------------------------------------------------------

class Formatter:
    """Base output formatter.

    Args:
        use_color: Whether to use ANSI color codes.
    """

    def __init__(self, use_color: bool = True) -> None:
        self.use_color = use_color
        self.c = Colors() if use_color else NoColors()

    def format_extracted(self, data: Dict[str, Any]) -> str:
        """Format extracted content data.

        Args:
            data: Extracted content dict from ContentExtractor.

        Returns:
            Formatted string.
        """
        raise NotImplementedError

    def format_page_info(self, info: Dict[str, Any]) -> str:
        """Format page information.

        Args:
            info: Page info dict from Browser.

        Returns:
            Formatted string.
        """
        raise NotImplementedError

    def format_screenshot(self, ascii_art: str) -> str:
        """Format an ASCII screenshot.

        Args:
            ascii_art: The ASCII art string.

        Returns:
            Formatted string.
        """
        return ascii_art

    def format_workflow_result(self, result: Dict[str, Any]) -> str:
        """Format workflow execution result.

        Args:
            result: Workflow result dict.

        Returns:
            Formatted string.
        """
        raise NotImplementedError

    def format_error(self, message: str) -> str:
        """Format an error message.

        Args:
            message: The error message.

        Returns:
            Formatted error string.
        """
        return f"{self.c.RED}{self.c.BOLD}Error:{self.c.RESET} {message}"

    def format_success(self, message: str) -> str:
        """Format a success message.

        Args:
            message: The success message.

        Returns:
            Formatted success string.
        """
        return f"{self.c.GREEN}{self.c.BOLD}Success:{self.c.RESET} {message}"

    def format_info(self, message: str) -> str:
        """Format an informational message.

        Args:
            message: The info message.

        Returns:
            Formatted info string.
        """
        return f"{self.c.CYAN}Info:{self.c.RESET} {message}"

    def format_warning(self, message: str) -> str:
        """Format a warning message.

        Args:
            message: The warning message.

        Returns:
            Formatted warning string.
        """
        return f"{self.c.YELLOW}{self.c.BOLD}Warning:{self.c.RESET} {message}"


# ---------------------------------------------------------------------------
# JSON formatter
# ---------------------------------------------------------------------------

class JsonFormatter(Formatter):
    """Output formatter that produces JSON."""

    def format_extracted(self, data: Dict[str, Any]) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2)

    def format_page_info(self, info: Dict[str, Any]) -> str:
        return json.dumps(info, ensure_ascii=False, indent=2)

    def format_workflow_result(self, result: Dict[str, Any]) -> str:
        return json.dumps(result, ensure_ascii=False, indent=2)

    def format_error(self, message: str) -> str:
        return json.dumps({"error": message}, ensure_ascii=False, indent=2)

    def format_success(self, message: str) -> str:
        return json.dumps({"success": message}, ensure_ascii=False, indent=2)

    def format_info(self, message: str) -> str:
        return json.dumps({"info": message}, ensure_ascii=False, indent=2)

    def format_warning(self, message: str) -> str:
        return json.dumps({"warning": message}, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Markdown formatter
# ---------------------------------------------------------------------------

class MarkdownFormatter(Formatter):
    """Output formatter that produces Markdown."""

    def format_extracted(self, data: Dict[str, Any]) -> str:
        lines: List[str] = []

        # Title
        title = data.get("title", "Untitled")
        lines.append(f"# {title}")
        lines.append("")

        # Description
        desc = data.get("description", "")
        if desc:
            lines.append(f"> {desc}")
            lines.append("")

        # Main text
        text_blocks = data.get("text", [])
        if text_blocks:
            lines.append("## Content")
            lines.append("")
            for block in text_blocks:
                # Check if it's a heading (starts with #)
                if block.startswith("#"):
                    lines.append(block)
                else:
                    lines.append(block)
                lines.append("")

        # Links
        links = data.get("links", [])
        if links:
            lines.append("## Links")
            lines.append("")
            lines.append("| # | Text | URL |")
            lines.append("|---|------|-----|")
            for i, link in enumerate(links, 1):
                text = link.get("text", "")[:50]
                href = link.get("href", "")
                lines.append(f"| {i} | {text} | {href} |")
            lines.append("")

        # Images
        images = data.get("images", [])
        if images:
            lines.append("## Images")
            lines.append("")
            lines.append("| # | Alt Text | URL |")
            lines.append("|---|----------|-----|")
            for i, img in enumerate(images, 1):
                alt = img.get("alt", "")[:50]
                src = img.get("src", "")
                lines.append(f"| {i} | {alt} | {src} |")
            lines.append("")

        return "\n".join(lines)

    def format_page_info(self, info: Dict[str, Any]) -> str:
        lines = [
            f"## Page Info",
            "",
            f"- **URL:** {info.get('url', 'N/A')}",
            f"- **Title:** {info.get('title', 'N/A')}",
            f"- **Content Length:** {info.get('content_length', 0):,} bytes",
            f"- **History Count:** {info.get('history_count', 0)}",
        ]
        return "\n".join(lines)

    def format_workflow_result(self, result: Dict[str, Any]) -> str:
        lines = ["## Workflow Result", ""]

        status = result.get("status", "unknown")
        status_icon = "completed" if status == "success" else "failed"
        lines.append(f"**Status:** {status_icon}")
        lines.append("")

        steps = result.get("steps", [])
        if steps:
            lines.append("### Steps")
            lines.append("")
            for i, step in enumerate(steps, 1):
                name = step.get("name", f"Step {i}")
                step_status = step.get("status", "unknown")
                lines.append(f"**{i}. {name}** - `{step_status}`")
                output = step.get("output")
                if output:
                    lines.append(f"   ```")
                    lines.append(f"   {str(output)[:200]}")
                    lines.append(f"   ```")
                lines.append("")

        variables = result.get("variables", {})
        if variables:
            lines.append("### Variables")
            lines.append("")
            lines.append("| Variable | Value |")
            lines.append("|----------|-------|")
            for key, value in variables.items():
                lines.append(f"| {key} | {str(value)[:100]} |")
            lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Plain text formatter
# ---------------------------------------------------------------------------

class TextFormatter(Formatter):
    """Output formatter that produces plain text."""

    def format_extracted(self, data: Dict[str, Any]) -> str:
        lines: List[str] = []

        title = data.get("title", "Untitled")
        lines.append(f"Title: {title}")
        lines.append("")

        desc = data.get("description", "")
        if desc:
            lines.append(f"Description: {desc}")
            lines.append("")

        text_blocks = data.get("text", [])
        if text_blocks:
            lines.append("--- Content ---")
            for block in text_blocks:
                lines.append(block)
            lines.append("")

        links = data.get("links", [])
        if links:
            lines.append("--- Links ---")
            for i, link in enumerate(links, 1):
                text = link.get("text", "")
                href = link.get("href", "")
                lines.append(f"  {i}. [{text}] {href}")
            lines.append("")

        images = data.get("images", [])
        if images:
            lines.append("--- Images ---")
            for i, img in enumerate(images, 1):
                alt = img.get("alt", "")
                src = img.get("src", "")
                lines.append(f"  {i}. {alt} -> {src}")
            lines.append("")

        return "\n".join(lines)

    def format_page_info(self, info: Dict[str, Any]) -> str:
        lines = [
            "Page Info",
            "=" * 40,
            f"  URL:            {info.get('url', 'N/A')}",
            f"  Title:          {info.get('title', 'N/A')}",
            f"  Content Length: {info.get('content_length', 0):,} bytes",
            f"  History Count:  {info.get('history_count', 0)}",
        ]
        return "\n".join(lines)

    def format_workflow_result(self, result: Dict[str, Any]) -> str:
        lines = [
            "Workflow Result",
            "=" * 40,
            f"  Status: {result.get('status', 'unknown')}",
            "",
        ]

        steps = result.get("steps", [])
        if steps:
            lines.append("  Steps:")
            for i, step in enumerate(steps, 1):
                name = step.get("name", f"Step {i}")
                step_status = step.get("status", "unknown")
                lines.append(f"    {i}. {name} - {step_status}")
            lines.append("")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Formatter factory
# ---------------------------------------------------------------------------

def get_formatter(
    output_format: str = "markdown",
    use_color: bool = True,
) -> Formatter:
    """Create a formatter instance based on the desired output format.

    Args:
        output_format: One of 'json', 'markdown', 'text'.
        use_color: Whether to enable colored output (ignored for JSON).

    Returns:
        A Formatter subclass instance.
    """
    formatters = {
        "json": JsonFormatter,
        "markdown": MarkdownFormatter,
        "text": TextFormatter,
    }

    cls = formatters.get(output_format.lower(), MarkdownFormatter)
    # JSON formatter doesn't need colors
    color = use_color if output_format.lower() != "json" else False
    return cls(use_color=color)
