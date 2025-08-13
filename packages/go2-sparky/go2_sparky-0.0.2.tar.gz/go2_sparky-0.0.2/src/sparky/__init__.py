"""
Sparky - Go2 Robot Control Package
Simple, fast robot control for real-time applications like Vision Pro
"""

# Simple API for beginners (recommended)
# Advanced API for power users
from . import core
from .core.analytics_engine import AnalyticsEngine
from .core.connection import Go2Connection
from .core.data_collector import DataCollector, SensorData
from .core.motion import MotionController
from .robot import Robot, connect_robot

# Connection methods
from .utils.constants import ConnectionMethod, MovementDirection, MovementQuality

__version__ = "1.0.0"
__author__ = "Ranga Reddy Nukala"
__description__ = "Fast Go2 Robot Control for Real-time Applications"

# Clean exports for Vision Pro and beginner use
__all__ = [
    # Simple API (start here!)
    "Robot",
    "connect_robot",
    "ConnectionMethod",
    # Advanced API
    "Go2Connection",
    "MotionController",
    "DataCollector",
    "SensorData",
    "AnalyticsEngine",
    "MovementDirection",
    "MovementQuality",
    # Core module
    "core",
]
