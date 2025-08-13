"""Define the mixin For ``csv`` kind and ``pandas`` engine."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

from ..._suffix import get_suffix_for, merge_suffixes
from ..compression import CompressionMixin
from ..engine.pandas import PandasEngineMixin
from ..kind.csv import CSVKindMixin


class CSVPandasCompression(StrEnum):
    """Available compression methods for CSV files with Pandas engine."""

    # Parametrizable compressions
    GZIP = "gzip"
    BZ2 = "bz2"
    ZSTD = "zstd"
    ZIP = "zip"
    # Non-parametrizable compressions
    XZ = "xz"
    TAR = "tar"


class ParametrizableCSVPandasCompression(StrEnum):
    """Parametrizable compression methods for CSV files with Pandas engine.

    These compression methods can be used as a dictionary to specify codec-specific
    options in the :py:attr:`CSVPandasMixin.compression` attribute
    through a :py:class:`CSVPandasCompressionDict`.
    """

    GZIP = "gzip"
    BZ2 = "bz2"
    ZSTD = "zstd"
    ZIP = "zip"


_COMPRESSION_LEVEL_PARAMETERS: dict[ParametrizableCSVPandasCompression, str] = {
    ParametrizableCSVPandasCompression.GZIP: "compresslevel",
    ParametrizableCSVPandasCompression.BZ2: "compresslevel",
    ParametrizableCSVPandasCompression.ZSTD: "level",
    ParametrizableCSVPandasCompression.ZIP: "compresslevel",
}


def _get_parametrizable(
    compression: CSVPandasCompression | Literal["default"] | None,
) -> ParametrizableCSVPandasCompression | None:
    if compression is None or compression == "default":
        return None
    try:
        return ParametrizableCSVPandasCompression(compression)
    except ValueError:
        return None


class CSVPandasMixin(
    CompressionMixin[CSVPandasCompression],
    CSVKindMixin,
    PandasEngineMixin,
    BaseModel,
):
    """Mixin for handling CSV files with Pandas engine."""

    compression_level: int | None = None
    """Compression level for the compression codec."""

    compression_params: dict[str, Any] = Field(default_factory=dict)
    """Other compression parameters for the compression codec."""

    @model_validator(mode="after")
    def _validate_compression(self) -> Self:
        if not _get_parametrizable(self.compression):
            if self.compression_level is not None:
                msg = f"Compression level is not supported for {self.compression}"
                raise ValueError(msg)
            if self.compression_params:
                msg = f"Compression parameters are not supported for {self.compression}"
                raise ValueError(msg)

        return self

    @classmethod
    def get_compression_methods(cls) -> set[CSVPandasCompression | None]:
        return {*CSVPandasCompression, None}

    def _get_compression_params(self) -> dict[str, Any] | None:
        compression = self.compression
        parametrizable_compression = _get_parametrizable(compression)

        if not parametrizable_compression:
            return None

        params: dict[str, Any] = (
            {
                _COMPRESSION_LEVEL_PARAMETERS[
                    parametrizable_compression
                ]: compression_level
            }
            if (compression_level := self.compression_level) is not None
            else {}
        )
        if compression_params := self.compression_params:
            params.update(compression_params)

        if not params:
            return None

        params["method"] = parametrizable_compression.value
        return params

    def _get_compression_argument(self):  # noqa: ANN202  (let mypy infer the type)
        """Get the compression argument for Pandas."""
        if (compression_params := self._get_compression_params()) is not None:
            return compression_params

        compression = self.compression
        if isinstance(compression, CSVPandasCompression):
            return compression.value
        elif compression == "default":
            return "infer"
        elif compression is None:
            return None
        else:  # pragma: no cover
            msg = (
                "Couldn't get the compression parameters for compression "
                f"{compression}. "
                "This is a bug."
            )
            raise RuntimeError(msg)

    def get_compression_method(self):
        """Get the actual compression, used for getting the suffix."""
        compression = self.compression
        if isinstance(compression, CSVPandasCompression):
            return compression.value
        else:  # None or "default"
            return compression

    def get_suffix(self) -> str:
        return merge_suffixes(".csv", get_suffix_for(self.get_compression_method()))
