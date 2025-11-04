#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Production-style Python essentials in one file.

What this file demonstrates (with best practices and explanations in comments):
  - Project scaffolding patterns: main guard, config via environment variables, logging setup
  - Core syntax & data types: int, float, str, bool, list, tuple, dict, set, None
  - Control flow: if/elif/else, "if not" truthiness checks, for/while loops, for-else, break/continue
  - Looping techniques: enumerate, range, zip, list/dict/set comprehensions
  - Functions: type hints, docstrings, pure vs. impure, dependency injection, guard clauses
  - Errors & exceptions: try/except/else/finally, raising exceptions with context
  - File I/O: reading/writing JSON safely with context managers
  - Libraries used in real projects: os, sys, logging, requests (with retries & timeouts), dotenv
  - CLI basics: argparse (standard library), returning exit codes

Prereqs:
    pip install requests python-dotenv
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# ----------------------------- Constants & Conventions -----------------------------
# In production, use UPPER_SNAKE_CASE for constants.
DEFAULT_API_URL = "https://httpbin.org/get"
DEFAULT_DATA_DIR = Path.cwd() / "data"

# ----------------------------- Logging Configuration ------------------------------
def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure application-wide logging.

    Best practices:
    - Don't hardcode log level: read from env and/or CLI.
    - Include time, level, logger name, and message in the format.
    - Log to stdout by default (works well in containers and CI).
    """
    env_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, env_level, logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # quiet noisy libs


# ----------------------------- Environment Configuration --------------------------
def load_config() -> dict[str, Any]:
    """
    Load configuration from environment variables and sensible defaults.

    We use python-dotenv to optionally read a local .env file (not required in prod).
    """
    load_dotenv()  # no error if .env is missing

    cfg = {
        "API_URL": os.getenv("API_URL", DEFAULT_API_URL),
        "API_KEY": os.getenv("API_KEY"),  # may be None, and that's OK for demo
        "DATA_DIR": Path(os.getenv("DATA_DIR", str(DEFAULT_DATA_DIR))),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    }

    # Ensure data directory exists
    cfg["DATA_DIR"].mkdir(parents=True, exist_ok=True)

    return cfg


# ----------------------------- Requests Session with Retries -----------------------
def make_session() -> requests.Session:
    """
    Create a requests Session with retry/backoff and a helpful User-Agent.

    Best practices:
    - Use a Session for connection pooling.
    - Add retries with exponential backoff for transient HTTP errors (5xx/429).
    - Always set a timeout when sending requests.
    - Provide a descriptive User-Agent for observability on the server side.
    """
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,  # exponential backoff: 0.5, 1.0, 2.0...
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods={"GET", "POST"},
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "Python-Essentials/1.0 (+https://example.org)"})
    return session


def fetch_json(
    url: str,
    *,
    api_key: Optional[str] = None,
    session: Optional[requests.Session] = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """
    Fetch JSON from an HTTP endpoint with error handling.

    Args:
        url: Target endpoint. Should include scheme (http/https).
        api_key: Optional API key for Authorization header.
        session: Optional dependency injection for testability.
        timeout: Per-request timeout in seconds.

    Returns:
        Parsed JSON as a dict.

    Raises:
        ValueError: if URL format is suspicious.
        requests.RequestException: if transport/HTTP fails.
        json.JSONDecodeError: if response isn't valid JSON.
    """
    log = logging.getLogger("fetch_json")

    # "if not" is a Pythonic guard clause to validate inputs early.
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"URL must start with http:// or https://, got: {url!r}")

    sess = session or make_session()
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        log.debug("GET %s", url)
        resp: Response = sess.get(url, headers=headers, timeout=timeout)
        # Check for HTTP errors (4xx/5xx). `raise_for_status` raises HTTPError on bad status.
        try:
            resp.raise_for_status()
        except requests.HTTPError as http_err:
            # Log enough context for troubleshooting.
            log.error("HTTP error %s for %s: %s", resp.status_code, url, http_err)
            raise

        # Parse JSON. JSONDecodeError will be raised if invalid.
        data: dict[str, Any] = resp.json()
        log.debug("Received %d bytes", len(resp.content))
        return data

    except requests.Timeout as e:
        log.error("Timed out fetching %s: %s", url, e)
        raise
    except requests.RequestException as e:
        log.error("Network error fetching %s: %s", url, e)
        raise


# ----------------------------- Core Python Essentials -----------------------------
def summarize_numbers(values: Iterable[float]) -> dict[str, float]:
    """
    Compute simple statistics with explicit loops to illustrate control flow.

    Demonstrates:
      - "if not" to handle empty iterables (truthiness)
      - for loop, continue
      - min/max tracking
    """
    log = logging.getLogger("summarize_numbers")

    # Truthiness: empty containers are falsy, so "if not values" catches empty iterables.
    values = list(values)  # materialize in case of generator (single pass)
    if not values:
        # Guard clause to fail fast with a clear message.
        raise ValueError("summarize_numbers() requires at least one value")

    total = 0.0
    count = 0
    smallest = float("inf")
    largest = float("-inf")

    for v in values:
        # Skip NaNs or None (example of using 'continue' to jump to next item)
        if v is None:
            continue

        # Defensive programming: make sure it's numeric
        try:
            num = float(v)  # may raise ValueError/TypeError
        except (ValueError, TypeError):
            log.debug("Skipping non-numeric item: %r", v)
            continue

        total += num
        count += 1
        if num < smallest:
            smallest = num
        if num > largest:
            largest = num

    if count == 0:
        raise ValueError("No numeric values to summarize")

    mean = total / count
    return {"count": float(count), "sum": total, "mean": mean, "min": smallest, "max": largest}


def clean_names(raw_names: Iterable[str]) -> list[str]:
    """
    Clean a list of names using a list comprehension and truthiness.

    Shows:
      - List comprehension with inline condition
      - str methods (strip, title)
      - "if n" filters out empty strings (falsy)
    """
    return [n.strip().title() for n in raw_names if n and n.strip()]


def demo_collections_and_loops() -> dict[str, Any]:
    """
    Demonstrate core data types, looping patterns, and comprehensions.

    Returns a dictionary with example results to keep the function pure/testable.
    """
    # --- Data types ---
    an_int: int = 42
    a_float: float = 3.14159
    a_str: str = "hello"
    a_bool: bool = True
    a_none = None  # None is used to represent 'no value'

    # Lists (mutable, ordered)
    numbers: list[int] = [1, 2, 3, 4, 5]

    # Tuples (immutable, ordered)
    point: tuple[int, int] = (10, 20)

    # Sets (unique items, no order)
    colors: set[str] = {"red", "green", "blue", "red"}  # duplicates collapse automatically

    # Dicts (key-value mapping)
    user: dict[str, Any] = {"id": 123, "name": "Ada", "active": True}

    # Tuple unpacking
    x, y = point  # x=10, y=20

    # --- Looping patterns ---
    # Standard for-loop over lists
    doubled = []
    for n in numbers:
        doubled.append(n * 2)

    # enumerate() gives index + value
    indexed = []
    for idx, n in enumerate(numbers):
        indexed.append((idx, n))

    # range() for a sequence of integers
    first_five = []
    for i in range(5):
        first_five.append(i)

    # while loop (use sparingly; prefer for loops when possible)
    countdown = []
    i = 3
    while i > 0:
        countdown.append(i)
        i -= 1
    else:
        # while-else executes if the loop wasn't broken via 'break'
        countdown.append("liftoff")

    # for-else: else runs if no 'break' occurred
    contains_even = False
    for n in numbers:
        if n % 2 == 0:
            contains_even = True
            break
    else:
        # runs if the loop completes without break
        contains_even = False

    # zip() to iterate multiple sequences in parallel
    letters = ["a", "b", "c", "d", "e"]
    pairs = list(zip(numbers, letters))  # [(1,'a'), (2,'b'), ...]

    # Comprehensions (list, set, dict)
    squares = [n * n for n in numbers]
    even_set = {n for n in numbers if n % 2 == 0}
    index_map = {i: n for i, n in enumerate(numbers)}

    # "if not" examples (truthiness rules):
    # - 0, 0.0, '', [], {}, set(), None are all falsy.
    empty_list = []
    is_empty = not empty_list  # True

    return {
        "primitives": (an_int, a_float, a_str, a_bool, a_none),
        "collections": {"numbers": numbers, "point": point, "colors": colors, "user": user},
        "unpacked": {"x": x, "y": y},
        "loops": {
            "doubled": doubled,
            "indexed": indexed,
            "first_five": first_five,
            "countdown": countdown,
            "contains_even": contains_even,
            "pairs": pairs,
            "squares": squares,
            "even_set": even_set,
            "index_map": index_map,
            "is_empty": is_empty,
        },
    }


# ----------------------------- File I/O Utilities ---------------------------------
def save_json(data: Any, path: Path) -> None:
    """
    Safely write JSON to a file using a context manager.

    Best practices:
    - Use 'with' to ensure files are closed even on exceptions.
    - Set indent for human-readable files.
    - ensure_ascii=False keeps Unicode readable.
    """
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_json(path: Path) -> Any:
    """
    Read JSON data from a file.
    """
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------- CLI / Main -----------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Python essentials demo with production-style patterns."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="How many numbers to generate (for summary demo).",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Override API URL (otherwise uses env API_URL or default).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point. Return an exit code (0 means success), rather than calling sys.exit here.
    This makes the function testable. The __main__ guard calls sys.exit(main()).
    """
    # Parse CLI args (don't use sys.argv directly inside logic; dependency injection via argv)
    parser = build_parser()
    args = parser.parse_args(argv)

    # Load config and setup logging as early as possible
    cfg = load_config()
    setup_logging(cfg.get("LOG_LEVEL"))

    log = logging.getLogger("main")
    api_url = args.url or cfg["API_URL"]
    api_key = cfg["API_KEY"]
    data_dir: Path = cfg["DATA_DIR"]

    # Never log secrets directly. Mask sensitive values.
    masked_key = (api_key[:4] + "..." + api_key[-2:]) if api_key and len(api_key) > 6 else None
    log.info("Using API_URL=%s | API_KEY=%s | DATA_DIR=%s", api_url, masked_key, data_dir)

    # --- Demonstrate core Python + best practices ---
    # Generate a simple sequence of numbers (pure function idea)
    numbers = list(range(1, args.count + 1))

    # Show summaries with loops and guard clauses
    try:
        stats = summarize_numbers(numbers + [None, "oops"])  # None & "oops" are skipped safely
        log.info("Summary: %s", stats)
    except ValueError as e:
        log.error("Could not summarize numbers: %s", e)
        return 1

    # Clean some names with a comprehension and truthiness
    raw_names = ["  ada  ", "", "grace", "  ", "ALAN"]
    cleaned = clean_names(raw_names)
    log.info("Cleaned names: %s", cleaned)

    # Demonstrate collections & loops
    demo = demo_collections_and_loops()
    log.debug("Demo payload: %s", demo)

    # --- Networking with requests (retries & timeout) ---
    try:
        payload = fetch_json(api_url, api_key=api_key, timeout=5.0)
        log.info("Fetched JSON keys: %s", list(payload.keys()))
    except Exception as e:
        log.error("Failed to fetch from %s: %s", api_url, e)
        # Continue; still demonstrate file I/O using what we have
        payload = {"error": str(e), "url": api_url}

    # --- File I/O: write and read back ---
    out_file = data_dir / "response.json"
    save_json(payload, out_file)
    log.info("Wrote %s (%d bytes)", out_file, out_file.stat().st_size)

    # Reading back (shows context manager for reading)
    loaded = read_json(out_file)
    assert isinstance(loaded, dict)  # simple check (would be a test in real code)

    # --- OS interactions ---
    # os.listdir to show directory contents (Pathlib is often nicer, but both are common)
    try:
        files = os.listdir(data_dir)
        log.debug("Files in DATA_DIR: %s", files)
    except OSError as e:
        log.warning("Could not list DATA_DIR: %s", e)

    # --- "if not" in action: quick config validation example ---
    # Prefer 'if not var' when checking for emptiness/None/Falsey. Be explicit if 0 is valid.
    if not cleaned:
        log.warning("No valid names provided after cleaning")

    # Example explicit None check when 0/empty string are valid but None is not:
    maybe_threshold: Optional[int] = None
    if maybe_threshold is None:
        log.debug("Threshold is not set (None). Using default behavior.")

    # Return explicit exit code for shells/CI
    return 0


# ----------------------------- Testable Execution Guard ---------------------------
if __name__ == "__main__":
    # sys.exit ensures the process returns the exit code from main()
    sys.exit(main())
