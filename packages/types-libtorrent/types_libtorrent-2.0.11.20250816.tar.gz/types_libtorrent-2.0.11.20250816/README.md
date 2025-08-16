# types-libtorrent

Type stubs for [python-libtorrent](https://pypi.org/project/python-libtorrent/) 2.0.11

This package provides type stubs for the python-libtorrent library, enabling static type checking and improved IDE support when working with libtorrent in Python.

## Installation

```bash
pip install types-libtorrent
```

## Usage

After installation, type checkers like mypy, PyCharm, or VS Code will automatically use these stubs when working with the `libtorrent` module.

```python
import libtorrent as lt

# Now with full type support
session = lt.session()
```

## Compatibility

This stub package is compatible with:
- python-libtorrent 2.0.11.*
- Python 3.8+

## Version Scheme

The version number follows the pattern: `{libtorrent_version}.{stub_date}`
- `2.0.11` - Compatible with libtorrent 2.0.11.*
- `20250815` - Stubs created/updated on August 15, 2025

## License

MIT License