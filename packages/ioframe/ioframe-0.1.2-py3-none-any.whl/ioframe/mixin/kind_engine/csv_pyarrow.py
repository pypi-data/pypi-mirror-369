"""Define a mixin for the ``csv`` kind with the ``pyarrow`` engine."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel

from ..._suffix import get_compression_method_for
from ..compression import CompressionMixin
from ..engine.pyarrow import PyArrowEngineMixin
from ..kind.csv import CSVKindMixin

if TYPE_CHECKING:
    from pathlib import Path


class CSVPyArrowCompression(StrEnum):
    """Available compression methods for CSV files in PyArrow."""

    BZ2 = "bz2"
    BROTLI = "brotli"
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"


class DFCSVPyArrowMixin(
    CompressionMixin[CSVPyArrowCompression], CSVKindMixin, PyArrowEngineMixin, BaseModel
):
    """Mixin for handling CSV files with PyArrow engine."""

    @classmethod
    def get_compression_methods(cls) -> set[CSVPyArrowCompression | None]:
        """Get the available compression methods."""
        return {*CSVPyArrowCompression, None}

    def _get_compression_argument(self, path: Path):  # noqa: ANN202 (let mypy infer the type)
        if self.compression == "default":
            suffix = path.suffix
            compression_method = get_compression_method_for(suffix)
        else:
            compression_method = self.compression

        if compression_method is None:
            return None

        try:
            return CSVPyArrowCompression(compression_method).value
        except ValueError:
            # If the compression method is not valid, return None
            return None

    def get_compression_method(self):
        """Get the compression method for PyArrow."""
        compression = self.compression
        if isinstance(compression, CSVPyArrowCompression):
            return compression.value
        else:  # None or "default"
            return None
