from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic

from pydantic import BaseModel, ConfigDict, Field

from ._io import IOResult, R, W
from ._stats import MachineSpecDict, get_machine_spec

if TYPE_CHECKING:
    from ...core.registry import BackendRegistry
    from ...io.reader import DFReaderBase
    from ...io.writer import DFWriterBase

__all__ = ["PerformanceResult", "load_performance_results"]

logger = getLogger(__name__)


class PerformanceResult(BaseModel, Generic[W, R]):
    """Performance results for various writers and readers."""

    model_config = ConfigDict(extra="forbid")

    machine: MachineSpecDict = Field(default_factory=get_machine_spec)
    """Machine specifications."""

    results: list[IOResult[W, R]] = Field(default_factory=list[IOResult[W, R]])
    """Performance results."""

    def to_json(self, path: str | Path, **kwargs: Any) -> None:
        """Convert the performance results to JSON format."""
        path = Path(path).expanduser().resolve()
        kwargs.setdefault("indent", 2)
        path.write_text(self.model_dump_json(**kwargs))


def load_performance_results(
    path: Path | None = None,
    *,
    writer_registry: BackendRegistry[DFWriterBase] | None = None,
    reader_registry: BackendRegistry[DFReaderBase] | None = None,
) -> PerformanceResult[DFWriterBase, DFReaderBase]:
    if writer_registry is None:
        from ...writer import (  # noqa: PLC0415
            writer_registry as default_writer_registry,
        )

        writer_registry = default_writer_registry

    if reader_registry is None:
        from ...reader import (  # noqa: PLC0415
            reader_registry as default_reader_registry,
        )

        reader_registry = default_reader_registry

    writer_type = writer_registry.discriminated_union
    reader_type = reader_registry.discriminated_union
    typed_perf_result_cls = PerformanceResult[writer_type, reader_type]  # type: ignore[valid-type]

    if path is None or not path.exists():
        return typed_perf_result_cls()
    result = typed_perf_result_cls.model_validate_json(path.read_text())
    logger.info("Loaded performance results from %s", path)
    return result
