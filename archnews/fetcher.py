# Minimal fetcher that parses the Arch Linux news table (#article-list)
# and extracts article title + url using only the Python standard library.
# Modernized typing to use built-in generics and PEP 604 unions.

from html.parser import HTMLParser
from collections.abc import Callable
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def log_call(func: Callable[..., Any]) -> Callable[..., Any]:
    """Small decorator used by tests/examples to show that a function was called."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print("Calling", func.__name__)
        return func(*args, **kwargs)

    return wrapper


class _ArticleTableParser(HTMLParser):
    """
    Parse the HTML and extract anchors found in the table with id="article-list".

    We look for:
      <table id="article-list"> ... <tbody> <tr> <td>... </td> <td class="wrap"><a href="...">Title</a></td> ...
    and capture the anchor text and href from the second <td> in each <tr>.

    The parser is intentionally small and forgiving.
    """

    def __init__(self) -> None:
        super().__init__()
        self._in_table = False
        self._in_tbody = False
        self._in_tr = False
        self._current_td_index = 0  # 1-based index for tds inside current tr
        self._in_anchor = False
        self._current_href: str | None = None
        self._current_text_parts: list[str] = []
        self.articles: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        # attrs may contain None values for some attributes, keep them as-is
        attrd = {k.lower(): v for k, v in attrs if k}

        if tag == "table" and (attrd.get("id") or "") == "article-list":
            self._in_table = True
            return

        if not self._in_table:
            return

        if tag == "tbody":
            self._in_tbody = True
            return

        if not self._in_tbody:
            return

        if tag == "tr":
            self._in_tr = True
            self._current_td_index = 0
            return

        if tag == "td" and self._in_tr:
            # entering a new td cell -> increment index
            self._current_td_index += 1
            return

        if tag == "a" and self._in_tr and self._current_td_index == 2:
            # anchor inside the second td (title cell) -> candidate article link
            href = attrd.get("href")
            if href:
                self._in_anchor = True
                self._current_href = href  # keep raw href; will be made absolute later
                self._current_text_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_anchor and data and data.strip():
            self._current_text_parts.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if tag == "a" and self._in_anchor:
            title = " ".join(self._current_text_parts).strip()
            if title and self._current_href:
                self.articles.append((title, self._current_href))
            self._in_anchor = False
            self._current_href = None
            self._current_text_parts = []
            return

        if tag == "tr" and self._in_tr:
            # end of row - reset state for next row
            self._in_tr = False
            self._current_td_index = 0
            return

        if tag == "tbody" and self._in_tbody:
            self._in_tbody = False
            return

        if tag == "table" and self._in_table:
            # finished parsing the article table
            self._in_table = False
            return


class NewsFetcher:
    """
    Minimal NewsFetcher that can fetch and parse the Arch Linux News page's
    article table, returning (title, url) pairs.

    Methods
    - fetch_from_web(limit, timeout) -> list[(title, full_url)]
    - get_articles() -> list[str]  (titles only; falls back to samples)
    """

    def __init__(self) -> None:
        self.source_url = "https://archlinux.org/news/"

    @log_call
    def get_articles(self) -> list[str]:
        # Try to fetch two real article titles, otherwise return sample data.
        try:
            items = self.fetch_from_web(limit=2, timeout=5)
            if items:
                return [t for t, _ in items]
        except Exception:
            pass
        return ["Article A", "Article B"]

    def fetch_from_web(
        self, limit: int = 10, timeout: int = 5
    ) -> list[tuple[str, str]]:
        """
        Fetch the news page and extract (title, full_url) from the #article-list table.

        Returns an empty list on network or parsing failure.
        """
        req = Request(self.source_url, headers={"User-Agent": "archnews-fetcher/0.1"})
        try:
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                try:
                    html = raw.decode("utf-8")
                except UnicodeDecodeError:
                    html = raw.decode("latin-1")
        except (HTTPError, URLError, ValueError):
            return []

        parser = _ArticleTableParser()
        parser.feed(html)

        # Build absolute URLs and deduplicate while preserving order
        seen: set[tuple[str, str]] = set()
        results: list[tuple[str, str]] = []
        for title, href in parser.articles:
            full = urljoin(self.source_url, href)
            key = (title, full)
            if key in seen:
                continue
            seen.add(key)
            results.append((title, full))
            if len(results) >= limit:
                break

        return results


__all__ = ["NewsFetcher"]
