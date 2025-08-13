"""Define a mixin for an IO that supports compression.

This allows to enforce a common interface for specifying the compression algorithm.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, Literal, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Set as AbstractSet

C = TypeVar("C")


class CompressionMixin(BaseModel, ABC, Generic[C]):
    """A mixin for adding compression support to DataFrame writers.

    This mixin allows to make sure writers that have compression support
    implement a common interface for specifying the compression algorithm.
    """

    compression: C | Literal["default"] | None = "default"
    """Compression algorithm to use for the DataFrame writer.

    ``default`` falls back to the default compression algorithm of the writer.
    ``None`` means no compression.
    """

    @classmethod
    @abstractmethod
    def get_compression_methods(cls) -> AbstractSet[C | None]:
        """Get a set of available compression methods."""
