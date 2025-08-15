"""Define the writer for the ``hdf5`` kind."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Any, Literal, TypedDict
from warnings import warn

from pydantic import Field

from ..io.writer import HierarchicalDFWriterBase
from ..mixin.compression import CompressionMixin
from ..mixin.engine.pytables import PyTablesEngineMixin
from ..mixin.kind.hdf5 import HDF5KindMixin

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from pandas import DataFrame
    from pandas._typing import HDFCompLib


__all__ = ["DFHDF5Writer"]


class HDF5Compression(StrEnum):
    """Compression options for HDF files."""

    ZLIB = "zlib"
    BZIP2 = "bzip2"
    BLOSC = "blosc"
    BLOSC2 = "blosc2"


class _HDF5CompressionDict(TypedDict, total=False):
    complib: HDFCompLib
    """Compression library to use."""
    complevel: int
    """Compression level to use."""


class DFHDF5Writer(
    CompressionMixin[HDF5Compression],
    HDF5KindMixin,
    PyTablesEngineMixin,
    HierarchicalDFWriterBase,
):
    """HDF Writer backed by **Pandas**.

    By default, ``index=False`` is used when writing HDF files.
    """

    compression_level: Annotated[int, Field(ge=0, le=9)] = 5
    """Compression level to use when writing HDF files. Must be between 0 and 9."""

    format: Literal["table", "fixed"] | None = None
    """HDF format to use when writing dataframes.

    If ``None``, default to ``fixed`` if no compression, ``table`` otherwise.
    """

    @property
    def table_format(self) -> Literal["table", "fixed"]:
        if self.format is None:
            return "fixed" if self.compression is None else "table"
        return self.format

    @classmethod
    def get_compression_methods(cls) -> set[HDF5Compression | None]:
        return {*HDF5Compression, None}

    def _get_compression_arguments(self) -> _HDF5CompressionDict:
        compression = self.compression
        if compression == "default":  # default is no compression
            return {}
        elif compression is None:
            return {"complevel": 0}
        else:
            return {
                "complib": compression.value,  # type: ignore[union-attr, typeddict-item] # mypy fails to narrow
                "complevel": self.compression_level,
            }

    def _write(
        self, dataframes: Mapping[str, DataFrame], path: Path, **kwargs: Any
    ) -> None:
        from pandas import HDFStore  # noqa: PLC0415

        compression_kwargs_ = self._get_compression_arguments()
        with HDFStore(path, mode="w") as store:
            for key, dataframe in dataframes.items():
                hdf5_format = self.table_format
                compression_kwargs = compression_kwargs_
                if dataframe.empty and hdf5_format == "table":
                    warn(
                        (
                            "Dataframe is empty: Switching to format 'fixed'. "
                            "and disabling compression."
                        ),
                        UserWarning,
                        stacklevel=2,
                    )
                    hdf5_format = "fixed"
                    compression_kwargs = {"complevel": 0}

                store.put(
                    key,
                    dataframe,
                    format=hdf5_format,
                    data_columns=True,
                    **compression_kwargs,
                    **kwargs,
                )
