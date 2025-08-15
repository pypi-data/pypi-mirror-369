"""Define a mixin for the ``parquet`` kind."""

from __future__ import annotations

from pathlib import Path


class CSVKindMixin:
    """Mixin for CSV I/O classes."""

    @classmethod
    def get_kind(cls) -> str:
        """Return the key used to identify this object in the registry."""
        return "csv"

    @classmethod
    def is_compatible(cls, path: str | Path) -> bool:
        """Check if the backend is compatible with the given path."""
        return ".csv" in Path(path).suffixes
