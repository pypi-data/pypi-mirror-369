"""Define the base classes for dataframe writers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from logging import DEBUG, getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias

from pandas import DataFrame

from ._base import IOBase

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["DFWriterBase", "HierarchicalDFWriterBase", "SingleDFWriterBase"]

logger = getLogger(__name__)


def _create_directory(path: Path) -> None:
    """Create a directory if it does not exist.

    Args:
        path: The path to the directory to create.
    """
    if not path.exists():
        logger.debug("Creating directory '%s'", path)
        path.mkdir(parents=True, exist_ok=True)


class DFWriterBase(IOBase, ABC):
    """Base class for DataFrame writer."""

    # Abstract methods ===============================================================
    @abstractmethod
    def get_suffix(self) -> str:
        """Return the file extension used by this writer, WITH leading dot.

        The extension is added to the path if not already present.
        """

    @abstractmethod
    def write(self, df: DataFrame, path: str | Path, **kwargs: Any) -> Path:
        """Save the DataFrame to *path*.

        Args:
            df: The DataFrame to save.
            path: Destination path.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            The path where the DataFrame was saved.
            The extension will be appended if not already present.
        """

    # Public methods =================================================================
    def resolve_path(self, path: str | Path) -> Path:
        """Resolve the path to a Path object.

        Args:
            path: The path to resolve.

        Returns:
            The resolved Path object.
        """
        path = Path(path).expanduser().resolve()
        if not path.suffix:
            extension = self.get_suffix()
            logger.debug("Appending extension '%s' to path '%s'", extension, path)
            path = path.with_suffix(extension)

        return path


class SingleDFWriterBase(DFWriterBase, ABC):
    """Base class for DataFrame writer.

    This class provides a common interface for writing DataFrames
    across different formats. It is not intended to be instantiated directly.
    Subclasses must implement the abstract methods defined below.
    """

    # Abstract methods ===============================================================
    @abstractmethod
    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        """Bare minimum method to write a DataFrame to the specified path."""

    # Public methods =================================================================
    def write(self, df: DataFrame, path: str | Path, **kwargs: Any) -> Path:
        """Save the DataFrame to *path*.

        Args:
            df: The DataFrame to save.
            path: Destination path.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            The path where the DataFrame was saved.
            The extension will be appended if not already present.
        """
        path = self.resolve_path(path)

        _create_directory(path.parent)
        logger.debug("Writing DataFrame to '%s' with %s", path, self.__class__.__name__)
        self._write(df, path, **self.merge_extra_kwargs(**kwargs))
        return path


Key: TypeAlias = str
"""A type alias for the key used in hierarchical DataFrames."""


class HierarchicalDFWriterBase(DFWriterBase, ABC):
    """Base class for hierarchical DataFrame writer.

    This class provides a common interface for writing hierarchical DataFrames
    across different formats. It is not intended to be instantiated directly.
    Subclasses must implement the abstract methods defined below.
    """

    default_key: str = "__key__"
    """Default key when a single DataFrame is written."""

    # Abstract methods ===============================================================
    @abstractmethod
    def _write(
        self, dataframes: Mapping[Key, DataFrame], path: Path, **kwargs: Any
    ) -> None:
        """Write a mapping of dataframes to the specified path."""

    # Public methods =================================================================
    def write(  # type: ignore[override]
        self,
        dataframes: DataFrame | Mapping[Key, DataFrame],
        path: str | Path,
        **kwargs: Any,
    ) -> Path:
        """Save dataframes to a file.

        Args:
            dataframes: A single DataFrame or a mapping of DataFrames to save.
            path: Destination path.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            The path where the hierarchical DataFrame was saved.
            The extension will be appended if not already present.
        """
        path = self.resolve_path(path)

        _create_directory(path.parent)
        if logger.isEnabledFor(DEBUG):  # pragma: no cover
            logger.debug(
                "Writing dataframes '%s' to '%s' with %s",
                list(dataframes.keys()),
                path,
                self.__class__.__name__,
            )

        if isinstance(dataframes, DataFrame):
            dataframes = {self.default_key: dataframes}

        self._write(dataframes, path, **self.merge_extra_kwargs(**kwargs))
        return path
