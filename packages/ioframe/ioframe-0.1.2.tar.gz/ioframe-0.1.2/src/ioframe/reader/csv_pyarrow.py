"""Define the reader for the ``csv`` kind and ``pyarrow`` engine."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any

from pyarrow import CompressedInputStream

from ..io.reader import SingleDFReaderBase
from ..mixin.kind_engine.csv_pyarrow import DFCSVPyArrowMixin

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame
    from pyarrow.csv import ConvertOptions

__all__ = ["DFCSVPyArrowReader"]


class DFCSVPyArrowReader(DFCSVPyArrowMixin, SingleDFReaderBase):
    """CSV I/O backed by **PyArrow**."""

    def _get_convert_options(
        self,
        columns: list[str] | None,
        convert_options: ConvertOptions | Mapping[str, Any] | None,
    ) -> ConvertOptions:
        from pyarrow.csv import ConvertOptions  # noqa: PLC0415

        if convert_options is None:
            convert_options = ConvertOptions(include_columns=columns)
        elif isinstance(convert_options, Mapping):
            convert_options = ConvertOptions(include_columns=columns, **convert_options)
        elif isinstance(convert_options, ConvertOptions):
            convert_options.include_columns = columns
        else:
            msg = f"Invalid convert_options type: {type(convert_options)}"
            raise TypeError(msg)
        return convert_options

    def _read(
        self, path: Path, columns: list[str] | None = None, **kwargs: Any
    ) -> DataFrame:
        from pyarrow.csv import read_csv  # noqa: PLC0415

        pyarrow_compression = self._get_compression_argument(path)

        convert_options = self._get_convert_options(
            columns, kwargs.pop("convert_options", None)
        )
        with (
            CompressedInputStream(path, compression=pyarrow_compression)
            if pyarrow_compression
            else nullcontext(path)
        ) as input_file:
            table = read_csv(
                input_file,  # type: ignore[arg-type]
                convert_options=convert_options,
                **kwargs,
            )
        return table.to_pandas()
