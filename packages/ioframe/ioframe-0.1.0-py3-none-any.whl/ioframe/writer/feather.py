"""Define the writer for the ``feather`` kind."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Any, Final

from ..io.writer import SingleDFWriterBase
from ..mixin.compression import CompressionMixin
from ..mixin.engine.pyarrow import PyArrowEngineMixin
from ..mixin.kind.feather import FeatherKindMixin

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame


__all__ = ["DFFeatherWriter"]


_UNCOMPRESSED_SENTINEL: Final[str] = "uncompressed"
"""Sentinel value used by PyArrow to denote no compression."""


class FeatherCompression(StrEnum):
    """Supported Feather compression codecs."""

    ZSTD = "zstd"
    """Zstandard compression codec."""

    LZ4 = "lz4"
    """LZ4 compression codec."""


class DFFeatherWriter(
    CompressionMixin[FeatherCompression],
    FeatherKindMixin,
    PyArrowEngineMixin,
    SingleDFWriterBase,
):
    """CSV Writer backed by **PyArrow**.

    By default, ``index=False`` is used when writing CSV files.
    """

    compression_level: int | None = None
    """Codec-specific compression level. ``None`` means Arrow default."""

    def _get_compression_argument(self):  # noqa: ANN202 (let mypy infer the type)
        compression = self.compression
        if isinstance(compression, FeatherCompression):
            return compression.value
        elif compression is None:
            return _UNCOMPRESSED_SENTINEL
        else:  # "default"
            return None

    @classmethod
    def get_compression_methods(cls) -> set[FeatherCompression | None]:
        return {*FeatherCompression, None}

    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        return df.to_feather(
            path,
            compression=self._get_compression_argument(),
            compression_level=self.compression_level,
            **kwargs,
        )

    def get_suffix(self) -> str:
        return ".feather"
