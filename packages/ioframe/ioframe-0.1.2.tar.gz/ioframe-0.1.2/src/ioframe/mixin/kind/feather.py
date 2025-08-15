"""Define a mixin for the ``feather`` kind."""

from __future__ import annotations

from pathlib import Path


class FeatherKindMixin:
    """Mixin for Feather I/O classes."""

    @classmethod
    def get_kind(cls) -> str:
        """Return the key used to identify this object in the registry."""
        return "feather"

    @classmethod
    def is_compatible(cls, path: str | Path) -> bool:
        """Check if the backend is compatible with the given path."""
        return ".feather" in Path(path).suffixes
