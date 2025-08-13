"""Define the writer for the ``root`` kind and ``pyroot`` engine."""

from __future__ import annotations

from functools import lru_cache
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import ConfigDict

from ..io.writer import HierarchicalDFWriterBase
from ..mixin.engine.pyroot import PyROOTEngineMixin
from ..mixin.kind.root import ROOT_COMPRESSION_LEVELS, ROOTCompression, RootKindMixin

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from pandas import DataFrame


__all__ = ["DFROOTPyRootWriter"]

logger = getLogger(__name__)


@lru_cache(maxsize=1)
def _get_codecs() -> dict[ROOTCompression, int]:
    """Get the available compression codecs."""
    from ROOT import kLZ4, kLZMA, kZLIB, kZSTD  # noqa: PLC0415

    return {
        ROOTCompression.ZLIB: kZLIB,
        ROOTCompression.LZMA: kLZMA,
        ROOTCompression.LZ4: kLZ4,
        ROOTCompression.ZSTD: kZSTD,
    }


def _get_compression_algorithm(compression: ROOTCompression) -> int:
    """Get the ROOT compression algorithm based on the specified codec."""
    codecs = _get_codecs()
    try:
        return codecs[compression]
    except KeyError as e:  # pragma: no cover (not reachable)
        msg = (
            f"Unsupported compression codec: {compression}. "
            "Supported codecs are: " + ", ".join(codecs.keys())
        )
        raise ValueError(msg) from e


class DFROOTPyRootWriter(RootKindMixin, PyROOTEngineMixin, HierarchicalDFWriterBase):
    """ROOT Reader backed by **Uproot**."""

    model_config = ConfigDict(extra="forbid")

    auto_flush: int = 0
    """Whether to automatically flush the ROOT file after writing."""

    overwrite_if_exists: bool = False
    """If mode is ``"UPDATE"``, whether to overwrite object if it exists."""

    split_level: int = 99
    """Split level for the ROOT tree."""

    def _get_rnsnapshot_options(self) -> object:
        """Get the ROOT RSnapshotOptions for writing."""
        from ROOT.RDF import RSnapshotOptions  # noqa: PLC0415

        rsnapshotoptions = RSnapshotOptions()
        compression = self.compression
        if compression is None:
            rsnapshotoptions.fCompressionLevel = 0
        elif compression == "default":
            pass
        else:
            compression = ROOTCompression(compression)  # sanity check
            rsnapshotoptions.fCompressionLevel = (
                compression_level
                if (compression_level := self.compression_level) is not None
                else ROOT_COMPRESSION_LEVELS[compression]
            )
            rsnapshotoptions.fCompressionAlgorithm = _get_compression_algorithm(
                compression
            )

        rsnapshotoptions.fAutoFlush = self.auto_flush
        rsnapshotoptions.fMode = "UPDATE"
        rsnapshotoptions.fOverwriteIfExists = self.overwrite_if_exists
        rsnapshotoptions.fSplitLevel = self.split_level
        return rsnapshotoptions

    def _write(
        self, dataframes: Mapping[str, DataFrame], path: Path, **kwargs: Any
    ) -> None:
        from ROOT.RDF import FromPandas  # noqa: PLC0415

        # delete path if it exists
        path.unlink(missing_ok=True)

        if kwargs:
            msg = (
                "Additional keyword arguments are not supported "
                f"for {self.__class__.__name__}. "
                "Got :" + ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            )
            raise ValueError(msg)

        rsnapshotoptions = self._get_rnsnapshot_options()

        for key, dataframe in dataframes.items():
            logger.debug("Writing '%s' dataframe to ROOT file: '%s'", key, path)
            rdataframe = FromPandas(dataframe)
            rdataframe.Snapshot(key, path.as_posix(), "", rsnapshotoptions)
