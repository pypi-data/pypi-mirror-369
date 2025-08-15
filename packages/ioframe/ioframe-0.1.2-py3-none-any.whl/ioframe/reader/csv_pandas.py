"""Define the reader for the ``csv`` kind and ``pandas`` engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..io.reader import SingleDFReaderBase
from ..mixin.kind_engine.csv_pandas import CSVPandasMixin

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame


__all__ = ["DFCSVPandasReader"]


class DFCSVPandasReader(CSVPandasMixin, SingleDFReaderBase):
    """CSV Reader backed by **Pandas**."""

    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        from pandas import read_csv  # noqa: PLC0415

        return read_csv(
            path,
            usecols=columns,
            compression=self._get_compression_argument(),
            **kwargs,
        )
