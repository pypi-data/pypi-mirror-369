"""Convenient exports for the :mod:`flarchitect` package.

This module exposes the primary public interface so users can simply do::

    from flarchitect import Architect

rather than importing from the internal ``core`` package.
"""

from importlib.metadata import version as _get_version

from .core.architect import Architect

__version__ = _get_version("flarchitect")

__all__ = ["Architect", "__version__"]
