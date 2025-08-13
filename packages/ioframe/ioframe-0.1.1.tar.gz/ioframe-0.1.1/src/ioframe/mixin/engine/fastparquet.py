"""Define a mixin for the ``fastparquet`` engine."""

from __future__ import annotations


class FastParquetEngineMixin:
    """Mixin for FastParquet engine-specific functionality."""

    @classmethod
    def get_engine(cls) -> str:
        """Return the engine used by this object."""
        return "fastparquet"

    @classmethod
    def is_available(cls) -> bool:
        """Check if the backend is available."""
        try:
            import fastparquet  # noqa: F401, PLC0415
        except ImportError:
            return False
        else:
            return True
