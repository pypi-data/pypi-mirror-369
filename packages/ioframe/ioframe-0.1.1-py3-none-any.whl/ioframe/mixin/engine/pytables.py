"""Define a mixin for the ``pytables`` engine."""

from __future__ import annotations


class PyTablesEngineMixin:
    """Mixin for IO classes with PyTables support."""

    @classmethod
    def get_engine(cls) -> str:
        """Return the engine used by this object."""
        return "pytables"

    @classmethod
    def is_available(cls) -> bool:
        """Check if the backend is available."""
        try:
            import tables  # noqa: F401, PLC0415
        except ImportError:
            return False
        else:
            return True
