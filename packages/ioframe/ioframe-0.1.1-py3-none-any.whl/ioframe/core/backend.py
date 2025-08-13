"""Define the base class for a backend that can be stored in registries."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from logging import getLogger

from pydantic import BaseModel, computed_field, model_validator

from ioframe.core.types import Engine, Kind

__all__ = ["BackendBase"]

logger = getLogger(__name__)


class BackendBase(BaseModel, ABC):
    """Mixin class for registry functionality.

    This class provides methods to register and retrieve objects in a registry.
    It is intended to be used as a mixin in classes that need registry capabilities.
    """

    @computed_field(return_type=Kind)  # type: ignore[prop-decorator]
    @property
    def kind(self) -> Kind:
        """Call :py:meth:`get_kind`."""
        return self.get_kind()

    @computed_field(return_type=Engine)  # type: ignore[prop-decorator]
    @property
    def engine(self) -> Engine:
        """Call :py:meth:`get_engine`."""
        return self.get_engine()

    @model_validator(mode="before")
    @classmethod
    def _drop_kind_and_engine(cls, values: object) -> object:
        """Drop 'kind' and 'engine' fields from the model."""
        expected_kind = cls.get_kind()
        expected_engine = cls.get_engine()

        if isinstance(values, Mapping):
            values = dict(values)
            # Pop them if they exist
            kind = values.pop("kind", None)
            engine = values.pop("engine", None)

            # Validate 'kind' and 'engine' against the class methods (if they exist)
            if kind is not None and kind != expected_kind:
                msg = f"Expected 'kind' to be '{expected_kind}', but got '{kind}'."
                raise ValueError(msg)

            if engine is not None and engine != expected_engine:
                msg = (
                    f"Expected 'engine' to be '{expected_engine}', but got '{engine}'."
                )
                raise ValueError(msg)

        if not cls.is_available():
            logger.warning(
                "Initializing '%s' with 'kind'='%s' and 'engine'='%s', "
                "but the backend is not available.",
                cls.__name__,
                expected_kind,
                expected_engine,
            )
        return values

    @classmethod
    @abstractmethod
    def get_kind(cls) -> str:
        """Return the key used to identify this object in the registry.

        This method should return a unique key that identifies the format of the
        object, such as "csv", "json", etc.
        """
        ...

    @classmethod
    @abstractmethod
    def get_engine(cls) -> str:
        """Return the engine used by this object.

        This method should return a string that identifies the engine used by
        the object, such as "pandas", "pyarrow", etc.
        """
        ...

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if the object is available.

        This method should return True if the object can be used,
        False otherwise. It can be used to check for optional dependencies.
        """
        ...
