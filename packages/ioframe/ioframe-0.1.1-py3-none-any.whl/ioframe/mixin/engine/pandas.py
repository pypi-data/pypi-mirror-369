"""Define a mixin for the ``pandas`` engine."""

from __future__ import annotations


class PandasEngineMixin:
    """Mixin for Pandas I/O classes."""

    @classmethod
    def get_engine(cls) -> str:
        """Return the engine used by this object."""
        return "pandas"

    @classmethod
    def is_available(cls) -> bool:
        """Check if the backend is available."""
        return True
