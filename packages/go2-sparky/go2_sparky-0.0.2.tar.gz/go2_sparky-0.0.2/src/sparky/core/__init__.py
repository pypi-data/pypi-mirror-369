"""
Sparky Core Module
Core functionality for Sparky robot control and data streaming
"""

# Connection management
from .analytics_engine import AnalyticsEngine
from .connection import (
    Go2Connection,
    create_local_ap_connection,
    create_local_sta_connection,
    create_local_sta_connection_by_serial,
    create_remote_connection,
)

# Data streaming and analytics
from .data_collector import DataBuffer, DataCollector, SensorData

# Motion control
from .motion import MotionController
from .stream_processor import MovementEvent, StreamMetrics, StreamProcessor

__all__ = [
    # Connection
    "Go2Connection",
    "create_local_ap_connection",
    "create_local_sta_connection",
    "create_local_sta_connection_by_serial",
    "create_remote_connection",
    # Motion
    "MotionController",
    # Data streaming
    "DataCollector",
    "SensorData",
    "DataBuffer",
    # Stream processing
    "StreamProcessor",
    "MovementEvent",
    "StreamMetrics",
    # Analytics
    "AnalyticsEngine",
]

# Version info
__version__ = "1.0.0"
__author__ = "Sparky Development Team"
__description__ = "Advanced robot control and analytics for Go2 robots"
