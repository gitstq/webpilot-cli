"""Unit tests for the content extractor module."""

import sys
import os
import unittest

# Add parent directory to path so we can import webpilot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from webpilot.extractor import extract_content, clean_text, ContentExtractor


class TestContentExtractor(unittest.TestCase):
    """Tests for the HTML content extractor."""

    def test_extract_title(self) -> None:
        """Test that the page title is extracted correctly."""
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        result = extract_content(html, "https://example.com")
        self.assertEqual(result["title"], "Test Page")

    def test_extract_meta_description(self) -> None:
        """Test that the meta description is extracted."""
        html = """
        <html><head>
            <meta name="description" content="A test description">
            <title>Test</title>
        </head><body><p>Hello world</p></body></html>
        """
        result = extract_content(html, "https://example.com")
        self.assertEqual(result["description"], "A test description")

    def test_extract_links(self) -> None:
        """Test that hyperlinks are extracted with absolute URLs."""
        html = """
        <html><head><title>Test</title></head>
        <body>
            <a href="/page1">Page 1</a>
            <a href="https://other.com/page2">Page 2</a>
            <a href="#anchor">Skip</a>
        </body></html>
        """
        result = extract_content(html, "https://example.com")
        links = result["links"]
        self.assertEqual(len(links), 3)
        self.assertEqual(links[0]["href"], "https://example.com/page1")
        self.assertEqual(links[0]["text"], "Page 1")
        self.assertEqual(links[1]["href"], "https://other.com/page2")
        self.assertEqual(links[2]["href"], "https://example.com#anchor")

    def test_extract_images(self) -> None:
        """Test that image URLs are extracted with absolute paths."""
        html = """
        <html><head><title>Test</title></head>
        <body>
            <img src="/images/logo.png" alt="Logo">
            <img src="https://cdn.example.com/photo.jpg" alt="Photo">
        </body></html>
        """
        result = extract_content(html, "https://example.com")
        images = result["images"]
        self.assertEqual(len(images), 2)
        self.assertEqual(images[0]["src"], "https://example.com/images/logo.png")
        self.assertEqual(images[0]["alt"], "Logo")
        self.assertEqual(images[1]["src"], "https://cdn.example.com/photo.jpg")

    def test_extract_text_blocks(self) -> None:
        """Test that meaningful text blocks are extracted."""
        html = """
        <html><head><title>Test</title></head>
        <body>
            <p>This is a paragraph with enough text to be extracted.</p>
            <p>Another paragraph here.</p>
        </body></html>
        """
        result = extract_content(html, "https://example.com")
        text_blocks = result["text"]
        self.assertTrue(len(text_blocks) > 0)
        # Check that the paragraph text is present
        all_text = " ".join(text_blocks)
        self.assertIn("paragraph", all_text)

    def test_skip_script_content(self) -> None:
        """Test that script and style content is not extracted as text."""
        html = """
        <html><head><title>Test</title></head>
        <body>
            <script>var x = 'should not appear';</script>
            <style>.hidden { display: none; }</style>
            <p>Visible content should appear here.</p>
        </body></html>
        """
        result = extract_content(html, "https://example.com")
        all_text = " ".join(result["text"])
        self.assertNotIn("should not appear", all_text)
        self.assertNotIn("display: none", all_text)

    def test_skip_navigation_noise(self) -> None:
        """Test that navigation elements are filtered out."""
        html = """
        <html><head><title>Test</title></head>
        <body>
            <nav id="main-nav">
                <a href="/home">Home</a>
                <a href="/about">About</a>
            </nav>
            <article>
                <p>This is the main article content that should be extracted properly.</p>
            </article>
            <footer id="footer">
                <p>Footer text that should be filtered out.</p>
            </footer>
        </body></html>
        """
        result = extract_content(html, "https://example.com")
        all_text = " ".join(result["text"])
        # Navigation and footer links should not appear in text blocks
        self.assertNotIn("Home", all_text)
        self.assertNotIn("About", all_text)

    def test_empty_html(self) -> None:
        """Test that empty HTML returns empty results."""
        result = extract_content("", "https://example.com")
        self.assertEqual(result["title"], "")
        self.assertEqual(result["description"], "")
        self.assertEqual(result["links"], [])
        self.assertEqual(result["images"], [])

    def test_extract_headings(self) -> None:
        """Test that headings are extracted with markdown markers."""
        html = """
        <html><head><title>Test</title></head>
        <body>
            <h1>Main Title</h1>
            <h2>Subtitle</h2>
            <p>Content under subtitle.</p>
        </body></html>
        """
        result = extract_content(html, "https://example.com")
        text_blocks = result["text"]
        all_text = "\n".join(text_blocks)
        self.assertIn("# Main Title", all_text)
        self.assertIn("## Subtitle", all_text)


class TestCleanText(unittest.TestCase):
    """Tests for the clean_text utility function."""

    def test_remove_extra_whitespace(self) -> None:
        """Test that excessive whitespace is cleaned."""
        text = "Hello    world\n\n\nGoodbye"
        result = clean_text(text)
        self.assertNotIn("    ", result)
        self.assertNotIn("\n\n\n", result)

    def test_remove_noise_patterns(self) -> None:
        """Test that common noise text is removed."""
        text = "Click here\nRead more\nActual content here"
        result = clean_text(text)
        self.assertNotIn("Click here", result)
        self.assertNotIn("Read more", result)
        self.assertIn("Actual content", result)


if __name__ == "__main__":
    unittest.main()
