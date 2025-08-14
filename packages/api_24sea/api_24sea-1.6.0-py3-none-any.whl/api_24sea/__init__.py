# -*- coding: utf-8 -*-
# noqa: E501
# pylint: disable=C0301
"""Facilitate the users' interaction with the 24SEA API (https://api/24sea/eu) by providing pandas interfaces to the API endpoints.

The subpackages are:

- :mod:`api_24sea.datasignals`: Contains the :class:`DataSignals` class, which
  is an accessor for transforming data signals from the 24SEA API into pandas
  DataFrames.

The submodules are:

- :mod:`api_24sea.core`: Contains core :class:`API` class, being the
  primary interface for users to interact with the 24SEA API.
- :mod:`api_24sea.exceptions`: Contains custom exceptions for the package.
- :mod:`api_24sea.singleton`: Contains the :class:`Singleton` class, which
  is a metaclass to facilitate the implementation usage with and without
  extras.
- :mod:`api_24sea.utils`: Contains utility functions and classes to help
  manage requests to the 24SEA API.
- :mod:`api_24sea.version`: Contains the version number of the package.
"""

from . import datasignals

__all__ = ["datasignals"]

from .version import __version__ as __version__  # noqa: F401
