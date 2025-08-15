"""Define the readers for the ``parquet`` kind."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

from ..io.reader import SingleDFReaderBase
from ..mixin.engine.fastparquet import FastParquetEngineMixin
from ..mixin.engine.pyarrow import PyArrowEngineMixin
from ..mixin.kind.parquet import ParquetKindMixin

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame

__all__ = [
    "DFParquetFastParquetReader",
    "DFParquetPyArrowReader",
]


class DFParquetReaderBase(ParquetKindMixin, SingleDFReaderBase):
    """Parquet Reader backed by **Pandas**."""

    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        from pandas import read_parquet  # noqa: PLC0415

        engine = self.get_engine()
        engine = cast("Literal['fastparquet', 'pyarrow']", self.get_engine())
        return read_parquet(path, columns=columns, engine=engine, **kwargs)


class DFParquetFastParquetReader(FastParquetEngineMixin, DFParquetReaderBase):
    """Parquet Reader backed by **FastParquet**."""


class DFParquetPyArrowReader(PyArrowEngineMixin, DFParquetReaderBase):
    """Parquet Reader backed by **PyArrow**."""
