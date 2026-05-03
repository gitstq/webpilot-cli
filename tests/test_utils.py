"""Unit tests for the utility functions module."""

import sys
import os
import unittest

# Add parent directory to path so we can import webpilot
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from webpilot.utils import (
    validate_url,
    normalize_url,
    extract_domain,
    ensure_dir,
    safe_filename,
    get_file_extension,
    parse_yaml,
    truncate,
    count_words,
    ProgressBar,
)


class TestValidateUrl(unittest.TestCase):
    """Tests for URL validation."""

    def test_valid_http_url(self) -> None:
        self.assertTrue(validate_url("http://example.com"))

    def test_valid_https_url(self) -> None:
        self.assertTrue(validate_url("https://example.com"))

    def test_valid_url_with_path(self) -> None:
        self.assertTrue(validate_url("https://example.com/path/to/page"))

    def test_valid_url_with_port(self) -> None:
        self.assertTrue(validate_url("https://example.com:8080"))

    def test_valid_url_with_query(self) -> None:
        self.assertTrue(validate_url("https://example.com?q=test"))

    def test_valid_ip_url(self) -> None:
        self.assertTrue(validate_url("http://192.168.1.1"))

    def test_invalid_no_scheme(self) -> None:
        self.assertFalse(validate_url("example.com"))

    def test_invalid_ftp_scheme(self) -> None:
        self.assertFalse(validate_url("ftp://example.com"))

    def test_invalid_empty(self) -> None:
        self.assertFalse(validate_url(""))

    def test_invalid_spaces(self) -> None:
        self.assertFalse(validate_url("https://example.com/path with spaces"))


class TestNormalizeUrl(unittest.TestCase):
    """Tests for URL normalization."""

    def test_add_https_scheme(self) -> None:
        self.assertEqual(normalize_url("example.com"), "https://example.com")

    def test_keep_existing_scheme(self) -> None:
        self.assertEqual(normalize_url("http://example.com"), "http://example.com")

    def test_strip_whitespace(self) -> None:
        self.assertEqual(normalize_url("  https://example.com  "), "https://example.com")

    def test_remove_fragment(self) -> None:
        self.assertEqual(
            normalize_url("https://example.com/page#section"),
            "https://example.com/page",
        )


class TestExtractDomain(unittest.TestCase):
    """Tests for domain extraction."""

    def test_simple_domain(self) -> None:
        self.assertEqual(extract_domain("https://example.com"), "example.com")

    def test_domain_with_path(self) -> None:
        self.assertEqual(extract_domain("https://example.com/path"), "example.com")

    def test_domain_with_port(self) -> None:
        self.assertEqual(extract_domain("https://example.com:8080"), "example.com:8080")

    def test_no_scheme_returns_input(self) -> None:
        self.assertEqual(extract_domain("example.com"), "example.com")


class TestSafeFilename(unittest.TestCase):
    """Tests for safe filename generation."""

    def test_replace_invalid_chars(self) -> None:
        result = safe_filename('file<>:"/\\|?*name')
        self.assertNotIn("<", result)
        self.assertNotIn(">", result)
        self.assertNotIn(":", result)

    def test_truncate_long_names(self) -> None:
        result = safe_filename("a" * 300, max_length=50)
        self.assertLessEqual(len(result), 50)

    def test_empty_string_fallback(self) -> None:
        result = safe_filename("")
        self.assertEqual(result, "unnamed")

    def test_strip_dots(self) -> None:
        result = safe_filename("...hidden...")
        self.assertFalse(result.startswith("."))
        self.assertFalse(result.endswith("."))


class TestGetFileExtension(unittest.TestCase):
    """Tests for file extension extraction from URLs."""

    def test_html_extension(self) -> None:
        self.assertEqual(get_file_extension("https://example.com/page.html"), ".html")

    def test_jpg_extension(self) -> None:
        self.assertEqual(get_file_extension("https://example.com/photo.jpg"), ".jpg")

    def test_no_extension_default(self) -> None:
        self.assertEqual(get_file_extension("https://example.com/page"), ".html")

    def test_query_string_ignored(self) -> None:
        self.assertEqual(get_file_extension("https://example.com/page.html?q=1"), ".html")

    def test_unknown_extension_default(self) -> None:
        self.assertEqual(get_file_extension("https://example.com/file.xyz"), ".html")


class TestParseYaml(unittest.TestCase):
    """Tests for the simple YAML parser."""

    def test_empty_yaml(self) -> None:
        result = parse_yaml("")
        self.assertEqual(result, {})

    def test_simple_mapping(self) -> None:
        yaml_text = "name: hello\nvalue: 42"
        result = parse_yaml(yaml_text)
        self.assertEqual(result["name"], "hello")
        self.assertEqual(result["value"], 42)

    def test_string_values(self) -> None:
        yaml_text = 'title: "My Title"\nauthor: John'
        result = parse_yaml(yaml_text)
        self.assertEqual(result["title"], "My Title")
        self.assertEqual(result["author"], "John")

    def test_boolean_values(self) -> None:
        yaml_text = "enabled: true\ndisabled: false"
        result = parse_yaml(yaml_text)
        self.assertTrue(result["enabled"])
        self.assertFalse(result["disabled"])

    def test_null_values(self) -> None:
        yaml_text = "value: null\nother: ~"
        result = parse_yaml(yaml_text)
        self.assertIsNone(result["value"])
        self.assertIsNone(result["other"])

    def test_simple_list(self) -> None:
        yaml_text = "- item1\n- item2\n- item3"
        result = parse_yaml(yaml_text)
        self.assertEqual(result, ["item1", "item2", "item3"])

    def test_nested_mapping(self) -> None:
        yaml_text = "server:\n  host: localhost\n  port: 8080"
        result = parse_yaml(yaml_text)
        self.assertEqual(result["server"]["host"], "localhost")
        self.assertEqual(result["server"]["port"], 8080)

    def test_list_of_mappings(self) -> None:
        yaml_text = "items:\n  - name: a\n    value: 1\n  - name: b\n    value: 2"
        result = parse_yaml(yaml_text)
        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["items"][0]["name"], "a")
        self.assertEqual(result["items"][1]["value"], 2)

    def test_multiline_string(self) -> None:
        yaml_text = "description: |\n  Line one\n  Line two\n  Line three"
        result = parse_yaml(yaml_text)
        self.assertIn("Line one", result["description"])
        self.assertIn("Line two", result["description"])
        self.assertIn("Line three", result["description"])

    def test_comments_ignored(self) -> None:
        yaml_text = "# This is a comment\nname: test  # inline comment\nvalue: 123"
        result = parse_yaml(yaml_text)
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["value"], 123)

    def test_numeric_values(self) -> None:
        yaml_text = "integer: 42\nfloat: 3.14\nnegative: -10"
        result = parse_yaml(yaml_text)
        self.assertEqual(result["integer"], 42)
        self.assertEqual(result["float"], 3.14)
        self.assertEqual(result["negative"], -10)

    def test_workflow_style_yaml(self) -> None:
        """Test parsing a workflow-style YAML document."""
        yaml_text = """name: test_workflow
vars:
  url: "https://example.com"
  count: 3
stop_on_error: true
steps:
  - name: "Navigate"
    type: navigate
    url: "${url}"
  - name: "Wait"
    type: wait
    seconds: 1"""
        result = parse_yaml(yaml_text)
        self.assertEqual(result["name"], "test_workflow")
        self.assertEqual(result["vars"]["url"], "https://example.com")
        self.assertEqual(result["vars"]["count"], 3)
        self.assertTrue(result["stop_on_error"])
        self.assertEqual(len(result["steps"]), 2)
        self.assertEqual(result["steps"][0]["name"], "Navigate")
        self.assertEqual(result["steps"][0]["type"], "navigate")


class TestTruncate(unittest.TestCase):
    """Tests for the truncate utility."""

    def test_short_text_unchanged(self) -> None:
        self.assertEqual(truncate("hello", 10), "hello")

    def test_long_text_truncated(self) -> None:
        result = truncate("a" * 100, 10)
        self.assertEqual(len(result), 10)
        self.assertTrue(result.endswith("..."))

    def test_custom_suffix(self) -> None:
        result = truncate("a" * 100, 10, suffix="!")
        self.assertTrue(result.endswith("!"))


class TestCountWords(unittest.TestCase):
    """Tests for the count_words utility."""

    def test_single_word(self) -> None:
        self.assertEqual(count_words("hello"), 1)

    def test_multiple_words(self) -> None:
        self.assertEqual(count_words("hello world foo"), 3)

    def test_empty_string(self) -> None:
        self.assertEqual(count_words(""), 0)


if __name__ == "__main__":
    unittest.main()
