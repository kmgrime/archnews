#!/usr/bin/env python3
"""
archnews/main.py

Simple CLI that prints an ASCII banner and a list of news articles (title and url).
This file is intentionally minimal so it's easy to read while you're learning.

This version avoids type annotations that produce linter/type-warn messages
and keeps the runtime behavior and banner unchanged.
"""

from archnews.fetcher import NewsFetcher


BANNER = r"""
    _             _     _   _
   / \   _ __ ___| |__ | \ | | _____      _____
  / _ \ | '__/ __| '_ \|  \| |/ _ \ \ /\ / / __|
 / ___ \| | | (__| | | | |\  |  __/\ V  V /\__ \
/_/   \_\_|  \___|_| |_|_| \_|\___| \_/\_/ |___/
            A r c h  L i n u x  N e w s
"""  # can be created with figlet and edited


def _print_articles(items):
    """
    Print items in a simple numbered list.

    Items may be:
      - (title, url) tuples or lists returned by fetch_from_web()
      - plain title strings returned by get_articles()
    """
    for i, it in enumerate(items, start=1):
        # Try to treat the item as a sequence with at least two elements.
        if isinstance(it, (tuple, list)):
            try:
                title, url = it[0], it[1]
            except Exception:
                # Fallback if the sequence doesn't have expected shape.
                title, url = str(it), ""
        else:
            title, url = str(it), ""

        if url:
            print(f"{i}. {title} — {url}")
        else:
            print(f"{i}. {title}")


def main():
    print(BANNER)
    fetcher = NewsFetcher()

    # Prefer fetching from the web; fall back to bundled sample titles on error
    # or when no results are returned.
    try:
        articles = fetcher.fetch_from_web(limit=10) or []
    except Exception:
        articles = []

    if articles:
        print("Latest articles (fetched from web):\n")
        _print_articles(articles)
        return

    try:
        samples = fetcher.get_articles() or []
    except Exception:
        samples = []

    if samples:
        print("Sample articles:\n")
        _print_articles(samples)
    else:
        print("No articles available.")


if __name__ == "__main__":
    main()
