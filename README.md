
```
    _             _     _   _
   / \   _ __ ___| |__ | \ | | _____      _____
  / _ \ | '__/ __| '_ \|  \| |/ _ \ \ /\ / / __|
 / ___ \| | | (__| | | | |\  |  __/\ V  V /\__ \
/_/   \_\_|  \___|_| |_|_| \_|\___| \_/\_/ |___/
```

[![CI](https://github.com/kmgrime/archnews/actions/workflows/ci.yml/badge.svg)](https://github.com/kmgrime/archnews/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kmgrime/archnews/branch/main/graph/badge.svg)](https://codecov.io/gh/kmgrime/archnews)
[![Python versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)

---
A small CLI tool to fetch the Arch Linux news.

Local testing
- Create and activate a virtual environment for your platform.
- Install test dependencies (pytest, coverage) and run tests:

python -m pip install --upgrade pip
pip install pytest coverage
coverage run -m pytest
coverage report -m
