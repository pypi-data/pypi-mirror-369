"""
Custom Exceptions for Sparky Robot Control
Centralized exception handling for better error management
"""


class SparkyError(Exception):
    """Base exception for all Sparky errors"""

    pass


class ConnectionError(SparkyError):
    """Connection-related errors"""

    pass


class RobotControlError(SparkyError):
    """Robot control command errors"""

    pass


class DataCollectionError(SparkyError):
    """Data collection and streaming errors"""

    pass


class ConfigurationError(SparkyError):
    """Configuration and setup errors"""

    pass


class TimeoutError(SparkyError):
    """Operation timeout errors"""

    pass
