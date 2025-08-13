"""Define read and write time metrics."""

from __future__ import annotations

from logging import getLogger
from math import ceil
from timeit import Timer
from typing import TYPE_CHECKING, Annotated, Any, TypeVar

from pydantic import Field

from ._base import MetricBase
from ._io import read_mapping, write_mapping

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from pathlib import Path

    from pandas import DataFrame

    from ...io.reader import DFReaderBase
    from ...io.writer import DFWriterBase

logger = getLogger(__name__)

_DEFAULT_MIN_TIME = 0.2

V = TypeVar("V")


def _custom_autorange(
    func: Callable[[], Any], *, time_per_repeat: float = _DEFAULT_MIN_TIME
) -> tuple[int, float, float]:
    timer = Timer(func)
    n_loops, total = timer.autorange()
    time_per_loop = total / n_loops
    if time_per_repeat != _DEFAULT_MIN_TIME:
        # scale up or down
        n_loops = ceil(time_per_repeat / time_per_loop)
        total = n_loops * time_per_loop

    return n_loops, total, time_per_loop


class TimeMetricBase(MetricBase[V]):
    """Base model for time metrics."""

    repeats: Annotated[int, Field(ge=1)] = 5
    """Number of times the ``time`` function is repeated."""

    time_per_repeat: Annotated[float, Field(gt=0)] = _DEFAULT_MIN_TIME
    """Minimum time for each repeat in seconds."""

    max_time: Annotated[float, Field(ge=0)] | None = None
    """Maximum time overall.

    If this parameter is set, the number of repeats will be adjusted
    to ensure the total time does not exceed this value.
    """

    def _time(self, func: Callable[[], Any], /) -> float:
        """Measure the time taken for a specific operation.

        Args:
            func: The function to time.

        Returns:
            Best time taken for the operation.
        """
        n_loops, total, time_per_loop = _custom_autorange(
            func, time_per_repeat=self.time_per_repeat
        )

        repeats = self.repeats
        if (max_time := self.max_time) is not None and total * repeats > max_time:
            repeats = round(max_time / total)
        if repeats == 0:
            # directly return the time per loop
            return time_per_loop

        logger.info("Timing with %d repeats of %d loops", repeats, n_loops)
        timer = Timer(func)
        times = timer.repeat(repeat=repeats, number=n_loops)
        return min(times)


class WriteTimeMetric(TimeMetricBase[float]):
    """Write time metric."""

    def measure(
        self,
        dataframes: Mapping[str, DataFrame],
        paths: Path | Mapping[str, Path],
        dfwriter: DFWriterBase,
        dfreader: DFReaderBase,  # noqa: ARG002
    ) -> float:
        """Measure the write time of the dataframe writer.

        Args:
            dataframes: The dataframes to write.
            paths: The paths to write the dataframes to.
            dfwriter: The dataframe writer.
            dfreader: The dataframe reader.

        Returns:
            Best write time for writing the dataframes.
        """
        return self._time(lambda: write_mapping(dataframes, paths, dfwriter))

    def get_name(self) -> str:
        return "write_time"


class ReadTimeMetric(TimeMetricBase[float]):
    """Read time metric."""

    def measure(
        self,
        dataframes: Mapping[str, DataFrame],
        paths: Path | Mapping[str, Path],
        dfwriter: DFWriterBase,
        dfreader: DFReaderBase,
    ) -> float:
        """Measure the read time of the dataframe reader.

        Args:
            dataframes: The dataframes to read.
            paths: The paths to read the dataframes from.
            dfwriter: The dataframe writer.
            dfreader: The dataframe reader.

        Returns:
            Best read time for reading the dataframes.
        """
        # Write the dataframe to disk once
        write_mapping(dataframes, paths, dfwriter, override=False)
        # Measure the read time
        return self._time(lambda: read_mapping(paths, dfreader))

    def get_name(self) -> str:
        return "read_time"
