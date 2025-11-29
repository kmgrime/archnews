#!/usr/bin/env python3
"""
archnews/main.py

Simple CLI that prints an ASCII banner and a list of news articles (title and url).
This file is intentionally minimal so it's easy to read while you're learning.
"""

from typing import Iterable, Tuple, List, Union

from archnews.fetcher import NewsFetcher


BANNER = r"""
    _             _     _   _
   / \   _ __ ___| |__ | \ | | _____      _____
  / _ \ | '__/ __| '_ \|  \| |/ _ \ \ /\ / / __|
 / ___ \| | | (__| | | | |\  |  __/\ V  V /\__ \
/_/   \_\_|  \___|_| |_|_| \_|\___| \_/\_/ |___/
            A r c h  L i n u x  N e w s
"""  # can be created with figlet and edited


def _is_tuple_item(x: object) -> bool:
    return isinstance(x, (tuple, list)) and len(x) >= 2


def _print_articles(items: Iterable[Union[Tuple[str, str], str]]) -> None:
    """
    Print items in a simple numbered list. Items can be:
      - (title, url) tuples returned by fetch_from_web()
      - plain title strings returned by get_articles()
    """
    for i, it in enumerate(items, start=1):
        if _is_tuple_item(it):
            title, url = it[0], it[1]
            if url:
                print(f"{i}. {title} — {url}")
            else:
                print(f"{i}. {title}")
        else:
            # plain title
            print(f"{i}. {it}")


def main() -> None:
    print(BANNER)
    fetcher = NewsFetcher()

    # Prefer a web fetch; if it returns nothing, fall back to sample titles.
    try:
        raw = fetcher.fetch_from_web(limit=10)
    except Exception:
        raw = []

    if raw:
        # fetch_from_web returns (title, url) tuples
        print("Latest articles (fetched from web):\n")
        _print_articles(raw)
        return

    # fallback: get_articles() returns a list of titles (strings)
    try:
        titles: List[str] = fetcher.get_articles()
    except Exception:
        titles = []

    if titles:
        print("Sample articles:\n")
        _print_articles(titles)
    else:
        print("No articles available.")


if __name__ == "__main__":
    main()
