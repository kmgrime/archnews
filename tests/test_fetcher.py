import pytest
from urllib.error import URLError, HTTPError

from archnews.fetcher import NewsFetcher
import archnews.fetcher as fetcher


def test_constructor():
    f = NewsFetcher()
    assert f.source_url == "https://archlinux.org/news/"


def test_get_articles_uses_fetch_from_web(monkeypatch):
    # Ensure get_articles returns titles produced by fetch_from_web
    monkeypatch.setattr(
        NewsFetcher,
        "fetch_from_web",
        lambda self, limit=2, timeout=5: [("T1", "u1"), ("T2", "u2")],
    )
    f = NewsFetcher()
    articles = f.get_articles()
    assert articles == ["T1", "T2"]


def test_get_articles_falls_back_on_exception(monkeypatch):
    # If fetch_from_web raises, get_articles should return the sample fallback
    def raise_exc(*args, **kwargs):
        raise RuntimeError("no network")

    monkeypatch.setattr(NewsFetcher, "fetch_from_web", raise_exc)
    f = NewsFetcher()
    articles = f.get_articles()
    assert articles == ["Article A", "Article B"]


def _make_response(html_bytes: bytes):
    class DummyResp:
        def __init__(self, data: bytes):
            self._data = data

        def read(self):
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    return DummyResp(html_bytes)


def test_fetch_from_web_parses_and_deduplicates(monkeypatch):
    # HTML with three rows: two unique articles and one duplicate of the first
    html = b"""
    <html>
      <body>
        <table id="article-list">
          <tbody>
            <tr><td>date</td><td class="wrap"><a href="/news/1/">First Article</a></td></tr>
            <tr><td>date</td><td class="wrap"><a href="https://example.com/news/2/">Second Article</a></td></tr>
            <tr><td>date</td><td class="wrap"><a href="/news/1/">First Article</a></td></tr>
          </tbody>
        </table>
      </body>
    </html>
    """

    def fake_urlopen(req, timeout=None):
        return _make_response(html)

    monkeypatch.setattr(fetcher, "urlopen", fake_urlopen)

    f = NewsFetcher()
    items = f.fetch_from_web(limit=10, timeout=1)
    # Should have two unique results in order
    assert len(items) == 2
    titles = [t for t, _ in items]
    urls = [u for _, u in items]
    assert titles == ["First Article", "Second Article"]
    # urljoin should resolve the relative href against the source URL
    assert urls[0].startswith("https://archlinux.org/news/")
    assert "example.com" in urls[1]


def test_fetch_from_web_respects_limit(monkeypatch):
    html = b"""
    <table id="article-list">
      <tbody>
        <tr><td>date</td><td class="wrap"><a href="/n/1/">A</a></td></tr>
        <tr><td>date</td><td class="wrap"><a href="/n/2/">B</a></td></tr>
        <tr><td>date</td><td class="wrap"><a href="/n/3/">C</a></td></tr>
      </tbody>
    </table>
    """

    monkeypatch.setattr(
        fetcher, "urlopen", lambda req, timeout=None: _make_response(html)
    )
    f = NewsFetcher()
    items = f.fetch_from_web(limit=1)
    assert len(items) == 1
    assert items[0][0] == "A"


def test_fetch_from_web_handles_latin1_decoding(monkeypatch):
    # Build HTML where the article title includes a latin-1 only byte (é as 0xe9).
    # This will cause a UnicodeDecodeError on utf-8 decode and force the latin-1 fallback.
    html = b"""
    <table id="article-list">
      <tbody>
        <tr><td>date</td><td class="wrap"><a href="/n/1/">Caf\xe9</a></td></tr>
      </tbody>
    </table>
    """

    monkeypatch.setattr(
        fetcher, "urlopen", lambda req, timeout=None: _make_response(html)
    )
    f = NewsFetcher()
    items = f.fetch_from_web()
    assert len(items) == 1
    assert items[0][0] == "Caf\u00e9"  # 'Café'


def test_fetch_from_web_returns_empty_on_network_error(monkeypatch):
    # Simulate URLError
    def raise_url_error(req, timeout=None):
        raise URLError("network down")

    monkeypatch.setattr(fetcher, "urlopen", raise_url_error)
    f = NewsFetcher()
    assert f.fetch_from_web() == []

    # Simulate HTTPError
    def raise_http_error(req, timeout=None):
        raise HTTPError(url=f.source_url, code=500, msg="err", hdrs=None, fp=None)

    monkeypatch.setattr(fetcher, "urlopen", raise_http_error)
    assert f.fetch_from_web() == []
