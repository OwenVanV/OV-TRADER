"""Core package for the OV Trader multi-agent trading system."""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("ov-trader")
except PackageNotFoundError:  # pragma: no cover - during local development
    __version__ = "0.1.0"

__all__ = ["__version__"]
