from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from ...io.reader import DFReaderBase
from ...io.writer import DFWriterBase

__all__ = ["IOResult", "R", "W"]

W = TypeVar("W", bound=DFWriterBase)
R = TypeVar("R", bound=DFReaderBase)


class IOResult(BaseModel, Generic[W, R]):
    """Input/Output configuration for DataFrames."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    dfwriter: W
    """DataFrame writer."""

    dfreader: R
    """DataFrame reader."""

    result: dict[str, Any] = Field(default_factory=dict)
    """Performnance results of these IOs."""
