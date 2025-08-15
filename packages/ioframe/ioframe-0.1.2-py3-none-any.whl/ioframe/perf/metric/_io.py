"""An I/O utility module to write and read DataFrames."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from ioframe.io.reader import DFReaderBase, HierarchicalDFReaderBase, SingleDFReaderBase
from ioframe.io.writer import DFWriterBase, HierarchicalDFWriterBase, SingleDFWriterBase

if TYPE_CHECKING:
    from pathlib import Path

    from pandas import DataFrame


def paths_exist(paths: Path | Mapping[str, Path]) -> bool:
    """Check if the given paths exist.

    Args:
        paths: A path or a mapping of DataFrame names to their paths.

    Returns:
        True if all paths exist, False otherwise.
    """
    if isinstance(paths, Mapping):
        return all(path.exists() for path in paths.values())
    return paths.exists()


def write_mapping(
    dataframes: Mapping[str, DataFrame],
    paths: Path | Mapping[str, Path],
    dfwriter: DFWriterBase,
    *,
    override: bool = True,
) -> None:
    """Write the given DataFrames using the specified DataFrame writer.

    Args:
        dataframes: The DataFrames to write.
        paths: The paths to write the DataFrames to.
        dfwriter: The DataFrame writer to use.
        override: Whether to override existing files.
    """
    if override or not paths_exist(paths):
        if isinstance(paths, Mapping):
            assert isinstance(dfwriter, SingleDFWriterBase)
            for dfname, path in paths.items():
                dfwriter.write(dataframes[dfname], path)
        else:
            assert isinstance(dfwriter, HierarchicalDFWriterBase)
            dfwriter.write(dataframes, paths)


def read_mapping(
    paths: Path | Mapping[str, Path], dfreader: DFReaderBase
) -> dict[str, DataFrame]:
    """Read DataFrames from the specified paths using the given DataFrame reader.

    Args:
        dfreader: The DataFrame reader to use.
        paths: A mapping of DataFrame names to their paths.

    Returns:
        A mapping of DataFrame names to the DataFrames read from the specified paths.
    """
    if isinstance(paths, Mapping):
        assert isinstance(dfreader, SingleDFReaderBase)
        return {dfname: dfreader.read(path) for dfname, path in paths.items()}
    else:
        assert isinstance(dfreader, HierarchicalDFReaderBase)
        return dfreader.read_mapping(paths)
