"""
SEDQL - Python SDK for SED (Semantic Entities Designs)

A Python wrapper around the SED CLI tool for programmatic access to semantic layers.
"""

from .client import SEDClient
from .exceptions import SEDError, SEDConnectionError, SEDValidationError

__version__ = "1.0.9"
__all__ = ["SEDClient", "SEDError", "SEDConnectionError", "SEDValidationError"]
