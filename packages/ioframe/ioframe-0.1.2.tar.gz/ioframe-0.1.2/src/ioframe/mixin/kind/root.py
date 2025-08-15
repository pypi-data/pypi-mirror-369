"""Define a mixin for the ``root`` kind."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from ...mixin.compression import CompressionMixin


class ROOTCompression(StrEnum):
    """Available compression methods for ROOT files."""

    LZ4 = "lz4"
    ZSTD = "zstd"
    ZLIB = "zlib"
    LZMA = "lzma"


ROOT_COMPRESSION_LEVELS: dict[ROOTCompression, int] = {
    ROOTCompression.ZLIB: 1,
    ROOTCompression.LZMA: 8,
    ROOTCompression.LZ4: 4,
    ROOTCompression.ZSTD: 5,
}
"""Compression levels of a ROOT file according to the chosen compression algorithm,

See https://root.cern/doc/master/Compression_8h_source.html for more details.
"""


class RootKindMixin(CompressionMixin[ROOTCompression]):
    """Mixin for Root I/O classes."""

    compression_level: int | None = None
    """Codec-specific compression level. None means default behavior."""

    @classmethod
    def get_compression_methods(cls) -> set[ROOTCompression | None]:
        return {*ROOTCompression, None}

    @classmethod
    def get_kind(cls) -> str:
        """Return the key used to identify this object in the registry."""
        return "root"

    @classmethod
    def is_compatible(cls, path: str | Path) -> bool:
        """Check if the backend is compatible with the given path."""
        return "".join(Path(path).suffixes) == ".root"

    def get_suffix(self) -> str:
        """Return the file extension for Root files."""
        return ".root"
