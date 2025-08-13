"""Define a mixin for the ``hdf5`` kind."""

from __future__ import annotations

from pathlib import Path


class HDF5KindMixin:
    """Mixin for HDF5 I/O classes."""

    @classmethod
    def get_kind(cls) -> str:
        """Return the key used to identify this object in the registry."""
        return "hdf5"

    @classmethod
    def is_compatible(cls, path: str | Path) -> bool:
        """Check if the backend is compatible with the given path."""
        return Path(path).suffix == ".h5"

    def get_suffix(self) -> str:
        return ".h5"
