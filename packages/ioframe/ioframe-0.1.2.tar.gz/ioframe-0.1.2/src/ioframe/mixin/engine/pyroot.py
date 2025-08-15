"""Define a mixin for the ``pyroot`` engine."""

from __future__ import annotations


class PyROOTEngineMixin:
    """Mixin for PyROOT I/O classes.

    This mixin provides common functionality for PyArrow I/O classes, such as
    getting the file extension based on the compression method.
    """

    @classmethod
    def get_engine(cls) -> str:
        """Return the engine used by this object."""
        return "pyroot"

    @classmethod
    def is_available(cls) -> bool:
        """Check if the backend is available."""
        try:
            import ROOT  # noqa: F401, PLC0415
        except ImportError:
            return False
        else:
            return True
