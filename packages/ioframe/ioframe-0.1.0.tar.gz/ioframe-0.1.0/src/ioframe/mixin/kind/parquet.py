"""Define a mixin for the ``parquet`` kind."""

from __future__ import annotations

from pathlib import Path

__all__ = ["ParquetKindMixin"]


class ParquetKindMixin:
    """Mixin for Parquet I/O classes."""

    @classmethod
    def get_kind(cls) -> str:
        """Return the key used to identify this object in the registry."""
        return "parquet"

    @classmethod
    def is_compatible(cls, path: str | Path) -> bool:
        """Check if the backend is compatible with the given path."""
        return ".parquet" in Path(path).suffixes

    def get_suffix(self) -> str:
        return ".parquet"
