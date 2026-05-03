"""
CLI entry point for WebPilot-CLI.

Provides the main command-line interface with subcommands:
  browse     - Browse a webpage and extract content
  screenshot - Capture a webpage screenshot
  extract    - Extract structured content from a webpage
  run        - Execute a YAML workflow
  interactive - Start an interactive browser session
"""

import argparse
import os
import sys
from typing import List, Optional

from . import __version__
from .browser import Browser
from .extractor import extract_content
from .formatter import get_formatter
from .workflow import WorkflowEngine


# ---------------------------------------------------------------------------
# CLI argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands and global options.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="webpilot",
        description="WebPilot-CLI: Lightweight AI browser automation tool",
        epilog="Example: webpilot browse https://example.com --output json",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"WebPilot-CLI v{__version__}",
    )

    # Global options
    parser.add_argument(
        "--output", "-o",
        choices=["json", "markdown", "text"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        default=False,
        help="Enable verbose output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- browse subcommand ---
    browse_parser = subparsers.add_parser(
        "browse",
        help="Browse a webpage and display content",
    )
    browse_parser.add_argument("url", help="URL to browse")
    browse_parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    # --- screenshot subcommand ---
    screenshot_parser = subparsers.add_parser(
        "screenshot",
        help="Capture a webpage screenshot",
    )
    screenshot_parser.add_argument("url", help="URL to screenshot")
    screenshot_parser.add_argument(
        "--output-file", "-o",
        default="screenshot.html",
        help="Output file path (default: screenshot.html)",
    )
    screenshot_parser.add_argument(
        "--format", "-f",
        choices=["ascii", "html"],
        default="html",
        help="Screenshot format (default: html)",
    )
    screenshot_parser.add_argument(
        "--width",
        type=int,
        default=80,
        help="Terminal width for ASCII screenshots (default: 80)",
    )

    # --- extract subcommand ---
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract structured content from a webpage",
    )
    extract_parser.add_argument("url", help="URL to extract from")
    extract_parser.add_argument(
        "--fields",
        nargs="+",
        choices=["title", "description", "text", "links", "images"],
        default=None,
        help="Fields to extract (default: all)",
    )
    extract_parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    # --- run subcommand ---
    run_parser = subparsers.add_parser(
        "run",
        help="Execute a YAML workflow file",
    )
    run_parser.add_argument("workflow", help="Path to YAML workflow file")
    run_parser.add_argument(
        "--export", "-e",
        default=None,
        help="Export results to a file",
    )

    # --- interactive subcommand ---
    interactive_parser = subparsers.add_parser(
        "interactive",
        help="Start an interactive browser session",
    )
    interactive_parser.add_argument(
        "--url", "-u",
        default=None,
        help="Initial URL to navigate to",
    )

    return parser


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_browse(args: argparse.Namespace) -> int:
    """Handle the 'browse' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from .utils import validate_url, normalize_url

    url = normalize_url(args.url)
    if not validate_url(url):
        formatter = get_formatter(args.output, not args.no_color)
        print(formatter.format_error(f"Invalid URL: {url}"))
        return 1

    formatter = get_formatter(args.output, not args.no_color)
    browser = Browser(timeout=args.timeout, verbose=args.verbose)

    try:
        if args.verbose:
            print(formatter.format_info(f"Fetching {url}..."))

        html = browser.fetch(url)
        info = browser.get_page_info()

        if args.verbose:
            print(formatter.format_info(
                f"Fetched {len(html):,} bytes, title: {info.get('title', 'N/A')}"
            ))

        # Extract content
        data = extract_content(html, url)
        print(formatter.format_extracted(data))

        return 0

    except Exception as e:
        print(formatter.format_error(str(e)))
        return 1


def cmd_screenshot(args: argparse.Namespace) -> int:
    """Handle the 'screenshot' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    from .utils import validate_url, normalize_url

    url = normalize_url(args.url)
    if not validate_url(url):
        formatter = get_formatter(args.output, not args.no_color)
        print(formatter.format_error(f"Invalid URL: {url}"))
        return 1

    formatter = get_formatter(args.output, not args.no_color)
    browser = Browser(verbose=args.verbose)

    try:
        if args.verbose:
            print(formatter.format_info(f"Fetching {url} for screenshot..."))

        output_path = browser.save_screenshot(
            url,
            output_path=args.output_file,
            screenshot_type=args.format,
        )

        print(formatter.format_success(f"Screenshot saved to: {output_path}"))
        return 0

    except Exception as e:
        print(formatter.format_error(str(e)))
        return 1


def cmd_extract(args: argparse.Namespace) -> int:
    """Handle the 'extract' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    from .utils import validate_url, normalize_url

    url = normalize_url(args.url)
    if not validate_url(url):
        formatter = get_formatter(args.output, not args.no_color)
        print(formatter.format_error(f"Invalid URL: {url}"))
        return 1

    formatter = get_formatter(args.output, not args.no_color)
    browser = Browser(timeout=args.timeout, verbose=args.verbose)

    try:
        if args.verbose:
            print(formatter.format_info(f"Extracting content from {url}..."))

        html = browser.fetch(url)
        data = extract_content(html, url)

        # Filter fields if specified
        if args.fields:
            data = {k: v for k, v in data.items() if k in args.fields}

        print(formatter.format_extracted(data))
        return 0

    except Exception as e:
        print(formatter.format_error(str(e)))
        return 1


def cmd_run(args: argparse.Namespace) -> int:
    """Handle the 'run' subcommand.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    formatter = get_formatter(args.output, not args.no_color)

    # Check workflow file exists
    if not os.path.isfile(args.workflow):
        print(formatter.format_error(f"Workflow file not found: {args.workflow}"))
        return 1

    try:
        engine = WorkflowEngine(verbose=args.verbose)
        workflow = engine.load_workflow_file(args.workflow)

        if args.verbose:
            print(formatter.format_info(f"Loaded workflow with {len(workflow.get('steps', []))} steps"))

        result = engine.run(workflow)

        # Print result
        print(formatter.format_workflow_result(result))

        # Export to file if requested
        if args.export:
            import json
            with open(args.export, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(formatter.format_success(f"Results exported to: {args.export}"))

        return 0 if result.get("status") == "success" else 1

    except Exception as e:
        print(formatter.format_error(str(e)))
        return 1


def cmd_interactive(args: argparse.Namespace) -> int:
    """Handle the 'interactive' subcommand.

    Provides a simple REPL for browser interaction.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code.
    """
    formatter = get_formatter("text", not args.no_color)
    browser = Browser(verbose=True)

    print(formatter.format_info("WebPilot Interactive Session"))
    print("Type 'help' for available commands, 'quit' to exit.")
    print()

    # Navigate to initial URL if provided
    if args.url:
        try:
            browser.fetch(args.url)
            info = browser.get_page_info()
            print(formatter.format_success(f"Navigated to: {info.get('title', args.url)}"))
        except Exception as e:
            print(formatter.format_error(str(e)))

    while True:
        try:
            user_input = input("webpilot> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        parts = user_input.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        elif cmd == "help":
            print("Available commands:")
            print("  browse <url>     - Navigate to a URL and show content")
            print("  extract          - Extract structured content from current page")
            print("  screenshot [path]- Save screenshot (default: screenshot.html)")
            print("  info             - Show current page information")
            print("  ascii            - Show ASCII screenshot")
            print("  title            - Show page title")
            print("  links            - List all links on current page")
            print("  images           - List all images on current page")
            print("  cookies          - Show current cookies")
            print("  help             - Show this help message")
            print("  quit             - Exit interactive mode")

        elif cmd == "browse" and arg:
            try:
                browser.fetch(arg)
                info = browser.get_page_info()
                print(formatter.format_success(f"Navigated to: {info.get('title', arg)}"))
            except Exception as e:
                print(formatter.format_error(str(e)))

        elif cmd == "extract":
            html = browser._last_html
            if not html:
                print(formatter.format_warning("No page loaded. Use 'browse <url>' first."))
            else:
                data = extract_content(html, browser._last_url)
                print(formatter.format_extracted(data))

        elif cmd == "screenshot":
            html = browser._last_html
            if not html:
                print(formatter.format_warning("No page loaded."))
            else:
                path = arg if arg else "screenshot.html"
                try:
                    saved = browser.html_screenshot(path)
                    print(formatter.format_success(f"Screenshot saved to: {saved}"))
                except Exception as e:
                    print(formatter.format_error(str(e)))

        elif cmd == "ascii":
            html = browser._last_html
            if not html:
                print(formatter.format_warning("No page loaded."))
            else:
                print(browser.ascii_screenshot())

        elif cmd == "info":
            info = browser.get_page_info()
            print(formatter.format_page_info(info))

        elif cmd == "title":
            info = browser.get_page_info()
            print(info.get("title", "(no title)"))

        elif cmd == "links":
            html = browser._last_html
            if not html:
                print(formatter.format_warning("No page loaded."))
            else:
                data = extract_content(html, browser._last_url)
                links = data.get("links", [])
                if not links:
                    print("No links found.")
                else:
                    for i, link in enumerate(links, 1):
                        text = link.get("text", "")[:40]
                        href = link.get("href", "")
                        print(f"  {i}. [{text}] {href}")

        elif cmd == "images":
            html = browser._last_html
            if not html:
                print(formatter.format_warning("No page loaded."))
            else:
                data = extract_content(html, browser._last_url)
                images = data.get("images", [])
                if not images:
                    print("No images found.")
                else:
                    for i, img in enumerate(images, 1):
                        alt = img.get("alt", "")[:40]
                        src = img.get("src", "")
                        print(f"  {i}. {alt} -> {src}")

        elif cmd == "cookies":
            cookies = browser.session.get_cookies()
            if not cookies:
                print("No cookies.")
            else:
                for cookie in cookies:
                    print(f"  {cookie['name']} = {cookie['value']} ({cookie['domain']})")

        else:
            print(formatter.format_warning(f"Unknown command: {cmd}. Type 'help' for available commands."))

    return 0


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handler
    handlers = {
        "browse": cmd_browse,
        "screenshot": cmd_screenshot,
        "extract": cmd_extract,
        "run": cmd_run,
        "interactive": cmd_interactive,
    }

    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
