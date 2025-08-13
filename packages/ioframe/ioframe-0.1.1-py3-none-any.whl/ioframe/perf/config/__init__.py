"""Define the performance configuration and results."""

from __future__ import annotations

from ._argument import IOArgument, WriterReaderArgumentInput
from ._io import IOResult
from ._loop import BackendKeyInput, loop_over_io_results
from ._result import PerformanceResult, load_performance_results

__all__ = [
    "BackendKeyInput",
    "IOArgument",
    "IOResult",
    "PerformanceResult",
    "WriterReaderArgumentInput",
    "load_performance_results",
    "loop_over_io_results",
]
