"""
Data Collector for Sparky Robot
Collects, structures, and buffers sensor data from the robot for analytics
"""

import asyncio
import logging
import time
from collections import deque
from collections.abc import Callable
from dataclasses import asdict, dataclass
from typing import Any

from go2_webrtc_driver.constants import RTC_TOPIC

logger = logging.getLogger(__name__)


@dataclass
class SensorData:
    """Structured sensor data from the robot"""

    timestamp: float

    # IMU Data
    imu_rpy: list[float]  # Roll, Pitch, Yaw
    imu_gyroscope: list[float]  # Angular velocity
    imu_accelerometer: list[float]  # Linear acceleration
    imu_quaternion: list[float]  # Orientation quaternion

    # Motor Data
    motor_positions: list[float]  # Joint positions
    motor_velocities: list[float]  # Joint velocities
    motor_torques: list[float]  # Joint torques
    motor_temperatures: list[float]  # Motor temperatures
    motor_lost_flags: list[bool]  # Communication status

    # Battery Data
    battery_soc: int  # State of charge percentage
    battery_current: float  # Current draw
    battery_voltage: float  # Battery voltage
    battery_temperature: float  # Battery temperature

    # Foot Force Data
    foot_forces: list[float]  # Forces on each foot

    # Additional Sensors
    temperature_ntc1: float  # NTC temperature sensor
    power_voltage: float  # Power voltage

    # Derived Metrics (calculated)
    movement_magnitude: float = 0.0
    rotation_magnitude: float = 0.0
    acceleration_magnitude: float = 0.0
    is_moving: bool = False
    stability_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class DataBuffer:
    """Time-series buffer for sensor data with analytics support"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.data: deque[SensorData] = deque(maxlen=max_size)
        self._lock = asyncio.Lock()

    async def add(self, sensor_data: SensorData):
        """Add new sensor data to buffer"""
        async with self._lock:
            self.data.append(sensor_data)

    async def get_latest(self, count: int = 1) -> list[SensorData]:
        """Get latest N sensor readings"""
        async with self._lock:
            if count == 1:
                return [self.data[-1]] if self.data else []
            return (
                list(self.data)[-count:] if len(self.data) >= count else list(self.data)
            )

    async def get_time_range(
        self, start_time: float, end_time: float
    ) -> list[SensorData]:
        """Get sensor data within time range"""
        async with self._lock:
            return [
                data for data in self.data if start_time <= data.timestamp <= end_time
            ]

    async def get_all(self) -> list[SensorData]:
        """Get all buffered data"""
        async with self._lock:
            return list(self.data)

    async def clear(self):
        """Clear the buffer"""
        async with self._lock:
            self.data.clear()

    @property
    def size(self) -> int:
        """Current buffer size"""
        return len(self.data)

    @property
    def is_empty(self) -> bool:
        """Check if buffer is empty"""
        return len(self.data) == 0


class DataCollector:
    """
    Collects and structures sensor data from Sparky robot
    Provides real-time data streaming and buffering for analytics
    """

    def __init__(self, connection, buffer_size: int = 1000):
        self.conn = connection
        self.buffer = DataBuffer(buffer_size)
        self.is_collecting = False
        self.callbacks: list[Callable[[SensorData], None]] = []
        self.collection_task = None
        self.stats = {
            "total_samples": 0,
            "collection_start_time": None,
            "last_sample_time": None,
            "sampling_rate": 0.0,
        }

    def add_callback(self, callback: Callable[[SensorData], None]):
        """Add callback function to be called on new data"""
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[SensorData], None]):
        """Remove callback function"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    async def start_collection(self):
        """Start collecting sensor data"""
        if self.is_collecting:
            logger.warning("Data collection already running")
            return

        self.is_collecting = True
        self.stats["collection_start_time"] = time.time()
        self.stats["total_samples"] = 0

        # Subscribe to low state data
        def data_callback(message):
            try:
                raw_data = message["data"]
                sensor_data = self._parse_sensor_data(raw_data)

                # Add to buffer
                asyncio.create_task(self.buffer.add(sensor_data))

                # Update stats
                self.stats["total_samples"] += 1
                self.stats["last_sample_time"] = sensor_data.timestamp

                # Calculate sampling rate
                if self.stats["collection_start_time"]:
                    duration = (
                        sensor_data.timestamp - self.stats["collection_start_time"]
                    )
                    if duration > 0:
                        self.stats["sampling_rate"] = (
                            self.stats["total_samples"] / duration
                        )

                # Call registered callbacks
                for callback in self.callbacks:
                    try:
                        callback(sensor_data)
                    except Exception as e:
                        logger.error(f"Error in data callback: {e}")

            except Exception as e:
                logger.error(f"Error processing sensor data: {e}")

        # Subscribe to sensor data stream
        self.conn.datachannel.pub_sub.subscribe(RTC_TOPIC["LOW_STATE"], data_callback)
        logger.info("Started data collection")

    async def stop_collection(self):
        """Stop collecting sensor data"""
        if not self.is_collecting:
            return

        self.is_collecting = False

        # Unsubscribe from data stream
        # Note: This is a simplified approach. In practice, you'd need to track the callback reference
        # to properly unsubscribe. For now, we'll rely on the connection cleanup.

        logger.info("Stopped data collection")

    def _parse_sensor_data(self, raw_data: dict[str, Any]) -> SensorData:
        """Parse raw sensor data into structured format"""
        timestamp = time.time()

        # Extract IMU data
        imu_state = raw_data.get("imu_state", {})
        imu_rpy = imu_state.get("rpy", [0.0, 0.0, 0.0])
        imu_gyroscope = imu_state.get("gyroscope", [0.0, 0.0, 0.0])
        imu_accelerometer = imu_state.get("accelerometer", [0.0, 0.0, 0.0])
        imu_quaternion = imu_state.get("quaternion", [0.0, 0.0, 0.0, 1.0])

        # Extract motor data
        motor_state = raw_data.get("motor_state", [])
        motor_positions = [motor.get("q", 0.0) for motor in motor_state]
        motor_velocities = [motor.get("dq", 0.0) for motor in motor_state]
        motor_torques = [motor.get("tau_est", 0.0) for motor in motor_state]
        motor_temperatures = [motor.get("temperature", 0.0) for motor in motor_state]
        motor_lost_flags = [motor.get("lost", False) for motor in motor_state]

        # Extract battery data
        bms_state = raw_data.get("bms_state", {})
        battery_soc = bms_state.get("soc", 0)
        battery_current = bms_state.get("current", 0.0)
        battery_voltage = raw_data.get("power_v", 0.0)
        battery_temperature = bms_state.get("bq_ntc", 0.0)

        # Extract foot force data
        foot_forces = raw_data.get("foot_force", [0.0, 0.0, 0.0, 0.0])

        # Additional sensors
        temperature_ntc1 = raw_data.get("temperature_ntc1", 0.0)
        power_voltage = raw_data.get("power_v", 0.0)

        # Calculate derived metrics
        movement_magnitude = sum(abs(x) for x in imu_gyroscope)
        rotation_magnitude = sum(abs(x) for x in imu_rpy)
        acceleration_magnitude = sum(abs(x) for x in imu_accelerometer)
        is_moving = movement_magnitude > 0.05 or acceleration_magnitude > 0.1

        # Calculate stability score (lower is more stable)
        stability_score = movement_magnitude + (acceleration_magnitude * 0.5)

        return SensorData(
            timestamp=timestamp,
            imu_rpy=imu_rpy,
            imu_gyroscope=imu_gyroscope,
            imu_accelerometer=imu_accelerometer,
            imu_quaternion=imu_quaternion,
            motor_positions=motor_positions,
            motor_velocities=motor_velocities,
            motor_torques=motor_torques,
            motor_temperatures=motor_temperatures,
            motor_lost_flags=motor_lost_flags,
            battery_soc=battery_soc,
            battery_current=battery_current,
            battery_voltage=battery_voltage,
            battery_temperature=battery_temperature,
            foot_forces=foot_forces,
            temperature_ntc1=temperature_ntc1,
            power_voltage=power_voltage,
            movement_magnitude=movement_magnitude,
            rotation_magnitude=rotation_magnitude,
            acceleration_magnitude=acceleration_magnitude,
            is_moving=is_moving,
            stability_score=stability_score,
        )

    async def get_latest_data(self) -> SensorData | None:
        """Get the most recent sensor data"""
        latest = await self.buffer.get_latest(1)
        return latest[0] if latest else None

    async def get_data_history(self, count: int = 100) -> list[SensorData]:
        """Get recent sensor data history"""
        return await self.buffer.get_latest(count)

    async def get_data_in_timeframe(self, duration_seconds: float) -> list[SensorData]:
        """Get sensor data from the last N seconds"""
        current_time = time.time()
        start_time = current_time - duration_seconds
        return await self.buffer.get_time_range(start_time, current_time)

    def get_collection_stats(self) -> dict[str, Any]:
        """Get data collection statistics"""
        return self.stats.copy()

    async def export_data(self, format_type: str = "json") -> Any:
        """Export collected data in specified format"""
        all_data = await self.buffer.get_all()

        if format_type == "json":
            return [data.to_dict() for data in all_data]
        elif format_type == "csv":
            # Return data in CSV-friendly format
            if not all_data:
                return []

            # Get all field names from the first data point
            fieldnames = list(all_data[0].to_dict().keys())
            csv_data = [fieldnames]  # Header row

            for data in all_data:
                row = [str(data.to_dict()[field]) for field in fieldnames]
                csv_data.append(row)

            return csv_data
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    async def clear_data(self):
        """Clear all collected data"""
        await self.buffer.clear()
        self.stats["total_samples"] = 0
        logger.info("Cleared all collected data")
