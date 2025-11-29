# conftest.py
# Ensure the repository root is on sys.path so tests can import the package
# located at <repo_root>/archnews without requiring PYTHONPATH or an editable install.
#
# This file is imported by pytest very early, so placing this logic here makes
# running `pytest` from the repo root (or from other locations) more robust.

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_repo_root_on_sys_path() -> None:
    try:
        # conftest.py is at <repo_root>/tests/conftest.py
        repo_root = Path(__file__).resolve().parent.parent
        repo_root_str = str(repo_root)
        if repo_root_str not in sys.path:
            # Insert at front so local package shadows any installed package with same name
            sys.path.insert(0, repo_root_str)
    except Exception:
        # Defensive: don't raise from conftest import problems; test runner will report other failures.
        pass


_ensure_repo_root_on_sys_path()
