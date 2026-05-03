"""
Intelligent content extractor for WebPilot-CLI.

Extracts structured content from HTML pages including:
  - Page title and meta description
  - Main body text (with noise removal)
  - All hyperlinks
  - All image URLs

Outputs in JSON, Markdown, or plain text format.
"""

import re
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse


# ---------------------------------------------------------------------------
# Noise patterns (navigation, ads, footers, etc.)
# ---------------------------------------------------------------------------

NOISY_ROLES = {"navigation", "banner", "contentinfo", "complementary", "alert", "dialog"}
NOISY_IDS = re.compile(
    r"nav|sidebar|footer|header|menu|advert|social|cookie|popup|modal|overlay|banner|comment",
    re.IGNORECASE,
)
NOISY_CLASSES = NOISY_IDS  # Same patterns for class names


# ---------------------------------------------------------------------------
# HTML content extractor parser
# ---------------------------------------------------------------------------

class ContentExtractor(HTMLParser):
    """Parse HTML and extract structured content while filtering noise.

    Attributes:
        title: The page title.
        meta_description: The meta description content.
        links: List of (text, href) tuples.
        images: List of (alt, src) tuples.
        text_blocks: List of significant text blocks.
    """

    SKIP_TAGS = {"script", "style", "noscript", "svg", "math"}
    BLOCK_TAGS = {"p", "div", "section", "article", "main", "td", "li", "blockquote", "pre", "h1", "h2", "h3", "h4", "h5", "h6"}
    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
    HEAD_TAGS = {"head", "title", "meta", "link"}  # Tags inside <head> that we handle specially

    def __init__(self, base_url: str = "") -> None:
        super().__init__()
        self.base_url = base_url

        # Extracted data
        self.title: str = ""
        self.meta_description: str = ""
        self.links: List[Dict[str, str]] = []
        self.images: List[Dict[str, str]] = []
        self.text_blocks: List[str] = []

        # Internal state
        self._skip_depth: int = 0
        self._in_head: int = 0  # depth counter for <head> section
        self._in_title: bool = False
        self._in_meta: bool = False
        self._meta_name: str = ""
        self._current_text: str = ""
        self._current_tag: str = ""
        self._in_noisy: int = 0  # depth counter for noisy elements
        self._seen_links: set = set()  # deduplicate links
        self._heading_level: int = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag_lower = tag.lower()
        attrs_dict = {k.lower(): v for k, v in attrs if v is not None}

        # Track <head> section
        if tag_lower == "head":
            self._in_head += 1

        # Skip noise tags
        if tag_lower in self.SKIP_TAGS:
            self._skip_depth += 1
            return

        if self._skip_depth > 0:
            return

        # Handle <title> and <meta> even inside <head>
        if tag_lower == "title":
            self._in_title = True
            self._current_text = ""

        if tag_lower == "meta":
            name = attrs_dict.get("name", "").lower()
            if name == "description":
                self.meta_description = attrs_dict.get("content", "")

        # Skip all other processing if we're inside <head>
        if self._in_head > 0:
            return

        # Check for noisy containers (nav, sidebar, footer, etc.)
        role = attrs_dict.get("role", "")
        elem_id = attrs_dict.get("id", "")
        elem_class = attrs_dict.get("class", "")

        if role in NOISY_ROLES:
            self._in_noisy += 1
        elif NOISY_IDS.search(elem_id) or NOISY_CLASSES.search(elem_class):
            # Only count as noisy if the match is strong (word boundary)
            self._in_noisy += 1

        # Links
        if tag_lower == "a" and self._in_noisy == 0:
            href = attrs_dict.get("href", "")
            if href and href not in self._seen_links:
                self._seen_links.add(href)
                self._current_tag = "a"
                self._current_text = ""  # reset to capture link text
                self._current_attrs = attrs_dict  # type: ignore

        # Images
        if tag_lower == "img" and self._in_noisy == 0:
            src = attrs_dict.get("src", "")
            alt = attrs_dict.get("alt", "")
            if src:
                absolute_src = urljoin(self.base_url, src)
                self.images.append({"alt": alt, "src": absolute_src})

        # Headings
        if tag_lower in self.HEADING_TAGS:
            self._heading_level = int(tag_lower[1])

        # Block-level tag: flush accumulated text
        if tag_lower in self.BLOCK_TAGS and tag_lower not in self.HEADING_TAGS:
            self._flush_text()

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()

        # Track </head>
        if tag_lower == "head":
            if self._in_head > 0:
                self._in_head -= 1

        if tag_lower in self.SKIP_TAGS:
            if self._skip_depth > 0:
                self._skip_depth -= 1
            return

        if self._skip_depth > 0:
            return

        # Handle title end even inside <head>
        if tag_lower == "title" and self._in_title:
            self.title = self._current_text.strip()
            self._in_title = False
            self._current_text = ""

        # Skip all other processing if we're inside <head>
        if self._in_head > 0:
            return

        # Check for noisy container end
        if self._in_noisy > 0:
            # We decrement on any closing tag that could be a container
            if tag_lower in {"div", "nav", "section", "aside", "footer", "header", "ul", "ol", "form"}:
                self._in_noisy = max(0, self._in_noisy - 1)

        # Link end
        if tag_lower == "a" and self._current_tag == "a" and self._in_noisy == 0:
            link_text = self._current_text.strip()
            href = getattr(self, "_current_attrs", {}).get("href", "")
            if href:
                absolute_href = urljoin(self.base_url, href)
                self.links.append({"text": link_text, "href": absolute_href})
            self._current_tag = ""
            self._current_text = ""

        # Heading end
        if tag_lower in self.HEADING_TAGS:
            text = self._current_text.strip()
            if text:
                prefix = "#" * self._heading_level
                self.text_blocks.append(f"{prefix} {text}")
            self._heading_level = 0
            self._current_text = ""

        # Block-level tag end: flush
        if tag_lower in self.BLOCK_TAGS:
            self._flush_text()

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0 or self._in_noisy > 0:
            return
        self._current_text += data

    def handle_entityref(self, name: str) -> None:
        """Handle HTML entities."""
        entities = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'", "nbsp": " "}
        self._current_text += entities.get(name, f"&{name};")

    def handle_charref(self, name: str) -> None:
        """Handle numeric character references."""
        try:
            if name.startswith("x"):
                char = chr(int(name[1:], 16))
            else:
                char = chr(int(name))
            self._current_text += char
        except (ValueError, OverflowError):
            pass

    def _flush_text(self) -> None:
        """Flush accumulated text into text_blocks if significant."""
        text = self._current_text.strip()
        if text and len(text) > 10:  # Only keep blocks with meaningful content
            # Clean up whitespace
            text = re.sub(r"\s+", " ", text)
            self.text_blocks.append(text)
        self._current_text = ""

    def get_extracted(self) -> Dict[str, Any]:
        """Return all extracted data as a dictionary.

        Returns:
            Dict with keys: title, description, text, links, images.
        """
        self._flush_text()

        # Deduplicate text blocks
        seen_texts = set()
        unique_blocks = []
        for block in self.text_blocks:
            if block not in seen_texts:
                seen_texts.add(block)
                unique_blocks.append(block)

        return {
            "title": self.title,
            "description": self.meta_description,
            "text": unique_blocks,
            "links": self.links,
            "images": self.images,
        }


# ---------------------------------------------------------------------------
# Public extraction function
# ---------------------------------------------------------------------------

def extract_content(html: str, url: str = "") -> Dict[str, Any]:
    """Extract structured content from HTML.

    Args:
        html: The raw HTML string.
        url: The source URL (used for resolving relative links).

    Returns:
        A dict with title, description, text blocks, links, and images.
    """
    extractor = ContentExtractor(base_url=url)
    try:
        extractor.feed(html)
    except Exception:
        pass  # Best-effort extraction
    return extractor.get_extracted()


def clean_text(text: str) -> str:
    """Clean extracted text by removing excessive whitespace and noise.

    Args:
        text: The raw text string.

    Returns:
        Cleaned text.
    """
    # Remove excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove common noise patterns
    text = re.sub(r"^\s*(click here|read more|learn more)\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
    return text.strip()
