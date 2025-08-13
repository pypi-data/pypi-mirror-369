"""Backend-related type aliases."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeAlias, TypeVar

if TYPE_CHECKING:
    from ..core.backend import BackendBase

__all__ = ["Engine", "Kind"]

Kind: TypeAlias = str
"""A type alias for the kind of DataFrame I/O operation.

This can be a format like 'csv', 'parquet', etc.
"""

Engine: TypeAlias = str
"""A type alias for the engine used in DataFrame I/O operations.

This can be 'pandas', 'pyarrow', etc.
"""

B_contra = TypeVar("B_contra", bound="BackendBase", contravariant=True)
T_co = TypeVar("T_co", covariant=True)


class BackendFunc(Protocol[B_contra, T_co]):
    """Protocol for a function that applies on a backend."""

    def __call__(self, backend: type[B_contra], /) -> T_co:
        """Call the backend function.

        The kind and engine of the backend can be obtained through
        the :py:meth:`ioframe.core.BackendBase.get_kind`
        and :py:meth:`ioframe.core.BackendBase.get_engine` class methods.
        """
        ...
