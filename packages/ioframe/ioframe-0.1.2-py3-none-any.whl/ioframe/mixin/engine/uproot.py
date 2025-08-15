"""Define a mixin for the ``uproot`` engine."""

from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

if TYPE_CHECKING:
    from pandas import DataFrame


class UpRootEngineMixin:
    """Mixin for PyROOT I/O classes."""

    @classmethod
    def get_engine(cls) -> str:
        """Return the engine used by this object."""
        return "uproot"

    @classmethod
    def is_available(cls) -> bool:
        """Check if the backend is available."""
        try:
            import uproot  # noqa: F401, PLC0415
        except ImportError:
            return False
        else:
            return True

    def _warns_empty(self, dataframe: DataFrame) -> None:
        """Warn if the DataFrame is empty."""
        if dataframe.empty:
            warn(
                (
                    f"DataFrame is empty so the {self.__class__.__name__} "
                    "might not be able to handle the dtypes correctly."
                ),
                UserWarning,
                stacklevel=2,
            )
