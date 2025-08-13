"""Define the writer for the ``root`` kind and ``uproot`` engine."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any

from ..io.writer import HierarchicalDFWriterBase
from ..mixin.engine.uproot import UpRootEngineMixin
from ..mixin.kind.root import ROOT_COMPRESSION_LEVELS, ROOTCompression, RootKindMixin

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from pandas import DataFrame
    from uproot.compression import Compression

__all__ = ["DFROOTUpRootWriter"]


@lru_cache(maxsize=1)
def _get_uproot_compressions() -> dict[str, type[Compression]]:
    """Get the available compression codecs."""
    from uproot.compression import LZ4, LZMA, ZLIB, ZSTD  # noqa: PLC0415

    return {
        ROOTCompression.LZ4: LZ4,
        ROOTCompression.ZSTD: ZSTD,
        ROOTCompression.ZLIB: ZLIB,
        ROOTCompression.LZMA: LZMA,
    }


def _get_uproot_compression(
    compression: ROOTCompression | None,
    level: int | None = None,
) -> Compression | None:
    """Get the Uproot compression object based on the specified codec."""
    codecs = _get_uproot_compressions()
    if compression is None:
        return None

    try:
        codec_cls = codecs[compression]
    except KeyError as e:  # pragma: no cover (not reachable)
        msg = (
            f"Unsupported compression codec: {compression}. "
            "Supported codecs are: " + ", ".join(codecs.keys())
        )
        raise ValueError(msg) from e

    return codec_cls(
        level=(
            level if level is not None else ROOT_COMPRESSION_LEVELS.get(compression, 1)
        )
    )


class DFROOTUpRootWriter(RootKindMixin, UpRootEngineMixin, HierarchicalDFWriterBase):
    """ROOT Writer backed by **Uproot**."""

    def _write(
        self, dataframes: Mapping[str, DataFrame], path: Path, **kwargs: Any
    ) -> None:
        from uproot.writing.writable import recreate  # noqa: PLC0415

        compression = self.compression
        if "compression" not in kwargs and compression != "default":
            kwargs["compression"] = _get_uproot_compression(
                compression,  # type: ignore[arg-type]
                self.compression_level,
            )

        with recreate(path, **kwargs) as file:
            for tree_name, dataframe in dataframes.items():
                self._warns_empty(dataframe=dataframe)
                file[tree_name] = dataframe

    def get_suffix(self) -> str:
        return ".root"
