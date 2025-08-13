"""
Constants and Enums for Sparky Robot Control
Centralized constants for consistent use across modules
"""

from enum import Enum


class MovementDirection(Enum):
    """Robot movement directions"""

    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    STATIONARY = "stationary"


class MovementQuality(Enum):
    """Movement quality assessment"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class ConnectionMethod(Enum):
    """Robot connection methods"""

    LOCALAP = "localap"  # Local AP mode
    ROUTER = "router"  # Router mode


# Robot control constants
DEFAULT_SPEED = 0.3
DEFAULT_DURATION = 2.0
MAX_SPEED = 1.0
MIN_SPEED = 0.1

# Data collection constants
DATA_BUFFER_SIZE = 1000
SAMPLE_RATE_HZ = 10
MAX_HISTORY_SECONDS = 300

# Connection constants
DEFAULT_TIMEOUT = 10.0
HEARTBEAT_INTERVAL = 1.0
RECONNECT_ATTEMPTS = 3
