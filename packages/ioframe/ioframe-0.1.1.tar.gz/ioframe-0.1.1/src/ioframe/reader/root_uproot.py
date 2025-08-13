"""Define the reader for the ``root`` kind and ``uproot`` engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, cast

from pydantic import Field

from ..io.reader import HierarchicalDFReaderBase
from ..mixin.engine.uproot import UpRootEngineMixin
from ..mixin.kind.root import RootKindMixin

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from pandas import DataFrame
    from uproot.source.futures import Executor

__all__ = ["DFROOTUpRootReader"]


def get_executor(n_workers: int | None) -> Executor:
    """Get the executor for reading."""
    from uproot.source.futures import (  # noqa: PLC0415
        ThreadPoolExecutor,
        TrivialExecutor,
    )

    if n_workers == 1:
        return TrivialExecutor()
    elif n_workers is None or n_workers > 1:
        return ThreadPoolExecutor(n_workers)
    else:  # pragma: no cover
        msg = (
            "Invalid number of workers specified. "
            "Please provide a positive integer or None for default behavior."
        )
        raise ValueError(msg)


def _get_key_from_treename(key: str) -> str:
    return key.rsplit(";", 1)[0]


def _replace_awkward_dtypes(dataframe: DataFrame) -> None:
    """Replace awkward dtypes with object dtypes."""
    for col in dataframe.columns:
        if dataframe[col].dtype == "awkward":
            dataframe[col] = dataframe[col].to_numpy()


class DFROOTUpRootReader(RootKindMixin, UpRootEngineMixin, HierarchicalDFReaderBase):
    """ROOT Reader backed by **Uproot**."""

    n_workers: Annotated[int, Field(ge=1)] | None = None
    """Number of workers to use for reading.

    If ``None``, all available cores are used.
    """

    decompression_n_workers: Annotated[int, Field(ge=1)] | None = 1
    """Number of workers to use for decompression."""

    drop_index: bool = True
    """Whether to drop the index column from the DataFrame."""

    def _read(
        self,
        path: Path,
        key_to_columns: Mapping[str, list[str] | None] | None = None,
        **kwargs: Any,
    ) -> dict[str, DataFrame]:
        from uproot.behaviors.TTree import TTree  # noqa: PLC0415
        from uproot.reading import open as uproot_open  # noqa: PLC0415

        with uproot_open(
            path,
            interpretation_executor=get_executor(self.n_workers),
            decompression_executor=get_executor(self.decompression_n_workers),
            **kwargs,
        ) as file:
            if key_to_columns is None:
                key_to_columns = {
                    _get_key_from_treename(tree_name): None
                    for tree_name, tree in file.items()
                    if isinstance(tree, TTree)
                }

            dataframes = {
                key: cast(
                    "DataFrame",
                    file[key].arrays(library="pandas", expressions=columns),
                )
                for key, columns in key_to_columns.items()
            }

        for key, dataframe in dataframes.items():
            self._warns_empty(dataframe=dataframe)
            _replace_awkward_dtypes(dataframe)
            if self.drop_index and "index" in dataframe.columns:
                dataframes[key] = dataframe.drop(columns=["index"], axis=1)

        return dataframes
