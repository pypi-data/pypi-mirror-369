"""A package that defines DataFrame readers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from ..core.registry import BackendRegistry
from ..io._base import find_first_io_compatible
from .csv_pandas import DFCSVPandasReader
from .csv_pyarrow import DFCSVPyArrowReader
from .feather import DFFeatherReader
from .hdf5 import DFHDF5Reader
from .parquet import DFParquetFastParquetReader, DFParquetPyArrowReader
from .root_pyroot import DFROOTPyRootReader
from .root_uproot import DFROOTUpRootReader

if TYPE_CHECKING:
    from pandas import DataFrame

    from ..core.types import BackendFunc
    from ..io.reader import DFReaderBase


__all__ = ["read", "reader_registry"]

reader_registry: Final[BackendRegistry[DFReaderBase]] = BackendRegistry()
"""A global registry for DataFrame readers."""

reader_registry.register_many(
    [
        DFParquetPyArrowReader,
        DFParquetFastParquetReader,
        DFFeatherReader,
        DFHDF5Reader,
        DFCSVPyArrowReader,
        DFCSVPandasReader,
        DFROOTUpRootReader,
        DFROOTPyRootReader,
    ]
)


def read(
    path: str | Path,
    *,
    columns: list[str] | None = None,
    __filter__: BackendFunc[DFReaderBase, bool] | None = None,
    __registry__: BackendRegistry[DFReaderBase] = reader_registry,
    **kwargs: Any,
) -> DataFrame:
    """Read a DataFrame from a file.

    Args:
        path: The file path to read from.
        columns: The columns to read from the file.
        __kind_to_engines__: A mapping of DataFrame kind to engines or a sequence
            of kinds to filter the registry.
        __registry__: The registry to use for finding the reader.
        **kwargs: Additional keyword arguments to pass to the reader.

    Returns:
        The read DataFrame.
    """
    path = Path(path)
    filtered_registry = (
        __registry__.filter(__filter__) if __filter__ is not None else __registry__
    )
    reader_cls = find_first_io_compatible(filtered_registry, path)
    reader = reader_cls.model_validate(kwargs)
    return reader.read(path, columns=columns)
