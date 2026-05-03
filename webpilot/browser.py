"""
Browser automation engine for WebPilot-CLI.

Uses only the Python standard library (urllib) for HTTP requests and
html.parser for HTML parsing.  Provides:
  - HTTP GET with User-Agent spoofing, timeout, and retry
  - Cookie / session management
  - ASCII-art screenshot generation (terminal-friendly)
  - HTML Canvas screenshot (saved as an .html file)
"""

import http.cookiejar
import json
import os
import re
import socket
import ssl
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple

from .utils import ProgressBar, ensure_dir, normalize_url, safe_filename


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


# ---------------------------------------------------------------------------
# Cookie / session manager
# ---------------------------------------------------------------------------

class SessionManager:
    """Manages cookies and HTTP headers across requests."""

    def __init__(self, user_agent: str = DEFAULT_USER_AGENT) -> None:
        self.cookie_jar = http.cookiejar.CookieJar()
        self.user_agent = user_agent
        self.extra_headers: Dict[str, str] = {}

    def get_opener(self) -> urllib.request.OpenerDirector:
        """Build an OpenerDirector with cookie support."""
        handler = urllib.request.HTTPCookieProcessor(self.cookie_jar)
        opener = urllib.request.build_opener(handler)
        return opener

    def add_header(self, key: str, value: str) -> None:
        """Add a persistent extra header for all requests."""
        self.extra_headers[key] = value

    def get_cookies(self) -> List[Dict[str, str]]:
        """Return current cookies as a list of dicts."""
        cookies = []
        for cookie in self.cookie_jar:
            cookies.append({
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
            })
        return cookies


# ---------------------------------------------------------------------------
# HTML page structure parser (for ASCII screenshot)
# ---------------------------------------------------------------------------

class PageStructureParser(HTMLParser):
    """Parse HTML to extract a simplified text-based structure.

    Used to generate ASCII-art "screenshots" that represent the
    visual layout of a web page in the terminal.
    """

    # Tags whose content we want to capture
    CAPTURE_TAGS = {"title", "h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th", "a", "span", "div", "button", "label", "input"}
    # Tags that represent structural blocks
    BLOCK_TAGS = {"div", "section", "article", "main", "header", "footer", "nav", "aside", "table", "ul", "ol", "form"}
    # Tags to skip entirely (noise)
    SKIP_TAGS = {"script", "style", "noscript", "meta", "link", "svg", "path"}

    def __init__(self, width: int = 80) -> None:
        super().__init__()
        self.width = width
        self.lines: List[str] = []
        self._capture_depth = 0
        self._skip_depth = 0
        self._current_text = ""
        self._in_title = False
        self._tag_stack: List[str] = []
        self._block_indent = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag_lower = tag.lower()
        self._tag_stack.append(tag_lower)

        if tag_lower in self.SKIP_TAGS:
            self._skip_depth += 1
            return

        if tag_lower in self.BLOCK_TAGS:
            self._flush_text()
            self._block_indent += 1

        if tag_lower in self.CAPTURE_TAGS:
            self._capture_depth += 1

        if tag_lower == "title":
            self._in_title = True

        # Handle self-closing / void elements
        if tag_lower in ("br", "hr", "img", "input"):
            self._flush_text()
            if tag_lower == "hr":
                self.lines.append(" " + "-" * (self.width - 4))
            elif tag_lower == "br":
                self.lines.append("")

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if self._tag_stack and self._tag_stack[-1] == tag_lower:
            self._tag_stack.pop()

        if tag_lower in self.SKIP_TAGS:
            if self._skip_depth > 0:
                self._skip_depth -= 1
            return

        if tag_lower in self.CAPTURE_TAGS:
            if self._capture_depth > 0:
                self._capture_depth -= 1

        if tag_lower == "title":
            self._in_title = False

        if tag_lower in self.BLOCK_TAGS:
            self._flush_text()
            if self._block_indent > 0:
                self._block_indent -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._capture_depth > 0 or self._in_title:
            self._current_text += data.strip() + " "

    def handle_entityref(self, name: str) -> None:
        """Handle HTML entities like &amp; &lt; etc."""
        entities = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'", "nbsp": " "}
        self._current_text += entities.get(name, f"&{name};") + " "

    def handle_charref(self, name: str) -> None:
        """Handle numeric character references."""
        try:
            if name.startswith("x"):
                char = chr(int(name[1:], 16))
            else:
                char = chr(int(name))
            self._current_text += char + " "
        except (ValueError, OverflowError):
            pass

    def _flush_text(self) -> None:
        """Flush accumulated text into the lines list."""
        text = self._current_text.strip()
        if text:
            # Word-wrap the text
            indent = "  " * self._block_indent
            available = self.width - len(indent) - 2
            if available < 20:
                available = 20
            words = text.split()
            line = indent
            for word in words:
                if len(line) + len(word) + 1 > self.width - 1:
                    self.lines.append(line)
                    line = indent
                line += word + " "
            if line.strip():
                self.lines.append(line)
        self._current_text = ""

    def get_text(self) -> str:
        """Return the full extracted text."""
        self._flush_text()
        return "\n".join(self.lines)


# ---------------------------------------------------------------------------
# Main browser engine
# ---------------------------------------------------------------------------

class Browser:
    """Lightweight browser automation engine built on urllib.

    Args:
        user_agent: Custom User-Agent string.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retry attempts.
        retry_delay: Delay between retries in seconds.
    """

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        retry_delay: int = RETRY_DELAY,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = SessionManager(user_agent)
        self._last_url: str = ""
        self._last_html: str = ""
        self._history: List[str] = []

    def fetch(self, url: str, method: str = "GET", data: Optional[bytes] = None) -> str:
        """Fetch a URL and return the response body as text.

        Args:
            url: The URL to fetch.
            method: HTTP method (GET or POST).
            data: Optional request body bytes.

        Returns:
            The response body decoded as UTF-8.

        Raises:
            urllib.error.URLError: If the request fails after all retries.
        """
        url = normalize_url(url)
        self._last_url = url

        # Build request
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("User-Agent", self.user_agent)
        req.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
        req.add_header("Accept-Language", "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7")

        # Add extra session headers
        for key, value in self.session.extra_headers.items():
            req.add_header(key, value)

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                opener = self.session.get_opener()
                # Use a custom SSL context that doesn't verify certs
                # (for compatibility in restricted environments)
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                https_handler = urllib.request.HTTPSHandler(context=ctx)
                opener = urllib.request.build_opener(
                    urllib.request.HTTPCookieProcessor(self.session.cookie_jar),
                    https_handler,
                )

                with opener.open(req, timeout=self.timeout) as resp:
                    content = resp.read()
                    # Try to detect encoding
                    encoding = "utf-8"
                    content_type = resp.headers.get("Content-Type", "")
                    charset_match = re.search(r"charset=([\w-]+)", content_type)
                    if charset_match:
                        encoding = charset_match.group(1)

                    try:
                        html = content.decode(encoding)
                    except (UnicodeDecodeError, LookupError):
                        html = content.decode("utf-8", errors="replace")

                    self._last_html = html
                    self._history.append(url)
                    return html

            except urllib.error.HTTPError as e:
                last_error = e
                # Don't retry 4xx client errors (except 429)
                if 400 <= e.code < 500 and e.code != 429:
                    raise
            except (urllib.error.URLError, socket.timeout, OSError) as e:
                last_error = e

            if attempt < self.max_retries - 1:
                import time
                time.sleep(self.retry_delay * (attempt + 1))

        raise last_error  # type: ignore

    def get_page_info(self) -> Dict[str, Any]:
        """Return basic information about the last fetched page.

        Returns:
            Dict with keys: url, title, content_length, etc.
        """
        title = ""
        if self._last_html:
            # Quick title extraction
            match = re.search(r"<title[^>]*>(.*?)</title>", self._last_html, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()

        return {
            "url": self._last_url,
            "title": title,
            "content_length": len(self._last_html),
            "history_count": len(self._history),
        }

    def ascii_screenshot(self, width: int = 80, max_lines: int = 40) -> str:
        """Generate an ASCII-art representation of the last fetched page.

        Args:
            width: Terminal width in characters.
            max_lines: Maximum number of lines to output.

        Returns:
            ASCII-art string representing the page layout.
        """
        if not self._last_html:
            return "(no page loaded)"

        parser = PageStructureParser(width=width)
        try:
            parser.feed(self._last_html)
        except Exception:
            pass

        text = parser.get_text()
        lines = text.split("\n")

        # Build a bordered box
        border = "+" + "-" * (width - 2) + "+"
        result = [border]

        # Title bar
        title = self.get_page_info().get("title", "Untitled")
        title_line = f"| {title[:width - 4]:^{width - 4}} |"
        result.append(title_line)
        result.append("+" + "=" * (width - 2) + "+")

        # Content
        for line in lines[:max_lines]:
            # Pad or truncate to fit width
            if len(line) > width - 3:
                line = line[: width - 4] + "..."
            padded = line.ljust(width - 3)
            result.append(f"| {padded} |")

        if len(lines) > max_lines:
            result.append(f"| {'... (truncated)':^{width - 4}} |")

        result.append(border)
        return "\n".join(result)

    def html_screenshot(self, output_path: str, width: int = 1280) -> str:
        """Generate an HTML file that renders a simplified visual screenshot.

        This creates a standalone HTML file with a canvas-based rendering
        of the page structure.

        Args:
            output_path: Path to save the HTML screenshot file.
            width: Viewport width in pixels.

        Returns:
            The path to the saved HTML file.
        """
        if not self._last_html:
            raise RuntimeError("No page loaded. Call fetch() first.")

        output_path = ensure_dir(output_path)

        # Extract page content
        parser = PageStructureParser(width=100)
        try:
            parser.feed(self._last_html)
        except Exception:
            pass

        text = parser.get_text()
        title = self.get_page_info().get("title", "Untitled")
        url = self._last_url

        # Escape HTML special characters
        text_escaped = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Screenshot: {title}</title>
<style>
  body {{
    margin: 0; padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #1a1a2e; color: #e0e0e0;
  }}
  .browser-frame {{
    border: 2px solid #444; border-radius: 8px; overflow: hidden;
    max-width: {width}px; margin: 0 auto;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }}
  .title-bar {{
    background: #2d2d44; padding: 10px 16px;
    display: flex; align-items: center; gap: 8px;
  }}
  .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
  .dot.red {{ background: #ff5f57; }}
  .dot.yellow {{ background: #febc2e; }}
  .dot.green {{ background: #28c840; }}
  .url-bar {{
    flex: 1; background: #1a1a2e; border: 1px solid #555;
    border-radius: 4px; padding: 6px 12px; margin-left: 8px;
    color: #aaa; font-size: 13px;
  }}
  .content {{
    background: #fff; color: #333; padding: 20px;
    min-height: 400px; font-size: 14px; line-height: 1.6;
    white-space: pre-wrap; word-wrap: break-word;
  }}
  .meta {{
    text-align: center; color: #888; font-size: 12px;
    margin-top: 16px;
  }}
</style>
</head>
<body>
<div class="browser-frame">
  <div class="title-bar">
    <span class="dot red"></span>
    <span class="dot yellow"></span>
    <span class="dot green"></span>
    <div class="url-bar">{url}</div>
  </div>
  <div class="content">{text_escaped}</div>
</div>
<div class="meta">
  Generated by WebPilot-CLI | {title} | {url}
</div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

    def save_screenshot(
        self,
        url: str,
        output_path: str,
        screenshot_type: str = "ascii",
    ) -> str:
        """Fetch a URL and save a screenshot.

        Args:
            url: The URL to screenshot.
            output_path: Path to save the screenshot.
            screenshot_type: 'ascii' for text-based, 'html' for HTML file.

        Returns:
            The path to the saved screenshot.
        """
        self.fetch(url)

        if screenshot_type == "html":
            return self.html_screenshot(output_path)
        else:
            ascii_art = self.ascii_screenshot()
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(ascii_art)
            return output_path
