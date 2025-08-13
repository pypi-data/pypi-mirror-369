from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

from pandas import DataFrame

from ..io.reader import HierarchicalDFReaderBase
from ..io.writer import HierarchicalDFWriterBase
from ..reader import reader_registry as default_reader_registry
from ..writer import writer_registry as default_writer_registry
from .config import BackendKeyInput, load_performance_results, loop_over_io_results
from .metric import get_default_metrics

if TYPE_CHECKING:
    from ..core.registry import BackendRegistry
    from ..io.reader import DFReaderBase
    from ..io.writer import DFWriterBase
    from .config import IOResult, PerformanceResult, WriterReaderArgumentInput
    from .metric._base import MetricBase

logger = getLogger(__name__)


def _normalize_dataframes(
    dataframes: DataFrame | Sequence[DataFrame] | Mapping[str, DataFrame],
) -> dict[str, DataFrame]:
    """Normalize input dataframes into a dictionary of dataframes."""
    if isinstance(dataframes, DataFrame):
        return {"dataframe": dataframes}
    elif isinstance(dataframes, Sequence):
        return {str(idx): df for idx, df in enumerate(dataframes)}
    elif isinstance(dataframes, Mapping):
        return dict(dataframes.items())
    else:
        msg = (
            "Invalid dataframes type. "
            "Expected a DataFrame, a sequence of DataFrames, "
            "or a mapping of string to DataFrame. "
            f"Got {type(dataframes)}."
        )
        raise TypeError(msg)


def _get_paths(
    directory: str | Path,
    keys: Iterable[str],
    io_result: IOResult[DFWriterBase, DFReaderBase],
) -> Path | Mapping[str, Path]:
    """Get the path for the DataFrame writer."""
    directory = Path(directory)
    if isinstance(io_result.dfwriter, HierarchicalDFWriterBase):
        if not isinstance(
            io_result.dfreader, HierarchicalDFReaderBase
        ):  # pragma: no cover
            msg = (
                f"Writer {io_result.dfwriter.__class__.__name__!r} is hierarchical "
                f"but reader {io_result.dfreader.__class__.__name__!r} is not."
            )
            raise TypeError(msg)
        return io_result.dfwriter.resolve_path(directory / "single")
    else:
        if isinstance(io_result.dfreader, HierarchicalDFReaderBase):  # pragma: no cover
            msg = (
                f"Writer {io_result.dfwriter.__class__.__name__!r} is not hierarchical "
                f"but reader {io_result.dfreader.__class__.__name__!r} is."
            )
            raise TypeError(msg)

        return {key: io_result.dfwriter.resolve_path(directory / key) for key in keys}


def _measure_metric(
    metric: MetricBase[Any],
    dataframes: Mapping[str, DataFrame],
    paths: Path | Mapping[str, Path],
    writer: DFWriterBase,
    reader: DFReaderBase,
    *,
    results: dict[str, Any],
) -> None:
    """Measure a single metric."""
    metric_name = metric.get_name()
    if metric_name in results:
        logger.info("Metric '%s' already measured.", metric_name)
        return

    logger.info("Measuring metric '%s'.", metric.get_name())
    try:
        result = metric.measure(dataframes, paths, writer, reader)
    except KeyboardInterrupt:
        raise
    except Exception:
        logger.exception("Error measuring metric '%s'", metric.get_name())
    else:
        logger.debug("Metric '%s' result: %s", metric.get_name(), result)
        results[metric_name] = result


def _measure_metrics(
    dataframes: Mapping[str, DataFrame],
    io_result: IOResult[DFWriterBase, DFReaderBase],
    metrics: Sequence[MetricBase[Any]],
) -> None:
    """Measure multiple metrics."""
    with TemporaryDirectory() as temp_dir_:
        paths = _get_paths(temp_dir_, dataframes.keys(), io_result)

        for metric in metrics:
            _measure_metric(
                metric,
                dataframes,
                paths,
                io_result.dfwriter,
                io_result.dfreader,
                results=io_result.result,
            )


def measure(
    dataframes: DataFrame | Sequence[DataFrame] | Mapping[str, DataFrame],
    key_to_arguments: Mapping[BackendKeyInput, Sequence[WriterReaderArgumentInput]]
    | None = None,
    path: str | Path | None = None,
    *,
    metrics: Sequence[MetricBase[Any]] | None = None,
    writer_registry: BackendRegistry[DFWriterBase] = default_writer_registry,
    reader_registry: BackendRegistry[DFReaderBase] = default_reader_registry,
) -> PerformanceResult[DFWriterBase, DFReaderBase]:
    """Measure performance of configurations.

    Args:
        dataframes: The dataframes to measure.
        key_to_arguments: The mapping of backend keys to writer/reader arguments.
        path: The path to the JSON file where results will be saved.
        metrics: The metrics to use for measurement.
        writer_registry: The writer registry to use.
        reader_registry: The reader registry to use.
    """
    path = Path(path) if path else None
    dataframes = _normalize_dataframes(dataframes)

    if metrics is None:
        metrics = get_default_metrics()

    performance_result = load_performance_results(
        path, writer_registry=writer_registry, reader_registry=reader_registry
    )

    try:
        for io_result in loop_over_io_results(
            performance_result,
            writer_registry,
            reader_registry,
            key_to_arguments=key_to_arguments,
        ):
            logger.info(
                "Testing writer=%r with reader=%r",
                io_result.dfwriter,
                io_result.dfreader,
            )
            _measure_metrics(
                dataframes=dataframes,
                io_result=io_result,
                metrics=metrics,
            )
            if path is not None:
                performance_result.to_json(path)
    except KeyboardInterrupt:
        logger.info("Measurement interrupted.")

    return performance_result
