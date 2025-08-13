"""Define the reader for the ``feather`` kind."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..io.reader import SingleDFReaderBase
from ..mixin.engine.pyarrow import PyArrowEngineMixin
from ..mixin.kind.feather import FeatherKindMixin

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame

__all__ = ["DFFeatherReader"]


class DFFeatherReader(FeatherKindMixin, PyArrowEngineMixin, SingleDFReaderBase):
    """Feather Reader backed by **PyArrow**."""

    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        from pandas import read_feather  # noqa: PLC0415

        return read_feather(path, columns=columns, **kwargs)
