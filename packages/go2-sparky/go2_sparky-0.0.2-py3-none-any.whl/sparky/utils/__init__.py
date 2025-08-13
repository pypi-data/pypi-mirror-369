"""
Sparky Utilities
Common constants, exceptions, and helper functions
"""

from .constants import (
    DEFAULT_DURATION,
    DEFAULT_SPEED,
    MAX_SPEED,
    MIN_SPEED,
    ConnectionMethod,
    MovementDirection,
    MovementQuality,
)
from .exceptions import (
    ConfigurationError,
    ConnectionError,
    DataCollectionError,
    RobotControlError,
    SparkyError,
    TimeoutError,
)

__all__ = [
    # Constants
    "MovementDirection",
    "MovementQuality",
    "ConnectionMethod",
    "DEFAULT_SPEED",
    "DEFAULT_DURATION",
    "MAX_SPEED",
    "MIN_SPEED",
    # Exceptions
    "SparkyError",
    "ConnectionError",
    "RobotControlError",
    "DataCollectionError",
    "ConfigurationError",
    "TimeoutError",
]
