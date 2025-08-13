from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Self, TypeAlias, TypedDict

Argument: TypeAlias = dict[str, Any]


class WriterReaderArgumentDict(TypedDict, total=False):
    """Dictionary representation of :py:class:`WriterReaderArgument`."""

    dfwriter: Argument
    dfreader: Argument


@dataclass
class IOArgument:
    """Representation of writer and reader arguments."""

    dfwriter: dict[str, Any] = field(default_factory=dict[str, Any])
    dfreader: dict[str, Any] = field(default_factory=dict[str, Any])

    @classmethod
    def from_any(
        cls,
        obj: Self
        | WriterReaderArgumentDict
        | tuple[Argument]
        | tuple[Argument, Argument],
    ) -> Self:
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, tuple):
            return cls(*(dict(arg) for arg in obj))
        elif isinstance(obj, Mapping):
            return cls(**obj)
        else:  # pragma: no cover
            msg = f"Invalid argument type: {type(obj)} Expected a 2-tuple or a mapping"
            raise TypeError(msg)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(dfwriter={dict(self.dfwriter)}, dfreader={dict(self.dfreader)})"
        )

    def __str__(self) -> str:
        return self.__repr__()


WriterReaderArgumentInput: TypeAlias = (
    tuple[Argument] | tuple[Argument, Argument] | IOArgument | WriterReaderArgumentDict
)
