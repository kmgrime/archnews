"""
Top-level package for the archnews project.

This module re-exports the main public symbols from the submodules so that
imports like `from archnews.fetcher import NewsFetcher` and
`from archnews import NewsFetcher` both work consistently.
"""

from .fetcher import NewsFetcher  # noqa: F401

__all__ = ["NewsFetcher"]
