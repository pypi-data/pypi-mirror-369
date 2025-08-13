from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, TypeAlias

from ...core.types import Engine, Kind
from ._argument import IOArgument
from ._io import IOResult

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from ...core.registry import BackendKey, BackendRegistry
    from ...io.reader import DFReaderBase
    from ...io.writer import DFWriterBase
    from ._argument import WriterReaderArgumentInput
    from ._result import PerformanceResult

__all__ = ["BackendKeyInput", "loop_over_io_results"]

BackendKeyInput: TypeAlias = tuple[Kind, Engine]

logger = getLogger(__name__)


def _get_common_backend_keys(
    writer_registry: BackendRegistry[Any],
    reader_registry: BackendRegistry[Any],
) -> list[BackendKey]:
    writer_keys = list(writer_registry.keys())
    reader_keys = list(reader_registry.keys())
    return [key for key in writer_keys if key in reader_keys]


def _find_io_result(
    io_results: list[IOResult[DFWriterBase, DFReaderBase]],
    writer: DFWriterBase,
    reader: DFReaderBase,
) -> IOResult[DFWriterBase, DFReaderBase] | None:
    for result in io_results:
        if result.dfwriter == writer and result.dfreader == reader:
            logger.debug("Found existing IOResult")
            return result
    return None


def loop_over_io_results(
    performance_result: PerformanceResult[DFWriterBase, DFReaderBase],
    writer_registry: BackendRegistry[DFWriterBase],
    reader_registry: BackendRegistry[DFReaderBase],
    key_to_arguments: Mapping[BackendKeyInput, Sequence[WriterReaderArgumentInput]]
    | None = None,
) -> Iterable[IOResult[DFWriterBase, DFReaderBase]]:
    """Loop over configurations."""
    io_results = list(performance_result.results)

    if key_to_arguments is None:
        key_to_arguments = {
            backend_key: [IOArgument()]
            for backend_key in _get_common_backend_keys(
                writer_registry=writer_registry, reader_registry=reader_registry
            )
        }

    for (kind, engine), arguments in key_to_arguments.items():
        writer_cls = writer_registry.get(kind, engine)
        reader_cls = reader_registry.get(kind, engine)
        for argument_input in arguments:
            argument = IOArgument.from_any(argument_input)
            writer = writer_cls.model_validate(argument.dfwriter)
            reader = reader_cls.model_validate(argument.dfreader)

            io_result = _find_io_result(io_results, writer, reader)
            if io_result is None:
                io_result = IOResult(dfwriter=writer, dfreader=reader)
                performance_result.results.append(io_result)
            yield io_result
