"""Define the base classes for dataframe readers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ._base import IOBase

if TYPE_CHECKING:
    from pandas import DataFrame

__all__ = ["DFReaderBase", "HierarchicalDFReaderBase", "SingleDFReaderBase"]

logger = getLogger(__name__)


class DFReaderBase(IOBase, ABC):
    """Base class for DataFrame reader."""

    # Private methods ================================================================
    def _resolve_path(self, path: str | Path) -> Path:
        """Resolve the path to a Path object.

        Args:
            path: The path to resolve.

        Returns:
            The resolved Path object.
        """
        return Path(path).expanduser().resolve()

    @abstractmethod
    def read(
        self, path: str | Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame: ...


class SingleDFReaderBase(DFReaderBase, ABC):
    """Base class for DataFrame reader.

    This class provides a common interface for reading DataFrames
    across different formats. It is not intended to be instantiated directly.
    Subclasses must implement the abstract methods defined below.
    """

    # Abstract methods ===============================================================
    @abstractmethod
    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        """Read the DataFrame from the specified path."""

    # Public methods =================================================================
    def read(
        self, path: str | Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        """Load a DataFrame from *path*.

        Args:
            path: The path to the DataFrame file.
            columns: Optional list of columns to read from the file.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            The loaded DataFrame(s).
        """
        path = self._resolve_path(path)

        if not path.exists():
            msg = f"Path '{path}' does not exist."
            raise FileNotFoundError(msg)
        logger.debug(
            "Reading DataFrame from '%s' with %s", path, self.__class__.__name__
        )
        return self._read(path, columns=columns, **self.merge_extra_kwargs(**kwargs))


class HierarchicalDFReaderBase(DFReaderBase, ABC):
    """Base class for hierarchical DataFrame reader.

    This class provides a common interface for reading hierarchical DataFrames
    across different formats. It is not intended to be instantiated directly.
    Subclasses must implement the abstract methods defined below.
    """

    default_key: str = "__key__"
    """Default key when a single DataFrame is read."""

    # Abstract methods ===============================================================
    @abstractmethod
    def _read(
        self,
        path: Path,
        key_to_columns: Mapping[str, list[str] | None] | None = None,
        **kwargs: Any,
    ) -> dict[str, DataFrame]:
        """Read the DataFrame from the specified path."""

    # Public methods =================================================================
    def read(
        self,
        path: str | Path,
        columns: list[str] | None = None,
        **kwargs: Any,
    ) -> DataFrame:
        """Load a DataFrame from *path*.

        Args:
            path: The path to the DataFrame file.
            columns: Optional list of columns to read from the file.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            The loaded DataFrame(s).
        """
        path = self._resolve_path(path)

        if not path.exists():
            msg = f"Path '{path}' does not exist."
            raise FileNotFoundError(msg)
        logger.debug(
            "Reading DataFrame from '%s' with %s", path, self.__class__.__name__
        )
        dataframes = self._read(
            path,
            key_to_columns={self.default_key: columns},
            **self.merge_extra_kwargs(**kwargs),
        )
        return dataframes[self.default_key]

    def read_mapping(
        self,
        path: str | Path,
        key_to_columns: Sequence[str] | Mapping[str, list[str] | None] | None = None,
        **kwargs: Any,
    ) -> dict[str, DataFrame]:
        """Load a mapping of DataFrames from *path*.

        Args:
            path: The path to the DataFrame file.
            key_to_columns: Optional mapping of keys to columns to read from the file.
            **kwargs: Additional backend-specific keyword arguments.

        Returns:
            A dictionary mapping keys to DataFrames.
        """
        path = self._resolve_path(path)

        if isinstance(key_to_columns, Sequence):
            key_to_columns = dict.fromkeys(key_to_columns, None)

        if not path.exists():
            msg = f"Path '{path}' does not exist."
            raise FileNotFoundError(msg)
        logger.debug(
            "Reading DataFrame from '%s' with %s", path, self.__class__.__name__
        )
        return self._read(
            path,
            key_to_columns=key_to_columns,
            **self.merge_extra_kwargs(**kwargs),
        )
