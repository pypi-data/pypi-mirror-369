"""Define the protocol for a metric."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from pandas import DataFrame

    from ...io.reader import DFReaderBase
    from ...io.writer import DFWriterBase

__all__ = ["MetricBase"]

V_co = TypeVar("V_co", covariant=True)


class MetricBase(BaseModel, ABC, Generic[V_co]):
    """Base class for all metrics."""

    model_config = ConfigDict(extra="forbid")

    @abstractmethod
    def measure(
        self,
        dataframes: Mapping[str, DataFrame],
        paths: Path | Mapping[str, Path],
        dfwriter: DFWriterBase,
        dfreader: DFReaderBase,
    ) -> V_co:
        """Measure the performance of a specific operation."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the metric."""
