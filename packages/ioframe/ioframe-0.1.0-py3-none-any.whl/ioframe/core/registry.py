"""Defines a registry for backends."""

from __future__ import annotations

import contextlib
from collections.abc import Generator, Iterable, Mapping
from functools import cached_property, partial
from logging import getLogger
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Generic,
    Literal,
    NamedTuple,
    NoReturn,
    TypeVar,
    Union,
)

from pydantic import Discriminator, Tag, TypeAdapter

from .backend import BackendBase

if TYPE_CHECKING:
    from .types import BackendFunc, Engine, Kind

__all__ = ["BackendKey", "BackendRegistry", "UnavailableBackendError"]

logger = getLogger(__name__)

B = TypeVar("B", bound=BackendBase)
V = TypeVar("V")


class BackendKey(NamedTuple):
    """Key for identifying a backend class."""

    kind: Kind
    engine: Engine


class UnavailableBackendError(Exception):
    """Exception raised when a requested backend is not available."""


def _raise_invalid_kind(
    kind: Kind, kinds: Iterable[Kind], e: Exception | None = None
) -> NoReturn:
    """Raise an error for an invalid kind."""
    msg = f"Invalid kind '{kind}'. Expected one of: " + ", ".join(map(repr, kinds))
    raise UnavailableBackendError(msg) from e


def _raise_invalid_engine(
    engine: Engine,
    engines: Iterable[Engine],
    kind: Kind | None = None,
    e: Exception | None = None,
) -> NoReturn:
    """Raise an error for an invalid engine."""
    msg = f"Invalid engine '{engine}'"
    msg += f" for kind {kind!r}. " if kind is not None else ". "
    msg += "Expected one of: " + ", ".join(map(repr, engines))
    raise UnavailableBackendError(msg) from e


def _get_value(
    mapping: object, *, key: Literal["kind", "engine"], default: object
) -> object:
    """Get the kind of the DataFrame I/O operation."""
    if isinstance(mapping, BackendBase):
        return getattr(mapping, f"get_{key}")()  # call get_kind() or get_engine()
    elif isinstance(mapping, Mapping):
        value = mapping.get(key, default)
        if value is None:
            value = default
        return value
    else:
        msg = f"Expected BackendMixin or Mapping, got: {type(mapping).__name__}"
        raise TypeError(msg)


def _get_default_kind(kinds: Iterable[Kind]) -> Kind:
    """Get the default kind from the registered backends."""
    try:
        return next(iter(kinds))
    except StopIteration:
        msg = "No kind registered in the backend registry."
        raise UnavailableBackendError(msg) from None


def _get_default_engine(
    backends: Mapping[Kind, Mapping[Engine, V]], kind: Kind
) -> Engine:
    """Get the default engine for a specific kind."""
    engines = backends.get(kind)
    if not engines:
        _raise_invalid_kind(kind, backends.keys())
    return next(iter(engines))


def _get_backend(
    backends: Mapping[Kind, Mapping[Engine, V]], kind: Kind, engine: Engine
) -> V:
    """Get a specific backend from the registry."""
    if kind not in backends:
        _raise_invalid_kind(kind, backends.keys())
    if engine not in backends[kind]:
        _raise_invalid_engine(engine, backends[kind].keys(), kind=kind)
    logger.debug("Using backend for kind '%s' and engine '%s'", kind, engine)
    return backends[kind][engine]


def _make_discriminated_union(
    tag_to_variant: Mapping[str, V], discriminator: Discriminator
) -> Annotated[Any, Discriminator]:
    """Create a discriminated union from a mapping of tags to variants."""
    if len(tag_to_variant) == 1:
        # If there's only one variant, we can return it directly
        return next(iter(tag_to_variant.values()))

    return Annotated[
        Union[
            *(Annotated[variant, Tag(tag)] for tag, variant in tag_to_variant.items())
        ],
        discriminator,
    ]


class BackendRegistry(Generic[B]):
    """A registry for DataFrame I/O backends.

    This registry allows for easy access to different backends based on their kind
    and engine.
    Fall backs to the first available backend if no specific kind or engine is provided.
    """

    def __empty_cache(self) -> None:
        """Clear the cached properties."""
        with contextlib.suppress(AttributeError):
            del self._available_backends

        with contextlib.suppress(AttributeError):
            del self.discriminated_union

    def __init__(
        self,
        registry: (
            BackendRegistry[B] | Mapping[Kind, Mapping[Engine, type[B]]] | None
        ) = None,
        /,
    ) -> None:
        if registry is None:
            backends = {}
        elif isinstance(registry, BackendRegistry):
            backends = registry.to_dict(only_available=False, view=False)
        elif isinstance(registry, Mapping):
            backends = {
                kind: dict(engines.items()) for kind, engines in registry.items()
            }
        else:
            msg = (
                "Expected a BackendRegistry or a mapping of kinds to engines, "
                f"got: {type(registry).__name__}"
            )
            raise TypeError(msg)

        self._backends: dict[Kind, dict[Engine, type[B]]] = backends
        """A dictionary containing registered backends."""

    # Private methods ================================================================
    @cached_property
    def _available_backends(self) -> dict[Kind, dict[Engine, type[B]]]:
        """Return a dictionary of available backends."""
        return {
            kind: engines_for_kind
            for kind, engines in self._backends.items()
            if (
                engines_for_kind := {
                    engine: backend
                    for engine, backend in engines.items()
                    if backend.is_available()
                }
            )
        }

    def _get_backends(
        self, *, only_available: bool = True
    ) -> dict[Kind, dict[Engine, type[B]]]:
        """Return a dictionary of backends."""
        return self._available_backends if only_available else self._backends

    def _register(self, backend: type[B], *, override: bool = False) -> None:
        """Register a backend in the registry."""
        kind = backend.get_kind()
        engine = backend.get_engine()

        if (
            not override
            and (engines := self._backends.get(kind))
            and (registered_backend := engines.get(engine))
        ):
            msg = (
                f"Backend with kind '{kind}' and engine '{engine}' "
                f"is already registered: {registered_backend}. "
                "Use 'override=True' to replace it."
            )
            raise ValueError(msg)

        self._backends.setdefault(kind, {})[engine] = backend

    def _get_engine_to_backend(
        self, kind: Kind, *, only_available: bool = True
    ) -> dict[Engine, type[B]]:
        """Get the engines and backends for a specific kind."""
        backends = self._get_backends(only_available=only_available)
        engine_to_backend = backends.get(kind)
        if not engine_to_backend:
            _raise_invalid_kind(kind, backends.keys())
        return engine_to_backend

    # Public methods =================================================================
    # Setters / getters --------------------------------------------------------------
    def register(self, backend: type[B], *, override: bool = False) -> None:
        """Register a backend in the registry."""
        self._register(backend, override=override)
        self.__empty_cache()

    def register_many(
        self, backends: Iterable[type[B]], *, override: bool = False
    ) -> None:
        """Register multiple backends in the registry."""
        for backend in backends:
            self._register(backend, override=override)
        self.__empty_cache()

    def get(
        self,
        kind: Kind | None = None,
        engine: Engine | None = None,
        *,
        only_available: bool = True,
    ) -> type[B]:
        """Return a backend based on kind and engine."""
        backends = self._get_backends(only_available=only_available)
        if kind is None:
            kind = _get_default_kind(backends)
            logger.debug("Using first registered kind: '%s'", kind)
        if engine is None:
            engine = _get_default_engine(backends, kind)
            logger.debug(
                "Using first registered engine for kind '%s': '%s'", kind, engine
            )
        return _get_backend(backends, kind, engine)

    # Available backends -------------------------------------------------------------
    def get_kinds(self, *, only_available: bool = True) -> list[Kind]:
        """Return a list of kinds available in the registry."""
        backends = self._get_backends(only_available=only_available)
        return list(backends.keys())

    def get_engines_for_kind(
        self, kind: Kind, *, only_available: bool = True
    ) -> list[Engine]:
        """Return a list of engines available for a specific kind."""
        return list(
            self._get_engine_to_backend(kind, only_available=only_available).keys()
        )

    # Filter methods ----------------------------------------------------------------
    def filter(self, func: BackendFunc[B, bool]) -> BackendRegistry[B]:
        backends = self._backends

        filtered_backends = {
            kind: engine_to_backend
            for kind, engine_to_backend_ in backends.items()
            if (
                engine_to_backend := {
                    engine: backend
                    for engine, backend in engine_to_backend_.items()
                    if func(backend)
                }
            )
        }
        return BackendRegistry(filtered_backends)

    def items(
        self, *, only_available: bool = True
    ) -> Generator[tuple[BackendKey, type[B]], None]:
        """Return an iterable of (kind, engine) pairs and corresponding backends."""
        backends = self._get_backends(only_available=only_available)
        for kind, engines in backends.items():
            for engine, backend in engines.items():
                yield BackendKey(kind=kind, engine=engine), backend

    def keys(self, *, only_available: bool = True) -> Generator[BackendKey, None]:
        """Return an iterable of (kind, engine) pairs."""
        backends = self._get_backends(only_available=only_available)
        for kind, engines in backends.items():
            for engine in engines:
                yield BackendKey(kind=kind, engine=engine)

    def values(self, *, only_available: bool = True) -> Generator[type[B], None]:
        """Return an iterable of backends."""
        backends = self._get_backends(only_available=only_available)
        for engines in backends.values():
            yield from engines.values()

    # Discriminated unions -----------------------------------------------------------
    def get_discriminated_union_for_kind(
        self, kind: Kind, *, only_available: bool = True
    ) -> Annotated[Any, Discriminator]:
        """Return a discriminated union for a specific kind."""
        backends = self._get_backends(only_available=only_available)
        engine_to_backend = self._get_engine_to_backend(
            kind, only_available=only_available
        )
        default_engine = _get_default_engine(backends, kind)

        discriminator_func = partial(_get_value, key="engine", default=default_engine)
        discriminator_func.__name__ = "get_engine"  # type: ignore[attr-defined]

        return _make_discriminated_union(
            {
                engine: backend
                for engine, backend in engine_to_backend.items()
                if backend.is_available()
            },
            Discriminator(discriminator_func),
        )

    @cached_property
    def discriminated_union(self) -> Annotated[Any, Discriminator]:
        """Return an annotation for the registry."""
        kinds = self.get_kinds(only_available=True)
        default_kind = _get_default_kind(kinds)

        discriminator_func = partial(_get_value, key="kind", default=default_kind)
        discriminator_func.__name__ = "get_kind"  # type: ignore[attr-defined]

        return _make_discriminated_union(
            {kind: self.get_discriminated_union_for_kind(kind) for kind in kinds},
            Discriminator(discriminator_func),
        )

    def initialize(self, value: object, /) -> B:
        """Initialize the backend with the given value."""
        return TypeAdapter(self.discriminated_union).validate_python(value)

    # Reordering methods -------------------------------------------------------------
    def favour_kinds(self, kinds: Iterable[Kind]) -> None:
        """Favour specific kinds in the registry."""
        old_backends = self._backends.copy()
        backends: dict[Kind, dict[Engine, type[B]]] = {}
        for kind in kinds:
            try:
                engine_to_backend = old_backends.pop(kind)
            except KeyError as e:
                _raise_invalid_kind(kind, old_backends.keys(), e)
            backends[kind] = engine_to_backend

        backends.update(old_backends)
        self._backends = backends
        self.__empty_cache()

    def favour_engines(self, kind: Kind, engines: Iterable[Engine]) -> None:
        """Favour specific engines for a kind in the registry."""
        _old_engine_to_backend = self._backends.get(kind)
        if not _old_engine_to_backend:
            _raise_invalid_kind(kind, self._backends.keys())

        old_engine_to_backend = _old_engine_to_backend.copy()
        engine_to_backend: dict[Engine, type[B]] = {}
        for engine in engines:
            try:
                backend = old_engine_to_backend.pop(engine)
            except KeyError as e:
                _raise_invalid_engine(
                    engine, old_engine_to_backend.keys(), kind=kind, e=e
                )
            engine_to_backend[engine] = backend

        engine_to_backend.update(old_engine_to_backend)
        # order of kind is not changed because it is already in the dictionary
        self._backends[kind] = engine_to_backend
        self.__empty_cache()

    # Dictionary representation ------------------------------------------------------
    def to_dict(
        self, *, only_available: bool = False, view: bool = False
    ) -> dict[Kind, dict[Engine, type[B]]]:
        """Return a dictionary representation of the registry."""
        backends = self._available_backends if only_available else self._backends
        return backends if view else backends.copy()
