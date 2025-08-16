# ankur_scraper/ankur_scraper/__init__.py
try:
    from ._version import __version__
except Exception:
    # safe fallback so builds never crash
    __version__ = "0.1.4"

__all__ = ["__version__"]