"""Core package for the OV Trader multi-agent trading system."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import os


def _load_root_env() -> None:
    """Load variables from the repository level ``.env`` file if present."""

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():  # pragma: no cover - optional convenience for devs
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


_load_root_env()


try:
    __version__ = version("ov-trader")
except PackageNotFoundError:  # pragma: no cover - during local development
    __version__ = "0.1.0"

__all__ = ["__version__"]
