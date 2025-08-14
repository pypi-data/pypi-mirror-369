"""
Sataid Package Initialization

This file makes the core components of the sataid package, like read_sataid and SataidArray,
available for direct import by the user.
"""

__version__ = "0.1.2"

from ._core import read_sataid
from ._array import SataidArray

__all__ = ['read_sataid', 'SataidArray']