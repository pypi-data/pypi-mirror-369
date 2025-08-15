"""Utility helpers for mapping compression codecs to canonical file extensions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["get_suffix_for", "merge_suffixes"]

_COMPRESSION_METHOD_TO_EXTENSION: Final[Mapping[str | None, str | None]] = {
    None: None,
    "gzip": ".gz",
    "zstd": ".zst",
    "brotli": ".br",
}
"""Mapping of compression method to their canonical file extensions.

Only specify codecs whose canonical file extension deviates from the codec name.
"""


def get_suffix_for(compression_method: str | None, /) -> str:
    """Return the canonical file-extension for *compression*.

    Args:
        compression_method: Compression codec name, e.g. ``gzip``.
            ``None`` means no compression.

    Returns:
        The extension string without the leading ``.``.

    Examples:
        >>> extension_for("gzip")
        'gz'
        >>> extension_for(None)
        ''
    """
    extension = _COMPRESSION_METHOD_TO_EXTENSION.get(
        compression_method, f".{compression_method}"
    )
    if extension is None:
        return ""
    return extension


def get_compression_method_for(suffix: str | None, /) -> str | None:
    """Return the compression method for a given file suffix.

    Args:
        suffix: File suffix, e.g. ``.gz``.
            ``None`` means no suffix.

    Returns:
        The compression codec name, or ``None`` if no compression is used.

    Examples:
        >>> get_compression_method_for(".gz")
        'gzip'
        >>> get_compression_method_for(None)
        None
    """
    if not suffix:
        return None

    return next(
        (
            method
            for method, ext in _COMPRESSION_METHOD_TO_EXTENSION.items()
            if ext == suffix
        ),
        suffix.lstrip(".") if suffix.startswith(".") else suffix,
    )


def merge_suffixes(*extensions: str | None) -> str:
    """Normalise and join *extensions* into a single dotted suffix.

    Args:
        *extensions: Individual extensions, with leading ``.``.
            ``None`` or empty strings are silently ignored.

    Returns:
        A single string that starts with ``.``. If *extensions* is empty or
        all values are falsy, an empty string is returned.

    Example:
        >>> merge_extensions("csv", "gz")
        '.csv.gz'
    """
    return "".join(extension for extension in extensions if extension)
