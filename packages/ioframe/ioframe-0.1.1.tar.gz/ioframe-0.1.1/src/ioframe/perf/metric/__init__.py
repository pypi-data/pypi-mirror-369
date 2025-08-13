"""A package that defines performance metrics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import MetricBase
from ._size import SizeMetric
from ._time import ReadTimeMetric, WriteTimeMetric

if TYPE_CHECKING:
    from collections.abc import Sequence


__all__ = [
    "MetricBase",
    "ReadTimeMetric",
    "SizeMetric",
    "WriteTimeMetric",
    "get_default_metrics",
]


def get_default_metrics() -> Sequence[MetricBase[Any]]:
    """Get default performance metrics."""
    return [WriteTimeMetric(), ReadTimeMetric(), SizeMetric()]
