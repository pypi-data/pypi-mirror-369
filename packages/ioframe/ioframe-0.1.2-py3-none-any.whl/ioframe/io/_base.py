from __future__ import annotations

from abc import abstractmethod
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import ConfigDict

from ..core.backend import BackendBase

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..core.registry import BackendRegistry

logger = getLogger(__name__)


class IOBase(BackendBase):
    """Base class for I/O operations.

    This class provides a common interface for I/O operations
    across different formats. It is not intended to be instantiated directly.
    Subclasses must implement the abstract methods defined below.
    """

    # extra fields are passed to the reader/writer
    model_config = ConfigDict(extra="allow")

    def merge_extra_kwargs(self, /, **kwargs: Any) -> dict[str, Any]:
        """Merge extra fields from the model config with the provided kwargs."""
        merged_kwargs: dict[str, Any] = {}
        if extra := self.__pydantic_extra__:
            merged_kwargs.update(extra)
        if kwargs:
            merged_kwargs.update(kwargs)
        return merged_kwargs

    @classmethod
    @abstractmethod
    def is_compatible(cls, path: str | Path) -> bool:
        """Check if the reader is compatible with the given path.

        Args:
            path: The path to check.

        Returns:
            True if the reader is compatible with the path, False otherwise.
        """


B = TypeVar("B", bound=IOBase)


def find_ios_compatible(
    registry: BackendRegistry[B], path: str | Path | None = None
) -> Iterable[type[B]]:
    """Find all available backends compatible with the given path.

    Returns:
        An iterable of all available backends.
    """
    if path is not None and Path(path).suffix:
        for backend in registry.values(only_available=True):
            if backend.is_compatible(path):
                yield backend
    else:
        for backend in registry.values(only_available=True):
            yield backend


def find_first_io_compatible(
    registry: BackendRegistry[B], path: str | Path | None = None
) -> type[B]:
    """Find the first available backend.

    Returns:
        The first available backend, or None if no backends are available.
    """
    for backend in find_ios_compatible(registry, path):
        logger.info(
            "Found compatible I/O backend with kind %r and engine %r",
            backend.get_kind(),
            backend.get_engine(),
        )
        return backend

    msg = f"No compatible I/O backend found for path: '{path}'"
    raise ValueError(msg)
