"""Define the writer for the ``csv`` kind and ``pyarrow`` engine."""

from __future__ import annotations

from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, Literal

from .._suffix import get_suffix_for, merge_suffixes
from ..io.writer import SingleDFWriterBase
from ..mixin.kind_engine.csv_pyarrow import CSVPyArrowCompression, DFCSVPyArrowMixin

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame

__all__ = ["DFCSVPyArrowWriter"]


class DFCSVPyArrowWriter(DFCSVPyArrowMixin, SingleDFWriterBase):
    """CSV Writer backed by **PyArrow**.

    By default, ``index=False`` is used when writing CSV files.
    """

    compression: CSVPyArrowCompression | Literal["default"] | None = "default"
    """Compression method. None means no compression."""

    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        from pyarrow import CompressedOutputStream, Table  # noqa: PLC0415
        from pyarrow.csv import write_csv  # noqa: PLC0415

        table = Table.from_pandas(df)

        pyarrow_compression = self._get_compression_argument(path)

        with (
            CompressedOutputStream(path, compression=pyarrow_compression)
            if pyarrow_compression
            else nullcontext(path)
        ) as output_file:
            write_csv(table, output_file, **kwargs)

    def get_suffix(self) -> str:
        return merge_suffixes(".csv", get_suffix_for(self.get_compression_method()))
