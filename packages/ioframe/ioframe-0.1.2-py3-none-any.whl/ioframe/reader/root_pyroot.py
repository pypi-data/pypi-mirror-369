"""Define the reader for the ``root`` kind and ``pyroot`` engine."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pandas import DataFrame
from pydantic import ConfigDict

from ..io.reader import HierarchicalDFReaderBase
from ..mixin.engine.pyroot import PyROOTEngineMixin
from ..mixin.kind.root import RootKindMixin

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

__all__ = ["DFROOTPyRootReader"]


def _get_tree_names(path: str | Path) -> list[str]:
    from ROOT import TFile  # noqa: PLC0415

    rfile = TFile(str(path))
    return [
        key.GetName() for key in rfile.GetListOfKeys() if key.GetClassName() == "TTree"
    ]


def _load_dataframe(
    path: str | Path, tree_name: str, columns: list[str] | None
) -> DataFrame:
    from ROOT import RDataFrame  # noqa: PLC0415

    rdataframe = RDataFrame(tree_name, str(path))
    arrays = rdataframe.AsNumpy(columns=columns)
    return DataFrame(arrays)


class DFROOTPyRootReader(RootKindMixin, PyROOTEngineMixin, HierarchicalDFReaderBase):
    """ROOT Reader backed by **Uproot**."""

    model_config = ConfigDict(extra="forbid")

    def _read(
        self,
        path: Path,
        key_to_columns: Mapping[str, list[str] | None] | None = None,
        **kwargs: Any,
    ) -> dict[str, DataFrame]:
        if kwargs:
            msg = (
                "Additional keyword arguments are not supported "
                f"for {self.__class__.__name__}. "
                "Got :" + ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
            )
            raise ValueError(msg)

        if key_to_columns is None:
            # get all the tree names from the ROOT files
            key_to_columns = dict.fromkeys(_get_tree_names(path), None)

        return {
            key: _load_dataframe(path, key, columns)
            for key, columns in key_to_columns.items()
        }
