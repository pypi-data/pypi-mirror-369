"""Measure the performance of IO classes."""

from __future__ import annotations

from . import metric
from ._measure import measure

__all__ = ["measure", "metric"]
