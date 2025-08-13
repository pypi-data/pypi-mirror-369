"""
Simple Data Streaming for Sparky Robot
Lightweight data streaming for real-time robot control
"""

import logging
from typing import Any

from .data_collector import DataCollector

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Simple analytics for basic robot movement detection
    Focused on real-time control with minimal overhead
    """

    def __init__(self, data_collector: DataCollector):
        self.data_collector = data_collector
        self.is_streaming = False

    async def start_streaming(self):
        """Start simple data streaming"""
        self.is_streaming = True
        logger.info("Started data streaming")

    async def stop_streaming(self):
        """Stop data streaming"""
        self.is_streaming = False
        logger.info("Stopped data streaming")

    async def is_robot_moving(self) -> bool:
        """Simple movement detection for real-time control"""
        try:
            latest_data = await self.data_collector.get_latest_data()
            return latest_data.is_moving if latest_data else False
        except Exception as e:
            logger.error(f"Error checking movement: {e}")
            return False

    async def get_current_sensor_data(self) -> dict[str, Any] | None:
        """Get latest sensor data for Vision Pro app"""
        try:
            latest_data = await self.data_collector.get_latest_data()
            if latest_data:
                return {
                    "timestamp": latest_data.timestamp,
                    "is_moving": latest_data.is_moving,
                    "imu_accelerometer": latest_data.imu_accelerometer,
                    "imu_gyroscope": latest_data.imu_gyroscope,
                    "imu_rpy": latest_data.imu_rpy,
                    "movement_magnitude": latest_data.movement_magnitude,
                }
            return None
        except Exception as e:
            logger.error(f"Error getting sensor data: {e}")
            return None

    async def get_basic_status(self) -> dict[str, Any]:
        """Get basic robot status for real-time monitoring"""
        try:
            is_moving = await self.is_robot_moving()
            sensor_data = await self.get_current_sensor_data()

            return {
                "streaming": self.is_streaming,
                "moving": is_moving,
                "data_available": sensor_data is not None,
                "timestamp": sensor_data["timestamp"] if sensor_data else 0,
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {
                "streaming": False,
                "moving": False,
                "data_available": False,
                "timestamp": 0,
            }
