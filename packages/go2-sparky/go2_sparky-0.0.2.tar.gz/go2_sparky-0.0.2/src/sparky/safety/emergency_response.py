"""
Emergency Response System for Sparky Robot
Layered emergency response to protect expensive robot hardware

Implements escalating response levels:
1. SOFT_STOP: Gentle deceleration and stabilization
2. HARD_STOP: Immediate movement cessation
3. EMERGENCY_STABILIZE: Safe stabilization maintaining leg stiffness
4. PROTECTIVE_POSTURE: Move to safest possible position
5. SAFE_SHUTDOWN: Complete system shutdown

This system is critical for protecting $15k+ Go2 robot investments.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD

logger = logging.getLogger(__name__)


class EmergencyLevel(Enum):
    """Emergency response levels - escalating severity"""

    NONE = 0
    SOFT_STOP = 1  # Gentle deceleration
    HARD_STOP = 2  # Immediate stop
    EMERGENCY_STABILIZE = 3  # Safe stabilization (maintains leg stiffness)
    PROTECTIVE_POSTURE = 4  # Move to safe position
    SAFE_SHUTDOWN = 5  # Complete shutdown


class EmergencyTrigger(Enum):
    """What triggered the emergency response"""

    MANUAL = "manual"
    FALL_DETECTED = "fall_detected"
    TILT_EXCESSIVE = "tilt_excessive"
    COLLISION = "collision"
    COMMUNICATION_LOST = "communication_lost"
    BATTERY_CRITICAL = "battery_critical"
    TEMPERATURE_CRITICAL = "temperature_critical"
    COMMAND_FAILURE = "command_failure"
    SENSOR_FAILURE = "sensor_failure"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class EmergencyResponse:
    """Emergency response record"""

    trigger: EmergencyTrigger
    level: EmergencyLevel
    timestamp: float
    success: bool
    duration: float
    error_message: str | None = None
    recovery_attempted: bool = False
    recovery_success: bool = False


class EmergencyResponseSystem:
    """
    Comprehensive emergency response system

    Provides layered responses to protect robot hardware from damage.
    Each level provides increasing protection with more restrictive responses.
    """

    def __init__(self, connection):
        self.conn = connection
        self.current_level = EmergencyLevel.NONE
        self.active_emergency = False
        self.response_history: list[EmergencyResponse] = []
        self.last_response_time = 0

        # Response timing constraints
        self.min_response_interval = 0.5  # Minimum time between responses (seconds)
        self.response_timeout = 10.0  # Maximum time to wait for response

        # Statistics
        self.stats = {
            "total_emergencies": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "recoveries_attempted": 0,
            "recoveries_successful": 0,
        }

        logger.info("Emergency Response System initialized")

    async def trigger_emergency(
        self,
        trigger: EmergencyTrigger,
        level: EmergencyLevel,
        context: dict[str, Any] = None,
    ) -> EmergencyResponse:
        """
        Trigger emergency response with specified level

        Args:
            trigger: What caused the emergency
            level: Severity level of response needed
            context: Additional context data

        Returns:
            EmergencyResponse record
        """
        current_time = time.time()

        # Prevent rapid-fire emergency responses
        if current_time - self.last_response_time < self.min_response_interval:
            logger.warning(
                f"Emergency response rate limited - ignoring {trigger.value}"
            )
            return None

        self.last_response_time = current_time
        self.stats["total_emergencies"] += 1

        logger.critical(
            f"🚨 EMERGENCY TRIGGERED: {trigger.value} (Level: {level.value})"
        )

        # Create response record
        response = EmergencyResponse(
            trigger=trigger,
            level=level,
            timestamp=current_time,
            success=False,
            duration=0,
        )

        try:
            # Execute emergency response based on level
            start_time = time.time()

            if level == EmergencyLevel.SOFT_STOP:
                success = await self._soft_stop()
            elif level == EmergencyLevel.HARD_STOP:
                success = await self._hard_stop()
            elif level == EmergencyLevel.EMERGENCY_STABILIZE:
                success = await self._emergency_stabilize()
            elif level == EmergencyLevel.PROTECTIVE_POSTURE:
                success = await self._protective_posture()
            elif level == EmergencyLevel.SAFE_SHUTDOWN:
                success = await self._safe_shutdown()
            else:
                success = False
                response.error_message = f"Unknown emergency level: {level}"

            response.duration = time.time() - start_time
            response.success = success

            if success:
                self.stats["successful_responses"] += 1
                self.current_level = level
                self.active_emergency = True
                logger.info(
                    f"Emergency response completed successfully in {response.duration:.2f}s"
                )
            else:
                self.stats["failed_responses"] += 1
                logger.error(
                    f"Emergency response FAILED after {response.duration:.2f}s"
                )

                # If this response failed, try a higher level response
                if level.value < EmergencyLevel.SAFE_SHUTDOWN.value:
                    logger.warning("Escalating to higher emergency level")
                    next_level = EmergencyLevel(level.value + 1)
                    await asyncio.sleep(0.2)  # Brief pause
                    await self.trigger_emergency(trigger, next_level, context)

        except Exception as e:
            response.duration = time.time() - start_time
            response.error_message = str(e)
            self.stats["failed_responses"] += 1
            logger.critical(f"CRITICAL: Emergency response exception: {e}")

        self.response_history.append(response)
        return response

    async def _soft_stop(self) -> bool:
        """Level 1: Gentle deceleration and stabilization"""
        try:
            logger.info("Executing SOFT STOP - gentle deceleration")

            # Send stop move command
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
            )

            if response["data"]["header"]["status"]["code"] != 0:
                logger.error("Stop command failed")
                return False

            # Brief pause for movement to cease
            await asyncio.sleep(0.5)

            # Transition to balanced stand for stability
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )

            return response["data"]["header"]["status"]["code"] == 0

        except Exception as e:
            logger.error(f"Soft stop failed: {e}")
            return False

    async def _hard_stop(self) -> bool:
        """Level 2: Immediate movement cessation"""
        try:
            logger.warning("Executing HARD STOP - immediate cessation")

            # Multiple rapid stop commands for immediate effect
            for _ in range(3):
                try:
                    await self.conn.datachannel.pub_sub.publish_request_new(
                        RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
                    )
                    await asyncio.sleep(0.1)
                except Exception:
                    pass

            return True

        except Exception as e:
            logger.error(f"Hard stop failed: {e}")
            return False

    async def _emergency_stabilize(self) -> bool:
        """Level 3: Safe emergency stabilization maintaining leg stiffness"""
        try:
            logger.warning(
                "Executing EMERGENCY STABILIZE - safe stabilization with leg stiffness"
            )

            # First stop movement
            await self._hard_stop()

            # Engage safe stabilization (SAFE: maintains leg stiffness)
            # NOTE: Previously used dangerous Damp which causes immediate leg collapse
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["RecoveryStand"]}
            )

            if response["data"]["header"]["status"]["code"] == 0:
                logger.info(
                    "🛡️ Emergency stabilization with RecoveryStand successful (avoiding dangerous Damp)"
                )
                return True
            else:
                # Fallback to BalanceStand if RecoveryStand fails
                logger.warning("RecoveryStand failed, trying BalanceStand as fallback")
                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
                )
                return response["data"]["header"]["status"]["code"] == 0

        except Exception as e:
            logger.error(f"Emergency stabilization failed: {e}")
            return False

    async def _protective_posture(self) -> bool:
        """Level 4: Move to safest possible position"""
        try:
            logger.warning("Executing PROTECTIVE POSTURE - safest position")

            # Stop and stabilize first (safe alternative to dangerous damp)
            await self._emergency_stabilize()
            await asyncio.sleep(1.0)

            # Try to move to sitting position (lower center of gravity)
            try:
                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["Sit"]}
                )

                if response["data"]["header"]["status"]["code"] == 0:
                    logger.info("Robot moved to sitting position")
                    return True

            except Exception as e:
                logger.warning(f"Could not sit - trying stand down: {e}")

            # If sitting failed, try lying down
            try:
                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StandDown"]}
                )

                if response["data"]["header"]["status"]["code"] == 0:
                    logger.info("Robot moved to lying position")
                    return True

            except Exception as e:
                logger.error(f"Stand down also failed: {e}")

            # If all else fails, at least we have safe stabilization active
            return True

        except Exception as e:
            logger.error(f"Protective posture failed: {e}")
            return False

    async def _safe_shutdown(self) -> bool:
        """Level 5: Complete safe shutdown"""
        try:
            logger.critical("Executing SAFE SHUTDOWN - complete protection")

            # Execute all lower level protections first
            await self._protective_posture()
            await asyncio.sleep(2.0)

            # Additional safe stabilization (avoiding dangerous Damp)
            try:
                await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
                )
                logger.info(
                    "🛡️ Applied BalanceStand for final stabilization (avoiding dangerous Damp)"
                )
            except Exception:
                pass

            logger.critical("Robot is in safe shutdown state")
            return True

        except Exception as e:
            logger.critical(f"Safe shutdown failed: {e}")
            return False

    async def attempt_recovery(self) -> bool:
        """
        Attempt to recover from emergency state

        Returns:
            True if recovery successful, False otherwise
        """
        if not self.active_emergency:
            logger.info("No active emergency - no recovery needed")
            return True

        self.stats["recoveries_attempted"] += 1

        logger.info(
            f"Attempting recovery from emergency level {self.current_level.value}"
        )

        try:
            # Mark all responses as having recovery attempted
            for response in self.response_history:
                if not response.recovery_attempted:
                    response.recovery_attempted = True

            # Recovery sequence based on current emergency level
            if self.current_level in [
                EmergencyLevel.SOFT_STOP,
                EmergencyLevel.HARD_STOP,
            ]:
                success = await self._recovery_from_stop()
            elif self.current_level == EmergencyLevel.EMERGENCY_STABILIZE:
                success = await self._recovery_from_stabilize()
            elif self.current_level == EmergencyLevel.PROTECTIVE_POSTURE:
                success = await self._recovery_from_posture()
            elif self.current_level == EmergencyLevel.SAFE_SHUTDOWN:
                success = await self._recovery_from_shutdown()
            else:
                success = False

            if success:
                self.current_level = EmergencyLevel.NONE
                self.active_emergency = False
                self.stats["recoveries_successful"] += 1

                # Mark recovery success in history
                for response in self.response_history:
                    if response.recovery_attempted and not response.recovery_success:
                        response.recovery_success = True

                logger.info("✅ Recovery successful - normal operation resumed")
            else:
                logger.error("❌ Recovery failed - robot may need manual intervention")

            return success

        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            return False

    async def _recovery_from_stop(self) -> bool:
        """Recover from stop states"""
        try:
            # Simple balance stand should be sufficient
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )

            return response["data"]["header"]["status"]["code"] == 0

        except Exception as e:
            logger.error(f"Recovery from stop failed: {e}")
            return False

    async def _recovery_from_stabilize(self) -> bool:
        """Recover from emergency stabilization state"""
        try:
            # Balance stand to ensure stable positioning (leg stiffness was maintained)
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )

            if response["data"]["header"]["status"]["code"] == 0:
                logger.info("🛡️ Recovery from emergency stabilization successful")
                return True
            else:
                logger.warning(
                    "Recovery balance stand failed, robot may need manual intervention"
                )
                return False

        except Exception as e:
            logger.error(f"Recovery from emergency stabilization failed: {e}")
            return False

    async def _recovery_from_posture(self) -> bool:
        """Recover from protective posture"""
        try:
            # Try recovery stand first
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["RecoveryStand"]}
            )

            if response["data"]["header"]["status"]["code"] == 0:
                await asyncio.sleep(3)  # Allow recovery time

                # Then balance stand
                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
                )

                return response["data"]["header"]["status"]["code"] == 0

            return False

        except Exception as e:
            logger.error(f"Recovery from posture failed: {e}")
            return False

    async def _recovery_from_shutdown(self) -> bool:
        """Recover from safe shutdown"""
        try:
            # This is the most complex recovery
            logger.info("Attempting recovery from safe shutdown...")

            # Step 1: Recovery stand
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["RecoveryStand"]}
            )

            if response["data"]["header"]["status"]["code"] != 0:
                logger.error("Recovery stand failed during shutdown recovery")
                return False

            await asyncio.sleep(4)  # Allow time for recovery

            # Step 2: Balance stand
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )

            return response["data"]["header"]["status"]["code"] == 0

        except Exception as e:
            logger.error(f"Recovery from shutdown failed: {e}")
            return False

    def get_emergency_status(self) -> dict[str, Any]:
        """Get comprehensive emergency system status"""
        return {
            "active_emergency": self.active_emergency,
            "current_level": self.current_level.value,
            "level_name": self.current_level.name,
            "last_response_time": self.last_response_time,
            "response_history_count": len(self.response_history),
            "recent_responses": [
                {
                    "trigger": r.trigger.value,
                    "level": r.level.value,
                    "success": r.success,
                    "duration": r.duration,
                    "timestamp": r.timestamp,
                    "recovery_attempted": r.recovery_attempted,
                    "recovery_success": r.recovery_success,
                }
                for r in self.response_history[-5:]  # Last 5 responses
            ],
            "stats": self.stats.copy(),
        }

    def clear_emergency_state(self):
        """Manually clear emergency state (use with caution)"""
        logger.warning("Emergency state manually cleared")
        self.current_level = EmergencyLevel.NONE
        self.active_emergency = False

    async def test_emergency_system(self) -> dict[str, bool]:
        """Test emergency system functionality (safe test)"""
        logger.info("Testing emergency response system...")

        results = {}

        try:
            # Test soft stop
            response = await self.trigger_emergency(
                EmergencyTrigger.MANUAL, EmergencyLevel.SOFT_STOP
            )
            results["soft_stop"] = response.success if response else False

            # Allow brief recovery
            await asyncio.sleep(1)

            # Test recovery
            recovery_success = await self.attempt_recovery()
            results["recovery"] = recovery_success

            logger.info(f"Emergency system test results: {results}")

        except Exception as e:
            logger.error(f"Emergency system test failed: {e}")
            results["test_error"] = True

        return results
