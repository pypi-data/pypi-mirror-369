"""Define the size metrics."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from ._base import MetricBase
from ._io import write_mapping

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from pandas import DataFrame

    from ...io.reader import DFReaderBase
    from ...io.writer import DFWriterBase


def _get_size_in_paths(paths: Iterable[Path]) -> int:
    """Return the sum of the sizes of the files in the given paths, in bytes."""
    return sum(path.stat().st_size for path in paths)


class SizeMetric(MetricBase[int]):
    """Measure the total size of the files written by the DataFrame writer."""

    def measure(
        self,
        dataframes: Mapping[str, DataFrame],
        paths: Path | Mapping[str, Path],
        dfwriter: DFWriterBase,
        dfreader: DFReaderBase,  # noqa: ARG002
    ) -> int:
        write_mapping(dataframes, paths, dfwriter, override=False)
        return _get_size_in_paths(
            paths.values() if isinstance(paths, Mapping) else [paths]
        )

    def get_name(self) -> str:
        return "size"
