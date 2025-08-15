"""Define the writers for the ``parquet`` kind."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any, Literal, cast

from ..io.writer import SingleDFWriterBase
from ..mixin.compression import CompressionMixin
from ..mixin.engine.fastparquet import FastParquetEngineMixin
from ..mixin.engine.pyarrow import PyArrowEngineMixin
from ..mixin.kind.parquet import ParquetKindMixin

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame

__all__ = ["DFParquetFastParquetWriter", "DFParquetPyArrowWriter"]


class ParquetCompression(StrEnum):
    """Supported Parquet compression codecs for PyArrow."""

    SNAPPY = "snappy"
    """Snappy compression codec."""

    GZIP = "gzip"
    """Gzip compression codec."""

    BROTLI = "brotli"
    """Brotli compression codec."""

    LZ4 = "lz4"
    """LZ4 compression codec."""

    ZSTD = "zstd"
    """Zstandard compression codec."""


class DFParquetWriterBase(
    CompressionMixin[ParquetCompression], ParquetKindMixin, SingleDFWriterBase
):
    """Parquet Reader backed by **Pandas**."""

    compression: ParquetCompression | Literal["default"] | None = "default"
    """Compression codec. ``None`` means *no compression*."""

    @classmethod
    def get_compression_methods(cls) -> set[ParquetCompression | None]:
        return {*ParquetCompression, None}

    def _get_compression_argument(self):  # noqa: ANN202 (let mypy infer the type)
        """Get the compression codec for Parquet."""
        compression = self.compression
        if isinstance(compression, ParquetCompression):
            return compression.value
        else:  # None or "default"
            return None

    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        kwargs.setdefault("index", False)
        engine = cast("Literal['fastparquet', 'pyarrow']", self.get_engine())
        df.to_parquet(
            path, compression=self._get_compression_argument(), engine=engine, **kwargs
        )


class DFParquetFastParquetWriter(FastParquetEngineMixin, DFParquetWriterBase):
    """Parquet Reader backed by **FastParquet**."""


class DFParquetPyArrowWriter(PyArrowEngineMixin, DFParquetWriterBase):
    """Parquet Reader backed by **PyArrow**."""
