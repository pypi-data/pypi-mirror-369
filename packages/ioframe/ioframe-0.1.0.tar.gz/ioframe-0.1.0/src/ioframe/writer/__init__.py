"""A package that defines DataFrames writers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from ..core.registry import BackendRegistry
from ..io._base import find_first_io_compatible
from .csv_pandas import DFCSVPandasWriter
from .csv_pyarrow import DFCSVPyArrowWriter
from .feather import DFFeatherWriter
from .hdf5 import DFHDF5Writer
from .parquet import DFParquetFastParquetWriter, DFParquetPyArrowWriter
from .root_pyroot import DFROOTPyRootWriter
from .root_uproot import DFROOTUpRootWriter

if TYPE_CHECKING:
    from pandas import DataFrame

    from ..core.types import BackendFunc
    from ..io.writer import DFWriterBase

__all__ = ["write", "writer_registry"]

writer_registry: Final[BackendRegistry[DFWriterBase]] = BackendRegistry()
"""A global registry for DataFrame writers."""

writer_registry.register_many(
    [
        DFParquetPyArrowWriter,
        DFParquetFastParquetWriter,
        DFFeatherWriter,
        DFHDF5Writer,
        DFCSVPyArrowWriter,
        DFCSVPandasWriter,
        DFROOTUpRootWriter,
        DFROOTPyRootWriter,
    ]
)


def write(
    df: DataFrame,
    path: str | Path,
    *,
    __filter__: BackendFunc[DFWriterBase, bool] | None = None,
    __registry__: BackendRegistry[DFWriterBase] = writer_registry,
    **kwargs: Any,
) -> Path:
    """Write a DataFrame to a file.

    Args:
        path: The file path to write to.
        df: The DataFrame to write.
        __filter__: A filter function to determine which backends to use.
        __registry__: The registry to use for finding the writer.
        **kwargs: Additional keyword arguments to pass to the writer.

    Returns:
        The path to the written file.
    """
    path = Path(path)
    filtered_registry = (
        __registry__.filter(__filter__) if __filter__ is not None else __registry__
    )
    writer_cls = find_first_io_compatible(filtered_registry, path)
    writer = writer_cls.model_validate(kwargs)
    return writer.write(df, path)
