"""Define the reader for the ``hdf5`` kind."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from ..io.reader import HierarchicalDFReaderBase
from ..mixin.engine.pytables import PyTablesEngineMixin
from ..mixin.kind.hdf5 import HDF5KindMixin

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from pandas import DataFrame

__all__ = ["DFHDF5Reader"]


class DFHDF5Reader(HDF5KindMixin, PyTablesEngineMixin, HierarchicalDFReaderBase):
    """HDF Reader backed by **Pandas**."""

    def _read(
        self,
        path: Path,
        key_to_columns: Mapping[str, list[str] | None] | None = None,
        **kwargs: Any,
    ) -> dict[str, DataFrame]:
        from pandas import HDFStore  # noqa: PLC0415

        with HDFStore(path, mode="r", **kwargs) as store:
            if key_to_columns is None:
                key_to_columns = dict.fromkeys(key.lstrip("/") for key in store)
            dataframes = {
                key: store[key][columns] if columns is not None else store[key]
                for key, columns in key_to_columns.items()
            }

        return cast("dict[str, DataFrame]", dataframes)
