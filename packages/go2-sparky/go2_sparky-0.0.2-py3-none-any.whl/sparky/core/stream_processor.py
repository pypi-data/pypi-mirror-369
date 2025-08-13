"""
Stream Processor for Sparky Robot
Real-time processing and analysis of sensor data streams
"""

import asyncio
import logging
import statistics
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .data_collector import DataCollector, SensorData

logger = logging.getLogger(__name__)


@dataclass
class MovementEvent:
    """Represents a detected movement event"""

    timestamp: float
    event_type: str  # 'start', 'stop', 'change'
    movement_type: str  # 'linear', 'rotation', 'complex'
    magnitude: float
    duration: float = 0.0
    confidence: float = 0.0
    details: dict[str, Any] = None


@dataclass
class StreamMetrics:
    """Real-time metrics from data stream"""

    timestamp: float

    # Movement metrics
    avg_movement_magnitude: float = 0.0
    max_movement_magnitude: float = 0.0
    movement_variance: float = 0.0

    # Stability metrics
    stability_score: float = 0.0
    stability_trend: str = "stable"  # "stable", "improving", "degrading"

    # Performance metrics
    avg_motor_temperature: float = 0.0
    max_motor_temperature: float = 0.0
    battery_efficiency: float = 0.0

    # Activity metrics
    movement_percentage: float = 0.0
    activity_level: str = "idle"  # "idle", "low", "moderate", "high"

    # System health
    communication_health: float = 100.0
    sensor_health: float = 100.0
    overall_health: str = "good"  # "good", "warning", "critical"


class StreamProcessor:
    """
    Real-time processor for sensor data streams
    Provides analytics, event detection, and metrics calculation
    """

    def __init__(self, data_collector: DataCollector, window_size: int = 50):
        self.data_collector = data_collector
        self.window_size = window_size
        self.processing_enabled = False

        # Event detection
        self.current_movement_state = "idle"
        self.movement_start_time = None
        self.last_movement_event = None
        self.event_callbacks: list[Callable[[MovementEvent], None]] = []

        # Metrics calculation
        self.metrics_window = deque(maxlen=window_size)
        self.current_metrics = StreamMetrics(timestamp=time.time())
        self.metrics_callbacks: list[Callable[[StreamMetrics], None]] = []

        # Thresholds for event detection
        self.movement_threshold = 0.05
        self.stability_threshold = 0.1
        self.temperature_warning_threshold = 60.0
        self.temperature_critical_threshold = 80.0

        # Processing state
        self.processing_task = None

    def add_event_callback(self, callback: Callable[[MovementEvent], None]):
        """Add callback for movement events"""
        self.event_callbacks.append(callback)

    def add_metrics_callback(self, callback: Callable[[StreamMetrics], None]):
        """Add callback for metrics updates"""
        self.metrics_callbacks.append(callback)

    async def start_processing(self):
        """Start real-time stream processing"""
        if self.processing_enabled:
            logger.warning("Stream processing already running")
            return

        self.processing_enabled = True

        # Add data collector callback
        self.data_collector.add_callback(self._process_data_point)

        # Start metrics calculation task
        self.processing_task = asyncio.create_task(self._metrics_calculation_loop())

        logger.info("Started stream processing")

    async def stop_processing(self):
        """Stop stream processing"""
        if not self.processing_enabled:
            return

        self.processing_enabled = False

        # Remove data collector callback
        self.data_collector.remove_callback(self._process_data_point)

        # Cancel processing task
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass

        logger.info("Stopped stream processing")

    def _process_data_point(self, sensor_data: SensorData):
        """Process a single sensor data point"""
        try:
            # Add to metrics window
            self.metrics_window.append(sensor_data)

            # Detect movement events
            self._detect_movement_events(sensor_data)

        except Exception as e:
            logger.error(f"Error processing data point: {e}")

    def _detect_movement_events(self, sensor_data: SensorData):
        """Detect movement events from sensor data"""
        try:
            current_state = "moving" if sensor_data.is_moving else "idle"

            # State change detection
            if current_state != self.current_movement_state:
                event_type = "start" if current_state == "moving" else "stop"

                # Calculate duration for stop events
                duration = 0.0
                if event_type == "stop" and self.movement_start_time:
                    duration = sensor_data.timestamp - self.movement_start_time

                # Determine movement type
                movement_type = self._classify_movement_type(sensor_data)

                # Create movement event
                event = MovementEvent(
                    timestamp=sensor_data.timestamp,
                    event_type=event_type,
                    movement_type=movement_type,
                    magnitude=sensor_data.movement_magnitude,
                    duration=duration,
                    confidence=self._calculate_event_confidence(sensor_data),
                    details={
                        "gyroscope": sensor_data.imu_gyroscope,
                        "accelerometer": sensor_data.imu_accelerometer,
                        "stability_score": sensor_data.stability_score,
                    },
                )

                # Update state
                self.current_movement_state = current_state
                if event_type == "start":
                    self.movement_start_time = sensor_data.timestamp
                else:
                    self.movement_start_time = None

                self.last_movement_event = event

                # Notify callbacks
                for callback in self.event_callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error(f"Error in event callback: {e}")

        except Exception as e:
            logger.error(f"Error detecting movement events: {e}")

    def _classify_movement_type(self, sensor_data: SensorData) -> str:
        """Classify the type of movement"""
        gyro_mag = sum(abs(x) for x in sensor_data.imu_gyroscope)
        accel_mag = sum(abs(x) for x in sensor_data.imu_accelerometer)

        if gyro_mag > accel_mag * 2:
            return "rotation"
        elif accel_mag > gyro_mag * 2:
            return "linear"
        else:
            return "complex"

    def _calculate_event_confidence(self, sensor_data: SensorData) -> float:
        """Calculate confidence score for movement event"""
        # Simple confidence based on magnitude and consistency
        magnitude_score = min(sensor_data.movement_magnitude / 1.0, 1.0)

        # Check recent data consistency if available
        consistency_score = 0.8  # Default
        if len(self.metrics_window) > 5:
            recent_movements = [
                data.movement_magnitude for data in list(self.metrics_window)[-5:]
            ]
            if recent_movements:
                variance = (
                    statistics.variance(recent_movements)
                    if len(recent_movements) > 1
                    else 0
                )
                consistency_score = max(0.1, 1.0 - min(variance, 1.0))

        return (magnitude_score + consistency_score) / 2.0

    async def _metrics_calculation_loop(self):
        """Background task for calculating stream metrics"""
        try:
            while self.processing_enabled:
                await self._calculate_metrics()
                await asyncio.sleep(1.0)  # Update metrics every second
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Error in metrics calculation loop: {e}")

    async def _calculate_metrics(self):
        """Calculate current stream metrics"""
        try:
            if not self.metrics_window:
                return

            # Get recent data
            window_data = list(self.metrics_window)
            current_time = time.time()

            # Movement metrics
            movements = [data.movement_magnitude for data in window_data]
            avg_movement = statistics.mean(movements) if movements else 0.0
            max_movement = max(movements) if movements else 0.0
            movement_variance = (
                statistics.variance(movements) if len(movements) > 1 else 0.0
            )

            # Stability metrics
            stability_scores = [data.stability_score for data in window_data]
            avg_stability = (
                statistics.mean(stability_scores) if stability_scores else 0.0
            )

            # Calculate stability trend
            if len(stability_scores) >= 10:
                recent_stability = statistics.mean(stability_scores[-5:])
                older_stability = statistics.mean(stability_scores[-10:-5])
                if recent_stability < older_stability - 0.05:
                    stability_trend = "improving"
                elif recent_stability > older_stability + 0.05:
                    stability_trend = "degrading"
                else:
                    stability_trend = "stable"
            else:
                stability_trend = "stable"

            # Temperature metrics
            all_temps = []
            for data in window_data:
                all_temps.extend(data.motor_temperatures)

            avg_temp = statistics.mean(all_temps) if all_temps else 0.0
            max_temp = max(all_temps) if all_temps else 0.0

            # Activity metrics
            moving_count = sum(1 for data in window_data if data.is_moving)
            movement_percentage = (
                (moving_count / len(window_data)) * 100 if window_data else 0.0
            )

            # Classify activity level
            if movement_percentage < 10:
                activity_level = "idle"
            elif movement_percentage < 30:
                activity_level = "low"
            elif movement_percentage < 70:
                activity_level = "moderate"
            else:
                activity_level = "high"

            # System health metrics
            communication_health = 100.0
            motor_lost_count = 0

            for data in window_data[-5:]:  # Check recent data
                motor_lost_count += sum(1 for lost in data.motor_lost_flags if lost)

            if motor_lost_count > 0:
                communication_health = max(0, 100 - (motor_lost_count * 20))

            # Sensor health based on data consistency
            sensor_health = 100.0
            if (
                movement_variance > 2.0
            ):  # High variance indicates potential sensor issues
                sensor_health = max(50, 100 - (movement_variance * 10))

            # Overall health
            if (
                max_temp > self.temperature_critical_threshold
                or communication_health < 50
            ):
                overall_health = "critical"
            elif (
                max_temp > self.temperature_warning_threshold
                or communication_health < 80
            ):
                overall_health = "warning"
            else:
                overall_health = "good"

            # Battery efficiency (simplified calculation)
            recent_currents = [data.battery_current for data in window_data[-10:]]
            avg_current = statistics.mean(recent_currents) if recent_currents else 0.0
            battery_efficiency = max(
                0, 100 - abs(avg_current) * 0.1
            )  # Simplified metric

            # Create metrics object
            self.current_metrics = StreamMetrics(
                timestamp=current_time,
                avg_movement_magnitude=avg_movement,
                max_movement_magnitude=max_movement,
                movement_variance=movement_variance,
                stability_score=avg_stability,
                stability_trend=stability_trend,
                avg_motor_temperature=avg_temp,
                max_motor_temperature=max_temp,
                battery_efficiency=battery_efficiency,
                movement_percentage=movement_percentage,
                activity_level=activity_level,
                communication_health=communication_health,
                sensor_health=sensor_health,
                overall_health=overall_health,
            )

            # Notify callbacks
            for callback in self.metrics_callbacks:
                try:
                    callback(self.current_metrics)
                except Exception as e:
                    logger.error(f"Error in metrics callback: {e}")

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")

    def get_current_metrics(self) -> StreamMetrics:
        """Get current stream metrics"""
        return self.current_metrics

    def get_last_movement_event(self) -> MovementEvent | None:
        """Get the last detected movement event"""
        return self.last_movement_event

    async def get_movement_history(
        self, duration_seconds: float = 60.0
    ) -> list[MovementEvent]:
        """Get movement events from the last N seconds"""
        # This would require storing event history - simplified for now
        if self.last_movement_event:
            current_time = time.time()
            if current_time - self.last_movement_event.timestamp <= duration_seconds:
                return [self.last_movement_event]
        return []

    def set_movement_threshold(self, threshold: float):
        """Set movement detection threshold"""
        self.movement_threshold = threshold
        logger.info(f"Movement threshold set to {threshold}")

    def set_temperature_thresholds(self, warning: float, critical: float):
        """Set temperature warning and critical thresholds"""
        self.temperature_warning_threshold = warning
        self.temperature_critical_threshold = critical
        logger.info(
            f"Temperature thresholds set to warning: {warning}°C, critical: {critical}°C"
        )

    async def analyze_movement_pattern(
        self, duration_seconds: float = 30.0
    ) -> dict[str, Any]:
        """Analyze movement patterns over a time period"""
        try:
            # Get data from the specified duration
            data = await self.data_collector.get_data_in_timeframe(duration_seconds)

            if not data:
                return {"error": "No data available for analysis"}

            # Analyze patterns
            movement_magnitudes = [d.movement_magnitude for d in data]
            stability_scores = [d.stability_score for d in data]

            analysis = {
                "duration_analyzed": duration_seconds,
                "sample_count": len(data),
                "movement_stats": {
                    "mean": statistics.mean(movement_magnitudes),
                    "median": statistics.median(movement_magnitudes),
                    "max": max(movement_magnitudes),
                    "min": min(movement_magnitudes),
                    "variance": statistics.variance(movement_magnitudes)
                    if len(movement_magnitudes) > 1
                    else 0,
                },
                "stability_stats": {
                    "mean": statistics.mean(stability_scores),
                    "median": statistics.median(stability_scores),
                    "trend": "stable",  # Could be enhanced with trend analysis
                },
                "activity_summary": {
                    "moving_percentage": (
                        sum(1 for d in data if d.is_moving) / len(data)
                    )
                    * 100,
                    "peak_activity_periods": [],  # Could identify peak activity times
                },
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing movement pattern: {e}")
            return {"error": str(e)}
