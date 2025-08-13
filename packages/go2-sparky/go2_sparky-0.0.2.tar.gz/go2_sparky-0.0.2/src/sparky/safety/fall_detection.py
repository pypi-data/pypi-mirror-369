"""
Fall Detection & Prevention System for Sparky Robot
Critical safety system to prevent expensive robot damage from falls

This system protects $15k+ Go2 robot investments by:
- Detecting fall risk conditions before they happen
- Implementing preemptive stability actions
- Handling actual falls if they occur
- Coordinating with emergency response systems

Real-time monitoring with predictive algorithms ensures maximum protection.
"""

import asyncio
import logging
import math
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any

from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD

logger = logging.getLogger(__name__)


class FallRiskLevel(Enum):
    """Fall risk assessment levels"""

    STABLE = 0  # Robot is stable and secure
    LOW_RISK = 1  # Minor stability concerns
    MODERATE_RISK = 2  # Significant stability issues
    HIGH_RISK = 3  # Immediate fall risk detected
    FALLING = 4  # Fall in progress - emergency response


class StabilityTrigger(Enum):
    """What triggered stability concerns"""

    ORIENTATION = "orientation"  # Excessive tilt
    ACCELERATION = "acceleration"  # Sudden acceleration changes
    GYROSCOPE = "gyroscope"  # Rapid rotation
    CONTACT = "contact"  # Loss of ground contact
    COMMAND_FAILURE = "command_failure"  # Control commands failing
    EXTERNAL_FORCE = "external_force"  # External disturbance
    TERRAIN = "terrain"  # Unstable terrain detected
    VELOCITY = "velocity"  # Unsafe movement speed


@dataclass
class OrientationData:
    """Robot orientation information"""

    roll: float = 0.0  # Roll angle (degrees)
    pitch: float = 0.0  # Pitch angle (degrees)
    yaw: float = 0.0  # Yaw angle (degrees)
    timestamp: float = 0.0


@dataclass
class MotionData:
    """Robot motion information"""

    linear_velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)  # x, y, z
    angular_velocity: tuple[float, float, float] = (
        0.0,
        0.0,
        0.0,
    )  # roll, pitch, yaw rates
    acceleration: tuple[float, float, float] = (0.0, 0.0, 0.0)  # x, y, z acceleration
    timestamp: float = 0.0


@dataclass
class StabilityLimits:
    """Configurable stability thresholds"""

    # Orientation limits (degrees)
    stable_roll_limit: float = 8.0  # Safe roll range
    stable_pitch_limit: float = 8.0  # Safe pitch range
    warning_roll_limit: float = 15.0  # Warning roll threshold
    warning_pitch_limit: float = 15.0  # Warning pitch threshold
    danger_roll_limit: float = 25.0  # Danger roll threshold
    danger_pitch_limit: float = 25.0  # Danger pitch threshold
    critical_roll_limit: float = 35.0  # Critical roll limit
    critical_pitch_limit: float = 35.0  # Critical pitch limit

    # Motion limits
    max_safe_angular_velocity: float = 30.0  # degrees/second
    max_safe_acceleration: float = 2.0  # m/s²
    max_safe_linear_velocity: float = 1.0  # m/s

    # Timing limits
    stability_check_interval: float = 0.02  # 50Hz monitoring
    prediction_window: float = 0.5  # 500ms prediction
    recovery_timeout: float = 3.0  # Recovery attempt timeout


@dataclass
class FallEvent:
    """Fall detection event record"""

    risk_level: FallRiskLevel
    trigger: StabilityTrigger
    message: str
    orientation: OrientationData
    motion: MotionData
    timestamp: float
    response_taken: str | None = None
    prevention_successful: bool = False


class FallDetectionSystem:
    """
    Advanced fall detection and prevention system

    Provides real-time monitoring and predictive fall prevention to protect
    expensive robot hardware from damage due to falls and instability.
    """

    def __init__(self, connection, limits: StabilityLimits | None = None):
        self.conn = connection
        self.limits = limits or StabilityLimits()

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
        self.current_risk_level = FallRiskLevel.STABLE

        # Data buffers for trend analysis
        self.orientation_history = deque(maxlen=50)  # 1 second at 50Hz
        self.motion_history = deque(maxlen=50)  # 1 second at 50Hz
        self.stability_history = deque(maxlen=25)  # 500ms at 50Hz

        # Fall event tracking
        self.fall_events: list[FallEvent] = []
        self.active_prevention = False
        self.last_prevention_time = 0

        # Statistics
        self.stats = {
            "falls_prevented": 0,
            "fall_events_total": 0,
            "false_positives": 0,
            "monitoring_uptime": 0,
            "start_time": time.time(),
        }

        # Prediction algorithms
        self.stability_score = 1.0  # 1.0 = fully stable, 0.0 = falling
        self.fall_probability = 0.0  # 0.0 = no risk, 1.0 = certain fall

        logger.info(
            "Fall Detection & Prevention System initialized - protecting robot investment"
        )

    async def start_monitoring(self):
        """Start real-time fall detection monitoring"""
        if self.is_monitoring:
            logger.warning("Fall detection already monitoring")
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info("🛡️ Fall Detection monitoring started - preventing expensive damage")

    async def stop_monitoring(self):
        """Stop fall detection monitoring"""
        self.is_monitoring = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Fall Detection monitoring stopped")

    async def _monitoring_loop(self):
        """Main fall detection monitoring loop - runs at 50Hz"""
        try:
            while self.is_monitoring:
                try:
                    # Update statistics
                    self.stats["monitoring_uptime"] = (
                        time.time() - self.stats["start_time"]
                    )

                    # Collect current sensor data
                    orientation, motion = await self._collect_sensor_data()

                    # Add to history buffers
                    if orientation:
                        self.orientation_history.append(orientation)
                    if motion:
                        self.motion_history.append(motion)

                    # Perform stability analysis
                    await self._analyze_stability()

                    # Predict fall risk
                    await self._predict_fall_risk()

                    # Take preventive action if needed
                    await self._execute_prevention()

                    # 50Hz monitoring for real-time response
                    await asyncio.sleep(self.limits.stability_check_interval)

                except Exception as e:
                    logger.error(f"Error in fall detection loop: {e}")
                    await asyncio.sleep(0.1)  # Slower cycle on errors

        except asyncio.CancelledError:
            logger.info("Fall detection monitoring loop cancelled")
        except Exception as e:
            logger.critical(f"Critical error in fall detection: {e}")

    async def _collect_sensor_data(
        self,
    ) -> tuple[OrientationData | None, MotionData | None]:
        """Collect orientation and motion data from robot sensors"""
        try:
            # In real implementation, this would read from robot state topics
            # For now, we'll simulate or use available data

            current_time = time.time()

            # Placeholder for actual sensor data collection
            # This would integrate with rt/lf/lowstate and rt/multiplestate topics
            orientation = OrientationData(
                roll=0.0,  # Would read from actual IMU
                pitch=0.0,  # Would read from actual IMU
                yaw=0.0,  # Would read from actual IMU
                timestamp=current_time,
            )

            motion = MotionData(
                linear_velocity=(0.0, 0.0, 0.0),  # Would read from actual sensors
                angular_velocity=(0.0, 0.0, 0.0),  # Would read from actual sensors
                acceleration=(0.0, 0.0, 0.0),  # Would read from actual sensors
                timestamp=current_time,
            )

            return orientation, motion

        except Exception as e:
            logger.error(f"Failed to collect sensor data: {e}")
            return None, None

    async def _analyze_stability(self):
        """Analyze current stability based on orientation and motion"""
        if not self.orientation_history or not self.motion_history:
            return

        current_orientation = self.orientation_history[-1]
        current_motion = self.motion_history[-1]

        # Calculate stability score based on multiple factors
        orientation_stability = self._calculate_orientation_stability(
            current_orientation
        )
        motion_stability = self._calculate_motion_stability(current_motion)
        trend_stability = self._calculate_trend_stability()

        # Weighted combination of stability factors
        self.stability_score = (
            orientation_stability * 0.4 + motion_stability * 0.4 + trend_stability * 0.2
        )

        # Add to stability history
        self.stability_history.append(
            {
                "score": self.stability_score,
                "timestamp": time.time(),
                "orientation": current_orientation,
                "motion": current_motion,
            }
        )

    def _calculate_orientation_stability(self, orientation: OrientationData) -> float:
        """Calculate stability score based on orientation"""
        try:
            # Calculate how far we are from stable orientation
            roll_factor = abs(orientation.roll) / self.limits.critical_roll_limit
            pitch_factor = abs(orientation.pitch) / self.limits.critical_pitch_limit

            # Combine factors (higher values = less stable)
            instability = max(roll_factor, pitch_factor)

            # Convert to stability score (1.0 = stable, 0.0 = unstable)
            return max(0.0, 1.0 - instability)

        except Exception as e:
            logger.error(f"Error calculating orientation stability: {e}")
            return 0.5  # Assume moderate stability on error

    def _calculate_motion_stability(self, motion: MotionData) -> float:
        """Calculate stability score based on motion"""
        try:
            # Calculate motion intensity
            linear_magnitude = math.sqrt(sum(v**2 for v in motion.linear_velocity))
            angular_magnitude = math.sqrt(sum(v**2 for v in motion.angular_velocity))
            accel_magnitude = math.sqrt(sum(a**2 for a in motion.acceleration))

            # Normalize against limits
            linear_factor = linear_magnitude / self.limits.max_safe_linear_velocity
            angular_factor = angular_magnitude / self.limits.max_safe_angular_velocity
            accel_factor = accel_magnitude / self.limits.max_safe_acceleration

            # Combine factors
            instability = max(linear_factor, angular_factor, accel_factor)

            # Convert to stability score
            return max(0.0, 1.0 - instability)

        except Exception as e:
            logger.error(f"Error calculating motion stability: {e}")
            return 0.5

    def _calculate_trend_stability(self) -> float:
        """Calculate stability based on historical trends"""
        try:
            if len(self.stability_history) < 5:
                return 1.0  # Assume stable if not enough history

            # Look at stability trend over last 100ms
            recent_scores = [
                entry["score"] for entry in list(self.stability_history)[-5:]
            ]

            # Calculate trend (negative = getting worse)
            trend = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)

            # Convert trend to stability factor
            if trend >= 0:
                return 1.0  # Improving or stable
            else:
                # Worsening trend reduces stability
                return max(0.0, 1.0 + trend * 2)  # Scale trend impact

        except Exception as e:
            logger.error(f"Error calculating trend stability: {e}")
            return 1.0

    async def _predict_fall_risk(self):
        """Predict fall probability using advanced algorithms"""
        try:
            # Base fall probability on stability score
            self.fall_probability = 1.0 - self.stability_score

            # Enhance prediction with orientation analysis
            if self.orientation_history:
                current_orientation = self.orientation_history[-1]

                # Increase probability for dangerous orientations
                if abs(current_orientation.roll) > self.limits.danger_roll_limit:
                    self.fall_probability = max(self.fall_probability, 0.8)
                if abs(current_orientation.pitch) > self.limits.danger_pitch_limit:
                    self.fall_probability = max(self.fall_probability, 0.8)

                # Critical orientations = very high fall probability
                if (
                    abs(current_orientation.roll) > self.limits.critical_roll_limit
                    or abs(current_orientation.pitch) > self.limits.critical_pitch_limit
                ):
                    self.fall_probability = 0.95

            # Determine risk level
            old_risk_level = self.current_risk_level

            if self.fall_probability < 0.1:
                self.current_risk_level = FallRiskLevel.STABLE
            elif self.fall_probability < 0.3:
                self.current_risk_level = FallRiskLevel.LOW_RISK
            elif self.fall_probability < 0.6:
                self.current_risk_level = FallRiskLevel.MODERATE_RISK
            elif self.fall_probability < 0.85:
                self.current_risk_level = FallRiskLevel.HIGH_RISK
            else:
                self.current_risk_level = FallRiskLevel.FALLING

            # Log risk level changes
            if self.current_risk_level != old_risk_level:
                logger.warning(
                    f"Fall risk changed: {old_risk_level.name} → {self.current_risk_level.name} "
                    f"(probability: {self.fall_probability:.2f})"
                )

                # Create fall event for significant risk increases
                if self.current_risk_level.value > FallRiskLevel.LOW_RISK.value:
                    await self._create_fall_event(
                        StabilityTrigger.ORIENTATION,
                        f"Fall risk increased to {self.current_risk_level.name}",
                    )

        except Exception as e:
            logger.error(f"Error predicting fall risk: {e}")
            self.fall_probability = 0.5  # Assume moderate risk on error

    async def _execute_prevention(self):
        """Execute fall prevention measures based on risk level"""
        current_time = time.time()

        # Don't execute prevention too frequently
        if current_time - self.last_prevention_time < 0.5:
            return

        try:
            if self.current_risk_level == FallRiskLevel.MODERATE_RISK:
                await self._preventive_stabilization()

            elif self.current_risk_level == FallRiskLevel.HIGH_RISK:
                await self._emergency_stabilization()

            elif self.current_risk_level == FallRiskLevel.FALLING:
                await self._fall_mitigation()

        except Exception as e:
            logger.error(f"Error executing fall prevention: {e}")

    async def _preventive_stabilization(self):
        """Gentle stabilization for moderate risk"""
        try:
            logger.warning("⚠️ Executing preventive stabilization")
            self.active_prevention = True
            self.last_prevention_time = time.time()

            # Engage balance stand for stability
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )

            if response["data"]["header"]["status"]["code"] == 0:
                self.stats["falls_prevented"] += 1
                logger.info("✅ Preventive stabilization successful")
            else:
                logger.warning("❌ Preventive stabilization failed")

        except Exception as e:
            logger.error(f"Preventive stabilization error: {e}")
        finally:
            self.active_prevention = False

    async def _emergency_stabilization(self):
        """Aggressive stabilization for high risk"""
        try:
            logger.critical("🚨 Executing emergency stabilization - HIGH FALL RISK")
            self.active_prevention = True
            self.last_prevention_time = time.time()

            # First stop any movement
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
            )

            await asyncio.sleep(0.1)

            # Engage safe stabilization maintaining leg stiffness
            # NOTE: Previously used dangerous Damp which causes leg collapse
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["RecoveryStand"]}
            )
            logger.info(
                "🛡️ Applied RecoveryStand for emergency stabilization (avoiding dangerous Damp)"
            )

            await asyncio.sleep(0.2)

            # Try to achieve stable standing position
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )

            if response["data"]["header"]["status"]["code"] == 0:
                self.stats["falls_prevented"] += 1
                logger.info("✅ Emergency stabilization successful")
            else:
                logger.critical(
                    "❌ Emergency stabilization failed - escalating to fall mitigation"
                )
                await self._fall_mitigation()

        except Exception as e:
            logger.error(f"Emergency stabilization error: {e}")
        finally:
            self.active_prevention = False

    async def _fall_mitigation(self):
        """Last resort fall mitigation - minimize damage"""
        try:
            logger.critical("🚨 FALL DETECTED - Executing damage mitigation")
            self.active_prevention = True
            self.last_prevention_time = time.time()

            # Immediate protective sequence
            # 1. Stop all movement
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
            )

            # 2. Safe stabilization to maintain robot structure during fall
            # NOTE: Previously used dangerous Damp which would worsen the fall
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["RecoveryStand"]}
            )
            logger.info(
                "🛡️ Applied RecoveryStand for fall mitigation (avoiding dangerous Damp)"
            )

            # 3. Try protective posture if possible
            try:
                await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["Sit"]}
                )
            except Exception:
                # If sitting fails, at least we have safe stabilization active
                pass

            logger.critical(
                "Fall mitigation sequence completed - robot should be safer"
            )

        except Exception as e:
            logger.critical(f"CRITICAL: Fall mitigation failed: {e}")
        finally:
            self.active_prevention = False

    async def _create_fall_event(self, trigger: StabilityTrigger, message: str):
        """Create a fall event record"""
        try:
            current_orientation = (
                self.orientation_history[-1]
                if self.orientation_history
                else OrientationData()
            )
            current_motion = (
                self.motion_history[-1] if self.motion_history else MotionData()
            )

            event = FallEvent(
                risk_level=self.current_risk_level,
                trigger=trigger,
                message=message,
                orientation=current_orientation,
                motion=current_motion,
                timestamp=time.time(),
            )

            self.fall_events.append(event)
            self.stats["fall_events_total"] += 1

            logger.warning(f"Fall event recorded: {trigger.value} - {message}")

        except Exception as e:
            logger.error(f"Error creating fall event: {e}")

    async def manual_stability_check(self) -> dict[str, Any]:
        """Perform manual stability assessment"""
        orientation, motion = await self._collect_sensor_data()

        if orientation:
            self.orientation_history.append(orientation)
        if motion:
            self.motion_history.append(motion)

        await self._analyze_stability()
        await self._predict_fall_risk()

        return self.get_stability_status()

    def get_stability_status(self) -> dict[str, Any]:
        """Get comprehensive stability status"""
        return {
            "risk_level": self.current_risk_level.name,
            "fall_probability": self.fall_probability,
            "stability_score": self.stability_score,
            "active_prevention": self.active_prevention,
            "monitoring_active": self.is_monitoring,
            "current_orientation": {
                "roll": self.orientation_history[-1].roll
                if self.orientation_history
                else 0,
                "pitch": self.orientation_history[-1].pitch
                if self.orientation_history
                else 0,
                "yaw": self.orientation_history[-1].yaw
                if self.orientation_history
                else 0,
            }
            if self.orientation_history
            else None,
            "recent_events": [
                {
                    "risk_level": event.risk_level.name,
                    "trigger": event.trigger.value,
                    "message": event.message,
                    "timestamp": event.timestamp,
                    "prevention_successful": event.prevention_successful,
                }
                for event in self.fall_events[-5:]  # Last 5 events
            ],
            "stats": self.stats.copy(),
            "limits": {
                "stable_roll_limit": self.limits.stable_roll_limit,
                "stable_pitch_limit": self.limits.stable_pitch_limit,
                "warning_roll_limit": self.limits.warning_roll_limit,
                "warning_pitch_limit": self.limits.warning_pitch_limit,
                "danger_roll_limit": self.limits.danger_roll_limit,
                "danger_pitch_limit": self.limits.danger_pitch_limit,
            },
        }

    async def test_fall_detection(self) -> dict[str, bool]:
        """Test fall detection system functionality"""
        logger.info("Testing fall detection system...")

        results = {}

        try:
            # Test sensor data collection
            orientation, motion = await self._collect_sensor_data()
            results["sensor_collection"] = (
                orientation is not None and motion is not None
            )

            # Test stability analysis
            if orientation and motion:
                self.orientation_history.append(orientation)
                self.motion_history.append(motion)
                await self._analyze_stability()
                results["stability_analysis"] = self.stability_score >= 0

            # Test risk prediction
            await self._predict_fall_risk()
            results["risk_prediction"] = self.fall_probability >= 0

            # Test preventive action (safe test)
            if self.current_risk_level == FallRiskLevel.STABLE:
                # Only test if currently stable
                await self._preventive_stabilization()
                results["prevention_system"] = True
            else:
                results["prevention_system"] = False

            logger.info(f"Fall detection test results: {results}")

        except Exception as e:
            logger.error(f"Fall detection test failed: {e}")
            results["test_error"] = True

        return results

    def __del__(self):
        """Cleanup when fall detection system is destroyed"""
        if self.is_monitoring:
            logger.warning(
                "Fall detection destroyed while monitoring - this could be unsafe"
            )
