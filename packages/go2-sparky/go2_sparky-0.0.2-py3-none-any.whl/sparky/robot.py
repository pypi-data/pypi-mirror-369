"""
High-Level Robot API
Simplified interface for common robot operations
"""

import logging
from typing import Any

from .core.analytics_engine import AnalyticsEngine
from .core.connection import Go2Connection, WebRTCConnectionMethod
from .core.data_collector import DataCollector
from .core.motion import MotionController
from .core.stream_processor import StreamProcessor
from .interfaces import RobotInterface
from .utils.constants import ConnectionMethod

logger = logging.getLogger(__name__)


class Robot(RobotInterface):
    """
    High-level robot interface that simplifies common operations

    This class provides a simplified API for basic robot operations,
    hiding the complexity of the underlying components while still
    allowing access to advanced features when needed.
    """

    def __init__(self):
        self.connection: Go2Connection | None = None
        self.motion: MotionController | None = None
        self.data_collector: DataCollector | None = None
        self.stream_processor: StreamProcessor | None = None
        self.analytics_engine: AnalyticsEngine | None = None
        self._data_streaming_active = False

    async def connect(
        self,
        method: ConnectionMethod = ConnectionMethod.LOCALAP,
        ip: str | None = None,
        serial_number: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> bool:
        """
        Connect to robot using simplified parameters

        Args:
            method: Connection method to use
            ip: Robot IP address (for LocalSTA)
            serial_number: Robot serial number (for LocalSTA/Remote)
            username: Username (for Remote)
            password: Password (for Remote)

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Map interface enum to internal enum
            method_map = {
                ConnectionMethod.LOCALAP: WebRTCConnectionMethod.LocalAP,
                ConnectionMethod.ROUTER: WebRTCConnectionMethod.LocalSTA,
            }

            webrtc_method = method_map[method]

            # Create connection based on method
            self.connection = Go2Connection(
                connection_method=webrtc_method,
                ip=ip,
                serial_number=serial_number,
                username=username,
                password=password,
            )

            # Attempt connection
            success = await self.connection.connect()

            if success:
                # Initialize motion controller
                self.motion = MotionController(self.connection.conn)
                logger.info(f"Successfully connected to robot via {method.value}")
                return True
            else:
                logger.error(f"Failed to connect to robot via {method.value}")
                return False

        except Exception as e:
            logger.error(f"Error connecting to robot: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from robot and cleanup resources"""
        try:
            # Stop data streaming if active
            if self._data_streaming_active:
                await self.stop_data_stream()

            # Disconnect from robot
            if self.connection:
                success = await self.connection.disconnect()
                self.connection = None
                self.motion = None
                logger.info("Disconnected from robot")
                return success

            return True

        except Exception as e:
            logger.error(f"Error disconnecting from robot: {e}")
            return False

    async def move(
        self,
        direction: str,
        speed: float = 0.5,
        duration: float = 2.0,
        verify: bool = True,
    ) -> bool:
        """
        Move robot in specified direction

        Args:
            direction: Movement direction (forward, backward, left, right, turn-left, turn-right)
            speed: Movement speed (0.1 to 1.0)
            duration: Movement duration in seconds
            verify: Whether to verify movement actually occurred

        Returns:
            True if movement successful, False otherwise
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False

        try:
            direction = direction.lower().replace("_", "-")

            if direction == "forward":
                return await self.motion.move_forward(speed, duration, verify=verify)
            elif direction == "backward":
                return await self.motion.move_backward(speed, duration, verify=verify)
            elif direction == "left":
                return await self.motion.move_left(speed, duration, verify=verify)
            elif direction == "right":
                return await self.motion.move_right(speed, duration, verify=verify)
            elif direction in ["turn-left", "turnleft"]:
                return await self.motion.turn_left(speed, duration, verify=verify)
            elif direction in ["turn-right", "turnright"]:
                return await self.motion.turn_right(speed, duration, verify=verify)
            elif direction == "stop":
                return await self.motion.stop()
            else:
                logger.error(f"Unknown movement direction: {direction}")
                return False

        except Exception as e:
            logger.error(f"Error moving robot {direction}: {e}")
            return False

    async def command(self, command: str, verify: bool = True) -> bool:
        """
        Execute a sport command

        Args:
            command: Sport command to execute (hello, sit, standup, etc.)
            verify: Whether to verify command execution

        Returns:
            True if command successful, False otherwise
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False

        try:
            # Handle common command name variations and casing
            command_mapping = {
                "balancestand": "BalanceStand",
                "standup": "StandUp",
                "standdown": "StandDown",
                "recoverystand": "RecoveryStand",
                "stopmove": "StopMove",
                "frontflip": "FrontFlip",
                "backflip": "BackFlip",
                "leftflip": "LeftFlip",
                "rightflip": "RightFlip",
                "frontjump": "FrontJump",
                "frontpounce": "FrontPounce",
            }

            # Normalize command name
            normalized_command = command_mapping.get(command.lower(), command.title())

            return await self.motion.execute_sport_command(
                normalized_command, verify=verify
            )
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return False

    async def is_moving(self) -> bool:
        """
        Check if robot is currently moving

        Returns:
            True if robot is moving, False otherwise
        """
        if self.analytics_engine:
            try:
                return await self.analytics_engine.is_robot_moving()
            except Exception as e:
                logger.error(f"Error checking movement via analytics: {e}")

        # Fallback to motion controller status
        if self.motion:
            try:
                status = self.motion.get_status()
                return status.get("is_moving", False)
            except Exception as e:
                logger.error(f"Error checking movement status: {e}")

        return False

    async def get_status(self) -> dict[str, Any]:
        """
        Get comprehensive robot status

        Returns:
            Dictionary containing robot status information
        """
        status = {
            "connected": self.connection is not None and self.connection.is_connected,
            "data_streaming": self._data_streaming_active,
            "motion_available": self.motion is not None,
            "analytics_available": self.analytics_engine is not None,
        }

        if self.connection:
            status["connection"] = self.connection.get_connection_info()

        if self.motion:
            status["motion"] = self.motion.get_status()

        if self.data_collector:
            status["data_collection"] = self.data_collector.get_collection_stats()

        if self.stream_processor:
            status["metrics"] = self.stream_processor.get_current_metrics()

        # Add safety and queue status
        if self.safety_manager:
            status["safety"] = self.safety_manager.get_safety_status()

        if self.motion:
            queue_status = self.motion.get_queue_status()
            if queue_status:
                status["action_queue"] = queue_status

        return status

    async def start_data_stream(
        self, buffer_size: int = 1000, analytics: bool = True
    ) -> None:
        """
        Start data streaming and analytics

        Args:
            buffer_size: Size of data buffer
            analytics: Whether to enable analytics engine
        """
        if not self.connection or not self.connection.is_connected:
            raise RuntimeError("Not connected to robot")

        try:
            # Initialize data collection components
            self.data_collector = DataCollector(self.connection.conn, buffer_size)
            self.stream_processor = StreamProcessor(self.data_collector)

            if analytics:
                self.analytics_engine = AnalyticsEngine(self.data_collector)

            # Start data streaming
            await self.data_collector.start_collection()
            await self.stream_processor.start_processing()

            if self.analytics_engine:
                await self.analytics_engine.start_streaming()

            self._data_streaming_active = True
            logger.info("Data streaming started")

        except Exception as e:
            logger.error(f"Error starting data stream: {e}")
            raise

    async def stop_data_stream(self) -> None:
        """Stop data streaming and analytics"""
        try:
            if self.analytics_engine:
                await self.analytics_engine.stop_streaming()
                self.analytics_engine = None

            if self.stream_processor:
                await self.stream_processor.stop_processing()
                self.stream_processor = None

            if self.data_collector:
                await self.data_collector.stop_collection()
                self.data_collector = None

            self._data_streaming_active = False
            logger.info("Data streaming stopped")

        except Exception as e:
            logger.error(f"Error stopping data stream: {e}")

    async def export_data(self, format_type: str = "json") -> Any:
        """
        Export collected data

        Args:
            format_type: Export format ("json" or "csv")

        Returns:
            Exported data in specified format
        """
        if not self.data_collector:
            raise RuntimeError("Data collection not active")

        try:
            return await self.data_collector.export_data(format_type)
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            raise

    async def _start_safety_systems(self):
        """Start all safety systems"""
        try:
            # Start safety manager monitoring
            if self.safety_manager:
                await self.safety_manager.start_monitoring()
                logger.info("🛡️ Safety monitoring started")

            # Start action queue if enabled
            if self.motion and self.enable_safety_queue:
                await self.motion.start_action_queue()
                logger.info("🛡️ Ultra-safe action queue started")

        except Exception as e:
            logger.error(f"Error starting safety systems: {e}")

    async def _stop_safety_systems(self):
        """Stop all safety systems"""
        try:
            # Stop action queue
            if self.motion:
                await self.motion.stop_action_queue()

            # Stop safety manager
            if self.safety_manager:
                await self.safety_manager.stop_monitoring()

            logger.info("Safety systems stopped")

        except Exception as e:
            logger.error(f"Error stopping safety systems: {e}")

    async def emergency_stop(
        self, reason: str = "User requested emergency stop"
    ) -> bool:
        """Ultra-safe emergency stop - highest priority"""
        logger.critical(f"🛑 EMERGENCY STOP: {reason}")

        try:
            # Stop via safety manager if available
            if self.safety_manager:
                await self.safety_manager.emergency_stop(reason)

            # Stop via motion controller
            if self.motion:
                await self.motion.emergency_stop_all(reason)

            logger.critical("Emergency stop completed")
            return True

        except Exception as e:
            logger.critical(f"Emergency stop failed: {e}")
            return False

    def get_safety_status(self) -> dict[str, Any]:
        """Get comprehensive safety status"""
        if self.safety_manager:
            return self.safety_manager.get_safety_status()
        return {"safety_manager": "not_available"}

    def get_queue_status(self) -> dict[str, Any] | None:
        """Get action queue status"""
        if self.motion:
            return self.motion.get_queue_status()
        return None

    async def pause_queue(self):
        """Pause the action queue (emergency actions still execute)"""
        if self.motion and self.motion.action_queue:
            await self.motion.action_queue.pause()
            logger.warning(
                "⏸️ Action queue paused - only emergency actions will execute"
            )

    async def resume_queue(self):
        """Resume the action queue"""
        if self.motion and self.motion.action_queue:
            await self.motion.action_queue.resume()
            logger.info("▶️ Action queue resumed")

    # Convenience methods for common operations

    async def hello(self) -> bool:
        """Make robot wave hello"""
        return await self.command("hello")

    async def sit(self) -> bool:
        """Make robot sit down"""
        return await self.command("sit")

    async def stand_up(self) -> bool:
        """Make robot stand up"""
        return await self.command("standup")

    async def dance(self, dance_number: int = 1) -> bool:
        """Make robot dance"""
        return await self.command(f"dance{dance_number}")

    async def walk_square(self, side_length: float = 0.5) -> bool:
        """Make robot walk in a square pattern"""
        if not self.motion:
            return False
        try:
            return await self.motion.walk_square(side_length)
        except Exception as e:
            logger.error(f"Error walking square: {e}")
            return False

    async def spin_360(self, direction: str = "right") -> bool:
        """Make robot spin 360 degrees"""
        if not self.motion:
            return False
        try:
            return await self.motion.spin_360(direction)
        except Exception as e:
            logger.error(f"Error spinning 360: {e}")
            return False

    # Advanced Movement Methods
    async def front_flip(self) -> bool:
        """
        Execute front flip/somersault

        WARNING: This command may not be available in current firmware.
        Requires adequate space and soft landing area.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.front_flip()
        except Exception as e:
            logger.error(f"Error executing front flip: {e}")
            return False

    async def back_flip(self) -> bool:
        """
        Execute back flip/somersault

        WARNING: This command may not be available in current firmware.
        Requires adequate space and soft landing area.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.back_flip()
        except Exception as e:
            logger.error(f"Error executing back flip: {e}")
            return False

    async def left_flip(self) -> bool:
        """
        Execute left side flip

        WARNING: This command may not be available in current firmware.
        Requires adequate space and soft landing area.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.left_flip()
        except Exception as e:
            logger.error(f"Error executing left flip: {e}")
            return False

    async def right_flip(self) -> bool:
        """
        Execute right side flip

        WARNING: This command may not be available in current firmware.
        Requires adequate space and soft landing area.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.right_flip()
        except Exception as e:
            logger.error(f"Error executing right flip: {e}")
            return False

    async def front_jump(self) -> bool:
        """
        Execute forward jump

        This command has medium priority and may work in current firmware.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.front_jump()
        except Exception as e:
            logger.error(f"Error executing front jump: {e}")
            return False

    async def front_pounce(self) -> bool:
        """
        Execute pouncing motion

        This command has medium priority and may work in current firmware.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.front_pounce()
        except Exception as e:
            logger.error(f"Error executing front pounce: {e}")
            return False

    async def handstand(self, enable: bool = True) -> bool:
        """
        Enable/disable handstand mode

        WARNING: This command may not be available in current firmware.
        Previous versions required "ai" mode, which is no longer available.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.handstand(enable)
        except Exception as e:
            logger.error(f"Error executing handstand: {e}")
            return False

    async def test_advanced_movements(self) -> dict[str, bool]:
        """
        Test which advanced movements are available

        Returns:
            Dictionary mapping command names to availability status
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return {}
        try:
            return await self.motion.test_advanced_movement_availability()
        except Exception as e:
            logger.error(f"Error testing advanced movements: {e}")
            return {}

    # Basic Movement Methods
    async def damp(self) -> bool:
        """
        ⚠️ DANGER: DAMP COMMAND BLOCKED FOR SAFETY ⚠️

        This command reduces robot leg stiffness causing immediate collapse and damage!

        🚨 SAFETY PROTECTION: This method is blocked by ultra-safe systems to prevent
        expensive robot damage. The Damp command causes legs to lose stiffness and
        the robot will immediately collapse, potentially causing $1000s in damage.

        💡 SAFE ALTERNATIVES:
        - Use balance_stand() for stable positioning
        - Use recovery_stand() after falls or instability
        - Use emergency_stop() to halt dangerous movements

        Returns:
            False: Always returns False as command is blocked for safety
        """
        logger.critical(
            "🚨 DAMP COMMAND BLOCKED: This command causes robot leg collapse and damage!"
        )
        logger.critical(
            "💡 SAFETY PROTECTION: Damp reduces leg stiffness causing immediate robot collapse"
        )
        logger.info(
            "✅ SAFE ALTERNATIVES: Use robot.balance_stand() or robot.recovery_stand() instead"
        )
        logger.warning("⚠️  Protecting your valuable robot investment from damage")
        return False

    async def balance_stand(self) -> bool:
        """
        Enter balanced standing position

        This is the standard standing position and should work in all firmware modes.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.balance_stand()
        except Exception as e:
            logger.error(f"Error executing balance stand: {e}")
            return False

    async def recovery_stand(self) -> bool:
        """
        Execute recovery stand after fall or unstable position

        This is a safety command to help robot recover from falls.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            # Recovery commands get high priority for safety
            from .core.action_queue import ActionPriority

            return await self.motion.execute_sport_command(
                "RecoveryStand", priority=ActionPriority.HIGH
            )
        except Exception as e:
            logger.error(f"Error executing recovery stand: {e}")
            return False

    async def stand_down(self) -> bool:
        """
        Lower to lying position from standing

        This transitions the robot to a lying down position.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.stand_down()
        except Exception as e:
            logger.error(f"Error executing stand down: {e}")
            return False

    async def rise_sit(self) -> bool:
        """
        Rise from sitting position to standing

        This transitions the robot from sitting to standing position.
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.rise_sit()
        except Exception as e:
            logger.error(f"Error executing rise sit: {e}")
            return False

    async def move_basic(self, x: float = 0.3, y: float = 0, z: float = 0) -> bool:
        """
        Execute basic movement with simple parameters

        Args:
            x: Forward/backward movement (default: 0.3 for gentle forward)
            y: Left/right movement
            z: Rotation/yaw
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return False
        try:
            return await self.motion.move_basic(x, y, z)
        except Exception as e:
            logger.error(f"Error executing basic move: {e}")
            return False

    async def test_basic_movements(self) -> dict[str, bool]:
        """
        Test which basic movements are available

        Returns:
            Dictionary mapping command names to availability status
        """
        if not self.motion:
            logger.error("Not connected to robot")
            return {}
        try:
            return await self.motion.test_basic_movement_availability()
        except Exception as e:
            logger.error(f"Error testing basic movements: {e}")
            return {}

    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


# Convenience functions for quick usage
async def connect_robot(
    method: ConnectionMethod = ConnectionMethod.LOCALAP, **kwargs
) -> Robot:
    """
    Quick function to connect to a robot

    Args:
        method: Connection method to use
        **kwargs: Additional connection parameters

    Returns:
        Connected Robot instance
    """
    robot = Robot()
    success = await robot.connect(method, **kwargs)
    if not success:
        raise RuntimeError("Failed to connect to robot")
    return robot
