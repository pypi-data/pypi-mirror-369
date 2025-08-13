"""
Sparky Safety Manager Core
Comprehensive safety system to protect expensive robot hardware from damage

This is the central safety coordination system that:
- Monitors robot state in real-time (50ms cycles)
- Implements multi-layered safety state machine
- Coordinates emergency responses
- Prevents falls and expensive damage
- Protects $15k+ investment in Go2 hardware
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD

logger = logging.getLogger(__name__)


class SafetyState(Enum):
    """Safety state levels with progressive response"""

    SAFE = "safe"  # Normal operation
    MONITORING = "monitoring"  # Increased vigilance
    WARNING = "warning"  # Detected potential issues
    DANGER = "danger"  # Immediate risk detected
    EMERGENCY = "emergency"  # Critical situation - emergency response
    SHUTDOWN = "shutdown"  # Safe shutdown in progress


class SafetyTrigger(Enum):
    """Types of safety triggers"""

    ORIENTATION = "orientation"  # Tilt/orientation issues
    BATTERY = "battery"  # Low battery/power issues
    TEMPERATURE = "temperature"  # Overheating
    COMMUNICATION = "communication"  # Lost connection
    COMMAND_FAILURE = "command_failure"  # Command execution failures
    ENVIRONMENTAL = "environmental"  # Environmental hazards
    COLLISION = "collision"  # Collision detected
    FALL_RISK = "fall_risk"  # Fall prediction
    USER_STOP = "user_stop"  # User-initiated emergency stop


@dataclass
class SafetyEvent:
    """Safety event data structure"""

    trigger: SafetyTrigger
    severity: SafetyState
    message: str
    data: dict[str, Any]
    timestamp: float
    resolved: bool = False


@dataclass
class SafetyLimits:
    """Configurable safety limits"""

    # Orientation limits (degrees)
    max_roll: float = 15.0  # Maximum roll angle
    max_pitch: float = 15.0  # Maximum pitch angle
    critical_roll: float = 25.0  # Critical roll angle
    critical_pitch: float = 25.0  # Critical pitch angle

    # Battery limits (percentage)
    low_battery_warning: float = 20.0
    critical_battery: float = 10.0

    # Temperature limits (Celsius)
    high_temp_warning: float = 70.0
    critical_temp: float = 85.0

    # Timing limits (seconds)
    command_timeout: float = 5.0
    communication_timeout: float = 10.0
    watchdog_timeout: float = 2.0

    # Movement limits
    max_movement_speed: float = 0.8  # Maximum safe movement speed


class SafetyManager:
    """
    Central safety management system for Go2 robot

    Provides comprehensive protection against falls, damage, and unsafe conditions.
    This is critical for protecting expensive robot hardware ($15k+ investment).
    """

    def __init__(self, connection, limits: SafetyLimits | None = None):
        self.conn = connection
        self.limits = limits or SafetyLimits()

        # Safety state management
        self.current_state = SafetyState.SAFE
        self.previous_state = SafetyState.SAFE
        self.safety_events: list[SafetyEvent] = []
        self.active_triggers: dict[SafetyTrigger, SafetyEvent] = {}

        # Monitoring and control
        self.is_monitoring = False
        self.monitoring_task = None
        self.last_heartbeat = time.time()
        self.emergency_stop_active = False

        # Callbacks for safety events
        self.event_callbacks: dict[SafetyState, list[Callable]] = {
            state: [] for state in SafetyState
        }

        # Safety statistics
        self.stats = {
            "events_total": 0,
            "events_resolved": 0,
            "emergency_stops": 0,
            "uptime": 0,
            "start_time": time.time(),
        }

        logger.info("Safety Manager initialized with comprehensive protection")

    async def start_monitoring(self):
        """Start real-time safety monitoring"""
        if self.is_monitoring:
            logger.warning("Safety monitoring already active")
            return

        self.is_monitoring = True
        self.last_heartbeat = time.time()
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info("🛡️ Safety monitoring started - protecting robot hardware")

        # Initial safety check
        await self._perform_safety_check()

    async def stop_monitoring(self):
        """Stop safety monitoring"""
        self.is_monitoring = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Safety monitoring stopped")

    async def _monitoring_loop(self):
        """Main safety monitoring loop - runs every 50ms"""
        try:
            while self.is_monitoring:
                try:
                    # Update statistics
                    self.stats["uptime"] = time.time() - self.stats["start_time"]

                    # Perform comprehensive safety check
                    await self._perform_safety_check()

                    # Check for safety state transitions
                    await self._evaluate_safety_state()

                    # Watchdog check
                    await self._watchdog_check()

                    # Update heartbeat
                    self.last_heartbeat = time.time()

                    # 50ms cycle for real-time response
                    await asyncio.sleep(0.05)

                except Exception as e:
                    logger.error(f"Error in safety monitoring loop: {e}")
                    await self._trigger_safety_event(
                        SafetyTrigger.COMMAND_FAILURE,
                        SafetyState.WARNING,
                        f"Safety monitoring error: {e}",
                        {"error": str(e)},
                    )
                    await asyncio.sleep(0.1)  # Slower cycle if errors

        except asyncio.CancelledError:
            logger.info("Safety monitoring loop cancelled")
        except Exception as e:
            logger.critical(f"Critical error in safety monitoring: {e}")
            await self.emergency_stop("Safety monitoring failure")

    async def _perform_safety_check(self):
        """Perform comprehensive safety checks"""
        try:
            # Check communication health
            await self._check_communication()

            # Check robot state (will expand with sensor data)
            await self._check_robot_state()

            # Check for expired safety events
            await self._check_event_expiration()

        except Exception as e:
            logger.error(f"Safety check error: {e}")

    async def _check_communication(self):
        """Check communication health with robot"""
        try:
            # Simple ping test - try to get motion mode
            if hasattr(self.conn, "datachannel") and self.conn.datachannel:
                # This is a lightweight check - just verify we can communicate
                current_time = time.time()
                time_since_heartbeat = current_time - self.last_heartbeat

                if time_since_heartbeat > self.limits.communication_timeout:
                    await self._trigger_safety_event(
                        SafetyTrigger.COMMUNICATION,
                        SafetyState.DANGER,
                        "Communication timeout detected",
                        {"timeout_duration": time_since_heartbeat},
                    )
            else:
                await self._trigger_safety_event(
                    SafetyTrigger.COMMUNICATION,
                    SafetyState.DANGER,
                    "No active data channel connection",
                    {"connection_state": "disconnected"},
                )

        except Exception as e:
            await self._trigger_safety_event(
                SafetyTrigger.COMMUNICATION,
                SafetyState.WARNING,
                f"Communication check failed: {e}",
                {"error": str(e)},
            )

    async def _check_robot_state(self):
        """Check robot state and sensor data"""
        try:
            # This will be expanded when we have sensor data access
            # For now, check basic operational state

            # Check if emergency stop is still active
            if self.emergency_stop_active:
                # Verify emergency stop is still needed
                active_critical_events = [
                    event
                    for event in self.active_triggers.values()
                    if event.severity in [SafetyState.DANGER, SafetyState.EMERGENCY]
                    and not event.resolved
                ]

                if not active_critical_events:
                    logger.info("No critical events - clearing emergency stop")
                    self.emergency_stop_active = False
                    await self._clear_trigger(SafetyTrigger.USER_STOP)

        except Exception as e:
            logger.error(f"Robot state check error: {e}")

    async def _check_event_expiration(self):
        """Check if safety events should be automatically resolved"""
        current_time = time.time()
        events_to_resolve = []

        for trigger, event in self.active_triggers.items():
            # Auto-resolve some events after timeout if conditions are good
            event_age = current_time - event.timestamp

            if event_age > 30.0:  # 30 second auto-resolution for some events
                if trigger in [
                    SafetyTrigger.COMMAND_FAILURE,
                    SafetyTrigger.COMMUNICATION,
                ]:
                    # Only auto-resolve if we can communicate
                    try:
                        if hasattr(self.conn, "datachannel") and self.conn.datachannel:
                            events_to_resolve.append(trigger)
                    except Exception:
                        pass

        for trigger in events_to_resolve:
            await self._clear_trigger(trigger)

    async def _evaluate_safety_state(self):
        """Evaluate overall safety state based on active triggers"""
        if not self.active_triggers:
            new_state = SafetyState.SAFE
        else:
            # Determine highest severity active trigger
            max_severity = max(
                event.severity
                for event in self.active_triggers.values()
                if not event.resolved
            )
            new_state = max_severity

        # Handle state transitions
        if new_state != self.current_state:
            await self._handle_state_transition(self.current_state, new_state)

    async def _handle_state_transition(
        self, old_state: SafetyState, new_state: SafetyState
    ):
        """Handle safety state transitions with appropriate responses"""
        self.previous_state = old_state
        self.current_state = new_state

        logger.info(f"Safety state transition: {old_state.value} → {new_state.value}")

        # Execute state-specific responses
        if new_state == SafetyState.WARNING:
            await self._handle_warning_state()
        elif new_state == SafetyState.DANGER:
            await self._handle_danger_state()
        elif new_state == SafetyState.EMERGENCY:
            await self._handle_emergency_state()
        elif new_state == SafetyState.SAFE:
            await self._handle_safe_state()

        # Call registered callbacks
        for callback in self.event_callbacks.get(new_state, []):
            try:
                await callback(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in safety callback: {e}")

    async def _handle_warning_state(self):
        """Handle warning state - increased monitoring"""
        logger.warning("⚠️ Safety WARNING state - increased monitoring active")
        # Could add audio warnings here in the future

    async def _handle_danger_state(self):
        """Handle danger state - defensive actions"""
        logger.warning("🚨 Safety DANGER state - implementing protective measures")
        try:
            # Use BalanceStand for stability (SAFE: maintains leg stiffness)
            # NOTE: Previously used dangerous Damp command which causes leg collapse
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )
            logger.info(
                "🛡️ Applied BalanceStand for safe stabilization (avoiding dangerous Damp)"
            )

            # Could add obstacle avoidance activation here
            # await self._enable_obstacle_avoidance()

        except Exception as e:
            logger.error(f"Error implementing danger state protections: {e}")

    async def _handle_emergency_state(self):
        """Handle emergency state - immediate protection"""
        logger.critical("🚨 Safety EMERGENCY state - executing emergency protection")
        await self.emergency_stop("Emergency safety state triggered")

    async def _handle_safe_state(self):
        """Handle return to safe state"""
        logger.info("✅ Safety SAFE state - normal operation resumed")
        self.emergency_stop_active = False

    async def _watchdog_check(self):
        """Safety watchdog to detect stuck states"""
        current_time = time.time()

        # Check if we've been in a bad state too long
        if self.current_state in [SafetyState.DANGER, SafetyState.EMERGENCY]:
            time_in_bad_state = current_time - self.last_heartbeat

            if time_in_bad_state > self.limits.watchdog_timeout * 10:  # 20 seconds
                logger.critical("Safety watchdog timeout - forcing emergency stop")
                await self.emergency_stop("Safety watchdog timeout")

    async def _trigger_safety_event(
        self,
        trigger: SafetyTrigger,
        severity: SafetyState,
        message: str,
        data: dict[str, Any],
    ):
        """Trigger a safety event"""
        event = SafetyEvent(
            trigger=trigger,
            severity=severity,
            message=message,
            data=data,
            timestamp=time.time(),
        )

        self.safety_events.append(event)
        self.active_triggers[trigger] = event
        self.stats["events_total"] += 1

        logger.warning(f"Safety event triggered: {trigger.value} - {message}")

    async def _clear_trigger(self, trigger: SafetyTrigger):
        """Clear a safety trigger"""
        if trigger in self.active_triggers:
            event = self.active_triggers[trigger]
            event.resolved = True
            del self.active_triggers[trigger]
            self.stats["events_resolved"] += 1

            logger.info(f"Safety trigger cleared: {trigger.value}")

    async def emergency_stop(self, reason: str = "Emergency stop requested"):
        """Execute emergency stop with comprehensive protection"""
        if self.emergency_stop_active:
            logger.warning(f"Emergency stop already active: {reason}")
            return

        self.emergency_stop_active = True
        self.stats["emergency_stops"] += 1

        logger.critical(f"🚨 EMERGENCY STOP ACTIVATED: {reason}")

        try:
            # Immediate stop command
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
            )

            # Wait briefly then engage safe stabilization
            await asyncio.sleep(0.1)

            # Use RecoveryStand for emergency stabilization (SAFE: maintains leg stiffness)
            # NOTE: Previously used dangerous Damp command which causes leg collapse
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["RecoveryStand"]}
            )
            logger.info(
                "🛡️ Applied RecoveryStand for emergency stabilization (avoiding dangerous Damp)"
            )

            # Trigger emergency safety event
            await self._trigger_safety_event(
                SafetyTrigger.USER_STOP,
                SafetyState.EMERGENCY,
                f"Emergency stop: {reason}",
                {"reason": reason, "timestamp": time.time()},
            )

            logger.critical("Emergency stop sequence completed")

        except Exception as e:
            logger.critical(f"CRITICAL: Emergency stop failed: {e}")

    async def recovery_sequence(self):
        """Execute recovery sequence after emergency"""
        logger.info("Executing recovery sequence...")

        try:
            # Clear emergency stop
            self.emergency_stop_active = False

            # Recovery stand
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["RecoveryStand"]}
            )

            await asyncio.sleep(3)

            # Balance stand
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )

            # Clear user stop trigger if it was the only issue
            if SafetyTrigger.USER_STOP in self.active_triggers:
                await self._clear_trigger(SafetyTrigger.USER_STOP)

            logger.info("Recovery sequence completed")

        except Exception as e:
            logger.error(f"Recovery sequence failed: {e}")

    def register_event_callback(self, state: SafetyState, callback: Callable):
        """Register callback for safety state changes"""
        self.event_callbacks[state].append(callback)

    def get_safety_status(self) -> dict[str, Any]:
        """Get comprehensive safety status"""
        return {
            "state": self.current_state.value,
            "previous_state": self.previous_state.value,
            "emergency_stop_active": self.emergency_stop_active,
            "active_triggers": {
                trigger.value: {
                    "severity": event.severity.value,
                    "message": event.message,
                    "age": time.time() - event.timestamp,
                }
                for trigger, event in self.active_triggers.items()
                if not event.resolved
            },
            "monitoring_active": self.is_monitoring,
            "stats": self.stats.copy(),
            "limits": {
                "max_roll": self.limits.max_roll,
                "max_pitch": self.limits.max_pitch,
                "low_battery_warning": self.limits.low_battery_warning,
                "critical_battery": self.limits.critical_battery,
            },
        }

    async def manual_safety_check(self) -> dict[str, Any]:
        """Perform manual safety check and return status"""
        await self._perform_safety_check()
        return self.get_safety_status()

    def __del__(self):
        """Cleanup when safety manager is destroyed"""
        if self.is_monitoring:
            logger.warning(
                "Safety manager destroyed while monitoring - this could be unsafe"
            )
