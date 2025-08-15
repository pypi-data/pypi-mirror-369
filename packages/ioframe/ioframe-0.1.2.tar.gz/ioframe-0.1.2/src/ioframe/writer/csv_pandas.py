"""Define the writer for the ``csv`` kind and ``pandas`` engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..io.writer import SingleDFWriterBase
from ..mixin.kind_engine.csv_pandas import CSVPandasMixin

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame


__all__ = ["DFCSVPandasWriter"]


class DFCSVPandasWriter(CSVPandasMixin, SingleDFWriterBase):
    """CSV Writer backed by **Pandas**.

    By default, ``index=False`` is used when writing CSV files.
    """

    def _write(self, df: DataFrame, path: Path, **kwargs: Any) -> None:
        kwargs.setdefault("index", False)

        df.to_csv(path, compression=self._get_compression_argument(), **kwargs)
