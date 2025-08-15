# rtflite <img src="assets/logo.png" align="right" width="120" />

[![PyPI version](https://img.shields.io/pypi/v/rtflite)](https://pypi.org/project/rtflite/)
![Python versions](https://img.shields.io/pypi/pyversions/rtflite)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![CI Tests](https://github.com/pharmaverse/rtflite/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/pharmaverse/rtflite/actions/workflows/ci-tests.yml)
[![mkdocs](https://github.com/pharmaverse/rtflite/actions/workflows/mkdocs.yml/badge.svg)](https://pharmaverse.github.io/rtflite/)
![License](https://img.shields.io/pypi/l/rtflite)

Lightweight RTF composer for Python.

Specializes in precise formatting of production-quality tables and figures. Inspired by [r2rtf](https://merck.github.io/r2rtf/).

## Installation

You can install rtflite from PyPI:

```bash
pip install rtflite
```

Or install the development version from GitHub:

```bash
git clone https://github.com/pharmaverse/rtflite.git
cd rtflite
python3 -m pip install -e .
```

### Install LibreOffice (optional)

rtflite can convert RTF documents to PDF using LibreOffice.
To enable this feature, install LibreOffice (free and open source, MPL license).

See the [converter setup
guide](https://pharmaverse.github.io/rtflite/articles/converter-setup/)
for detailed instructions.

## Contributing

We welcome contributions to rtflite. Please read the rtflite
[Contributing Guidelines](https://pharmaverse.github.io/rtflite/contributing/)
to get started.

All interactions within rtflite repositories and issue trackers should adhere to
the rtflite [Contributor Code of Conduct](https://github.com/pharmaverse/rtflite/blob/main/CODE_OF_CONDUCT.md).

## License

This project is licensed under the terms of the MIT license.
