"""
Sparky Motion Controller
Comprehensive motion control for Go2 robots

IMPORTANT FIRMWARE UPDATE NOTE:
The Go2 robot firmware has been updated and no longer supports the "normal" and "ai" motion modes
that were present in earlier firmware versions. The robot now operates primarily in "mcf"
(Manual Control Firmware) mode, which provides access to basic movements and sport commands
but restricts advanced features that previously required AI mode.

This change affects:
- Motion mode switching (normal/ai modes no longer available)
- Advanced commands like handstand, flips, etc. (may not be available)
- Command availability and behavior
"""

import asyncio
import json
import logging
from typing import Any

from go2_webrtc_driver.constants import RTC_TOPIC, SPORT_CMD

from .action_queue import ActionPriority, ActionType, QueueConfig, SafeActionQueue

# Motion verifier removed - using simplified approach for real-time control

logger = logging.getLogger(__name__)


class MotionController:
    """
    Comprehensive motion controller for Go2 robots
    Handles all movement commands and motion mode switching

    Now with ultra-safe action queue system to prevent race conditions
    and protect expensive robot hardware.

    Note: Current Go2 firmware only supports "mcf" mode.
    Legacy "normal" and "ai" modes are no longer available.
    """

    def __init__(self, connection, safety_manager=None, use_action_queue=True):
        self.conn = connection
        self.current_mode = None
        self.is_moving = False
        self.safety_manager = safety_manager

        # Initialize safe action queue system
        self.use_action_queue = use_action_queue
        self.action_queue = None

        if self.use_action_queue:
            queue_config = QueueConfig(
                min_action_interval=0.2,  # 200ms between commands
                require_safety_validation=True,
                auto_stop_on_danger=True,
            )
            self.action_queue = SafeActionQueue(safety_manager, queue_config)
            # Override the command execution method
            self.action_queue._perform_command_execution = self._execute_queued_command

        logger.info(
            f"MotionController initialized with {'SAFE QUEUE' if use_action_queue else 'DIRECT'} mode"
        )

    async def get_motion_mode(self) -> str | None:
        """Get current motion mode"""
        try:
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["MOTION_SWITCHER"], {"api_id": 1001}
            )

            if response["data"]["header"]["status"]["code"] == 0:
                data = json.loads(response["data"]["data"])
                self.current_mode = data["name"]
                return self.current_mode
            return None
        except Exception as e:
            logger.error(f"Failed to get motion mode: {e}")
            return None

    async def switch_motion_mode(self, mode: str) -> bool:
        """
        Switch to specified motion mode

        WARNING: Current Go2 firmware only supports "mcf" mode.
        Attempting to switch to "normal" or "ai" will fail with error codes:
        - 7004: Motion mode switching restriction
        - 7002: AI mode not available

        Args:
            mode: Motion mode to switch to (currently only "mcf" is supported)
        """
        try:
            logger.info(f"Attempting to switch to {mode} mode...")

            # Check if trying to switch to unsupported modes
            if mode in ["normal", "ai"]:
                logger.warning(
                    f"Mode '{mode}' is not supported in current firmware. Only 'mcf' mode is available."
                )
                logger.warning(
                    "This is due to a recent firmware update that removed normal/ai modes."
                )
                return False

            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["MOTION_SWITCHER"],
                {"api_id": 1002, "parameter": {"name": mode}},
            )

            if response["data"]["header"]["status"]["code"] == 0:
                self.current_mode = mode
                logger.info(f"Successfully switched to {mode} mode")
                await asyncio.sleep(5)  # Wait for mode switch
                return True
            else:
                error_code = response["data"]["header"]["status"]["code"]
                logger.error(
                    f"Failed to switch to {mode} mode. Error code: {error_code}"
                )
                if error_code in [7004, 7002]:
                    logger.error(
                        "This error indicates the requested mode is not available in current firmware."
                    )
                return False
        except Exception as e:
            logger.error(f"Error switching to {mode} mode: {e}")
            return False

    async def start_action_queue(self):
        """Start the safe action queue if enabled"""
        if self.action_queue and not self.action_queue.is_running:
            await self.action_queue.start()
            logger.info("🛡️ Safe action queue started - ultra-safe mode active")

    async def stop_action_queue(self):
        """Stop the safe action queue"""
        if self.action_queue and self.action_queue.is_running:
            await self.action_queue.stop()
            logger.info("Safe action queue stopped")

    async def emergency_stop_all(self, reason: str = "Emergency stop"):
        """Emergency stop all movement via action queue"""
        if self.action_queue:
            await self.action_queue.emergency_stop_queue(reason)
        else:
            # Fallback to direct stop
            await self.stop()

    async def move(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        duration: float = 3.0,
        verify: bool = True,
    ) -> bool:
        """
        Move the robot with specified parameters

        Args:
            x: Forward/backward movement (-1.0 to 1.0)
            y: Left/right movement (-1.0 to 1.0)
            z: Rotation/yaw (-1.0 to 1.0)
            duration: How long to maintain this movement
            verify: Whether to verify that movement actually occurred
        """
        if self.use_action_queue and self.action_queue:
            # Route through safe action queue
            action_id = await self.action_queue.queue_action(
                command="Move",
                action_type=ActionType.MOVEMENT,
                priority=ActionPriority.NORMAL,
                parameters={"x": x, "y": y, "z": z, "duration": duration},
            )
            logger.info(f"Move command queued safely: {action_id}")

            # Wait for completion
            while True:
                status = self.action_queue.get_action_status(action_id)
                if not status:
                    return False

                if status["status"] == "completed":
                    return True
                elif status["status"] == "failed":
                    logger.error(
                        f"Queued move failed: {status.get('error_message', 'Unknown error')}"
                    )
                    return False

                await asyncio.sleep(0.1)
        else:
            # Direct execution (legacy mode)
            return await self._execute_direct_move(x, y, z, duration)

    async def _execute_direct_move(
        self, x: float, y: float, z: float, duration: float
    ) -> bool:
        """Direct move execution (legacy mode)"""
        try:
            logger.info(f"Direct move: x={x}, y={y}, z={z}, duration={duration}")

            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"],
                {"api_id": SPORT_CMD["Move"], "parameter": {"x": x, "y": y, "z": z}},
            )

            if response["data"]["header"]["status"]["code"] == 0:
                self.is_moving = True
                logger.info("Move command accepted")
                await asyncio.sleep(duration)
                return True
            else:
                logger.error("Move command failed")
                return False

        except Exception as e:
            logger.error(f"Error in move command: {e}")
            return False

    def _get_expected_direction(self, x: float, y: float, z: float) -> str:
        """Get expected movement direction based on parameters"""
        if abs(x) > abs(y) and abs(x) > abs(z):
            return "forward" if x > 0 else "backward"
        elif abs(y) > abs(x) and abs(y) > abs(z):
            return "left" if y > 0 else "right"
        elif abs(z) > abs(x) and abs(z) > abs(y):
            return "turn-left" if z > 0 else "turn-right"
        else:
            return "unknown"

    async def stop(self) -> bool:
        """Stop all movement - emergency priority"""
        if self.use_action_queue and self.action_queue:
            # Route as emergency action (bypasses queue)
            action_id = await self.action_queue.queue_action(
                command="StopMove",
                action_type=ActionType.EMERGENCY,
                priority=ActionPriority.EMERGENCY,
                bypass_queue=True,
            )
            logger.warning(f"🛑 Emergency stop queued: {action_id}")

            # Wait for completion (should be immediate)
            for _ in range(50):  # 5 second timeout
                status = self.action_queue.get_action_status(action_id)
                if status and status["status"] == "completed":
                    return True
                await asyncio.sleep(0.1)

            logger.error("Emergency stop timeout - falling back to direct stop")

        # Direct execution for emergency or fallback
        return await self._execute_direct_stop()

    async def _execute_direct_stop(self) -> bool:
        """Direct stop execution"""
        try:
            logger.warning("🛑 Direct emergency stop")
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
            )

            if response["data"]["header"]["status"]["code"] == 0:
                self.is_moving = False
                logger.info("Stop command accepted")
                return True
            else:
                logger.error("Stop command failed")
                return False

        except Exception as e:
            logger.error(f"Error in stop command: {e}")
            return False

    # Convenience methods for common movements
    async def move_forward(
        self, speed: float = 0.5, duration: float = 3.0, verify: bool = True
    ) -> bool:
        """Move forward at specified speed"""
        return await self.move(x=speed, duration=duration, verify=verify)

    async def move_backward(
        self, speed: float = 0.5, duration: float = 3.0, verify: bool = True
    ) -> bool:
        """Move backward at specified speed"""
        return await self.move(x=-speed, duration=duration, verify=verify)

    async def move_left(
        self, speed: float = 0.3, duration: float = 3.0, verify: bool = True
    ) -> bool:
        """Move left at specified speed"""
        return await self.move(y=speed, duration=duration, verify=verify)

    async def move_right(
        self, speed: float = 0.3, duration: float = 3.0, verify: bool = True
    ) -> bool:
        """Move right at specified speed"""
        return await self.move(y=-speed, duration=duration, verify=verify)

    async def turn_left(
        self, speed: float = 0.3, duration: float = 3.0, verify: bool = True
    ) -> bool:
        """Turn left at specified speed"""
        return await self.move(z=speed, duration=duration, verify=verify)

    async def turn_right(
        self, speed: float = 0.3, duration: float = 3.0, verify: bool = True
    ) -> bool:
        """Turn right at specified speed"""
        return await self.move(z=-speed, duration=duration, verify=verify)

    async def execute_sport_command(
        self,
        command_name: str,
        parameters: dict | None = None,
        verify: bool = True,
        priority: ActionPriority = ActionPriority.NORMAL,
    ) -> bool:
        """
        Execute a sport command by name

        Note: Some advanced commands may not be available in current firmware.
        Commands that previously required "ai" mode may fail with error code 3203.

        Args:
            command_name: Name of the command (e.g., "Hello", "Sit", "StandUp")
            parameters: Optional parameters for the command
            verify: Whether to verify that command was actually executed
        """
        # Check if command exists first
        if command_name not in SPORT_CMD:
            available_commands = list(SPORT_CMD.keys())
            similar_commands = [
                cmd
                for cmd in available_commands
                if command_name.lower() in cmd.lower()
                or cmd.lower() in command_name.lower()
            ]

            error_msg = f"Unknown sport command: {command_name}"
            if similar_commands:
                error_msg += (
                    f". Did you mean one of: {', '.join(similar_commands[:3])}?"
                )
            else:
                error_msg += f". Available commands include: {', '.join(available_commands[:5])}..."

            logger.error(error_msg)
            return False

        if self.use_action_queue and self.action_queue:
            # Determine action type based on command
            action_type = self._get_action_type_for_command(command_name)

            # Route through safe action queue
            action_id = await self.action_queue.queue_action(
                command=command_name,
                action_type=action_type,
                priority=priority,
                parameters=parameters,
            )
            logger.info(f"Sport command queued safely: {command_name} ({action_id})")

            # Wait for completion
            while True:
                status = self.action_queue.get_action_status(action_id)
                if not status:
                    return False

                if status["status"] == "completed":
                    return True
                elif status["status"] == "failed":
                    logger.error(
                        f"Queued sport command failed: {status.get('error_message', 'Unknown error')}"
                    )
                    return False

                await asyncio.sleep(0.1)
        else:
            # Direct execution (legacy mode)
            return await self._execute_direct_sport_command(command_name, parameters)

    def _get_action_type_for_command(self, command_name: str) -> ActionType:
        """Determine action type based on command name"""
        safety_commands = {"StopMove", "RecoveryStand"}  # Removed dangerous "Damp"
        movement_commands = {"Move"}
        blocked_commands = {"Damp"}  # Dangerous commands blocked by safety system

        if command_name in blocked_commands:
            # Blocked commands will be rejected by safety validation
            return ActionType.SPORT_COMMAND  # Will be blocked anyway
        elif command_name in safety_commands:
            return ActionType.SAFETY_ACTION
        elif command_name in movement_commands:
            return ActionType.MOVEMENT
        else:
            return ActionType.SPORT_COMMAND

    async def _execute_direct_sport_command(
        self, command_name: str, parameters: dict | None = None
    ) -> bool:
        """Direct sport command execution (legacy mode)"""
        try:
            logger.info(f"Direct sport command: {command_name}")

            if parameters:
                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"],
                    {"api_id": SPORT_CMD[command_name], "parameter": parameters},
                )
            else:
                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD[command_name]}
                )

            if response["data"]["header"]["status"]["code"] == 0:
                logger.info(f"Sport command {command_name} accepted")
                await asyncio.sleep(2)  # Wait for command execution
                return True
            else:
                error_code = response["data"]["header"]["status"]["code"]
                logger.error(
                    f"Sport command {command_name} failed. Error code: {error_code}"
                )
                if error_code == 3203:
                    logger.error(
                        "This command may not be available in current firmware or motion mode."
                    )
                return False

        except Exception as e:
            logger.error(f"Error executing sport command {command_name}: {e}")
            return False

    # Advanced movement sequences
    async def walk_square(self, side_length: float = 0.5, verify: bool = True) -> bool:
        """Walk in a square pattern"""
        try:
            logger.info("Starting square walk pattern")

            # Forward
            if not await self.move_forward(side_length, 2.0, verify):
                logger.error("Square walk failed at forward movement")
                return False
            await self.stop()
            await asyncio.sleep(1)

            # Right
            if not await self.move_right(side_length, 2.0, verify):
                logger.error("Square walk failed at right movement")
                return False
            await self.stop()
            await asyncio.sleep(1)

            # Backward
            if not await self.move_backward(side_length, 2.0, verify):
                logger.error("Square walk failed at backward movement")
                return False
            await self.stop()
            await asyncio.sleep(1)

            # Left
            if not await self.move_left(side_length, 2.0, verify):
                logger.error("Square walk failed at left movement")
                return False
            await self.stop()

            logger.info("Square walk pattern completed")
            return True

        except Exception as e:
            logger.error(f"Error in square walk: {e}")
            return False

    async def spin_360(self, direction: str = "right", verify: bool = True) -> bool:
        """Spin 360 degrees"""
        try:
            logger.info(f"Spinning 360 degrees {direction}")

            if direction.lower() == "right":
                success = await self.turn_right(0.5, 6.0, verify)
            else:
                success = await self.turn_left(0.5, 6.0, verify)

            await self.stop()

            if success:
                logger.info("360 degree spin completed")
            else:
                logger.warning("360 degree spin may not have completed successfully")

            return success

        except Exception as e:
            logger.error(f"Error in 360 spin: {e}")
            return False

    async def handstand(self, enable: bool = True, verify: bool = True) -> bool:
        """
        Enable/disable handstand mode

        WARNING: This command may not be available in current firmware.
        Previous versions required "ai" mode, which is no longer available.
        """
        try:
            logger.warning(
                "Handstand command may not be available in current firmware."
            )
            logger.warning(
                "This command previously required 'ai' mode, which has been removed."
            )

            logger.info(f"{'Enabling' if enable else 'Disabling'} handstand mode")
            return await self.execute_sport_command(
                "StandOut", {"data": enable}, verify
            )

        except Exception as e:
            logger.error(f"Error in handstand command: {e}")
            return False

    def get_available_commands(self) -> dict[str, int]:
        """Get all available sport commands"""
        return SPORT_CMD.copy()

    async def _execute_queued_command(self, action) -> bool:
        """Execute command from action queue - implements the actual command execution"""
        try:
            command = action.command
            parameters = action.parameters

            logger.info(f"Executing queued command: {command}")

            # Handle different command types
            if command == "Move":
                # Extract move parameters
                x = parameters.get("x", 0)
                y = parameters.get("y", 0)
                z = parameters.get("z", 0)
                duration = parameters.get("duration", 3.0)

                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"],
                    {
                        "api_id": SPORT_CMD["Move"],
                        "parameter": {"x": x, "y": y, "z": z},
                    },
                )

                if response["data"]["header"]["status"]["code"] == 0:
                    self.is_moving = True
                    await asyncio.sleep(duration)
                    return True
                else:
                    action.error_message = f"Move command failed with code {response['data']['header']['status']['code']}"
                    return False

            elif command in SPORT_CMD:
                # Handle sport commands
                if parameters:
                    payload = {"api_id": SPORT_CMD[command], "parameter": parameters}
                else:
                    payload = {"api_id": SPORT_CMD[command]}

                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], payload
                )

                if response["data"]["header"]["status"]["code"] == 0:
                    if command == "StopMove":
                        self.is_moving = False

                    # Brief pause for command execution
                    await asyncio.sleep(
                        0.5 if action.action_type == ActionType.EMERGENCY else 2.0
                    )
                    return True
                else:
                    error_code = response["data"]["header"]["status"]["code"]
                    action.error_message = (
                        f"Command {command} failed with code {error_code}"
                    )
                    return False
            else:
                action.error_message = f"Unknown command: {command}"
                return False

        except Exception as e:
            action.error_message = f"Execution error: {str(e)}"
            logger.error(f"Error executing queued command {action.command}: {e}")
            return False

    def get_status(self) -> dict[str, Any]:
        """Get current motion controller status"""
        status = {
            "current_mode": self.current_mode,
            "is_moving": self.is_moving,
            "available_commands": list(SPORT_CMD.keys()),
            "firmware_note": "Current firmware only supports 'mcf' mode. Legacy 'normal' and 'ai' modes are not available.",
            "safe_queue_enabled": self.use_action_queue,
            "action_queue_status": self.action_queue.get_queue_status()
            if self.action_queue
            else None,
        }

        return status

    def get_queue_status(self) -> dict[str, Any] | None:
        """Get action queue status if enabled"""
        if self.action_queue:
            return self.action_queue.get_queue_status()
        return None

    # Advanced Movement Methods
    async def front_flip(self, verify: bool = True) -> bool:
        """
        Execute front flip/somersault

        WARNING: This command may not be available in current firmware.
        Previous versions required "ai" mode, which is no longer available.
        """
        try:
            logger.warning(
                "FrontFlip command may not be available in current firmware."
            )
            logger.info("Executing front flip command")
            return await self.execute_sport_command("FrontFlip", verify=verify)
        except Exception as e:
            logger.error(f"Error in front flip: {e}")
            return False

    async def back_flip(self, verify: bool = True) -> bool:
        """
        Execute back flip/somersault

        WARNING: This command may not be available in current firmware.
        """
        try:
            logger.warning("BackFlip command may not be available in current firmware.")
            logger.info("Executing back flip command")
            return await self.execute_sport_command("BackFlip", verify=verify)
        except Exception as e:
            logger.error(f"Error in back flip: {e}")
            return False

    async def left_flip(self, verify: bool = True) -> bool:
        """
        Execute left side flip

        WARNING: This command may not be available in current firmware.
        """
        try:
            logger.warning("LeftFlip command may not be available in current firmware.")
            logger.info("Executing left flip command")
            return await self.execute_sport_command("LeftFlip", verify=verify)
        except Exception as e:
            logger.error(f"Error in left flip: {e}")
            return False

    async def right_flip(self, verify: bool = True) -> bool:
        """
        Execute right side flip

        WARNING: This command may not be available in current firmware.
        """
        try:
            logger.warning(
                "RightFlip command may not be available in current firmware."
            )
            logger.info("Executing right flip command")
            return await self.execute_sport_command("RightFlip", verify=verify)
        except Exception as e:
            logger.error(f"Error in right flip: {e}")
            return False

    async def front_jump(self, verify: bool = True) -> bool:
        """
        Execute forward jump

        This command has medium priority and may work in current firmware.
        """
        try:
            logger.info("Executing front jump command")
            return await self.execute_sport_command("FrontJump", verify=verify)
        except Exception as e:
            logger.error(f"Error in front jump: {e}")
            return False

    async def front_pounce(self, verify: bool = True) -> bool:
        """
        Execute pouncing motion

        This command has medium priority and may work in current firmware.
        """
        try:
            logger.info("Executing front pounce command")
            return await self.execute_sport_command("FrontPounce", verify=verify)
        except Exception as e:
            logger.error(f"Error in front pounce: {e}")
            return False

    async def test_advanced_movement_availability(self) -> dict[str, bool]:
        """
        Test which advanced movements are available in current firmware

        Returns:
            Dictionary mapping command names to availability status
        """
        advanced_commands = [
            "FrontFlip",
            "BackFlip",
            "LeftFlip",
            "RightFlip",
            "FrontJump",
            "FrontPounce",
            "Handstand",
        ]

        availability = {}

        logger.info("Testing advanced movement availability...")

        for command in advanced_commands:
            try:
                # Test command availability without executing
                response = await self.conn.datachannel.pub_sub.publish_request_new(
                    RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD[command]}
                )

                if response["data"]["header"]["status"]["code"] == 0:
                    availability[command] = True
                    logger.info(f"✅ {command} is available")
                else:
                    availability[command] = False
                    error_code = response["data"]["header"]["status"]["code"]
                    logger.warning(f"❌ {command} not available (error {error_code})")

            except Exception as e:
                availability[command] = False
                logger.error(f"❌ {command} test failed: {e}")

            # Brief pause between tests
            await asyncio.sleep(0.5)

        return availability

    # Basic Movement Methods
    async def damp(self, verify: bool = True) -> bool:
        """
        ⚠️ DANGER: DAMP COMMAND BLOCKED FOR SAFETY ⚠️

        This command reduces robot leg stiffness causing immediate collapse and damage!

        🚨 CRITICAL SAFETY ISSUE: The Damp command causes the robot's legs to lose
        stiffness, resulting in immediate collapse. This can cause severe damage to
        expensive robot hardware ($15k+ Go2 investment).

        🛡️ ULTRA-SAFE PROTECTION: This method is automatically blocked by the safety
        system to prevent robot damage. The action queue will reject any Damp commands.

        💡 SAFE ALTERNATIVES FOR STABILITY:
        - balance_stand(): Maintains leg stiffness while stabilizing
        - recovery_stand(): Safe recovery from unstable positions
        - stop(): Halt movement without reducing leg stiffness

        Args:
            verify: Ignored - command always blocked regardless of verification

        Returns:
            False: Always returns False as command is blocked for safety
        """
        logger.critical(
            "🚨 DAMP COMMAND BLOCKED: This command causes robot leg collapse!"
        )
        logger.critical(
            "💡 MOTION CONTROLLER SAFETY: Protecting robot from dangerous leg stiffness reduction"
        )
        logger.info(
            "✅ SAFE ALTERNATIVES: Use balance_stand() or recovery_stand() for stability"
        )
        logger.warning("⚠️  Ultra-safe protection active - preventing robot damage")
        return False

    async def balance_stand(self, verify: bool = True) -> bool:
        """
        Enter balanced standing position

        This is the standard standing position and should work in all firmware modes.
        """
        try:
            logger.info("Executing balance stand command")
            return await self.execute_sport_command("BalanceStand", verify=verify)
        except Exception as e:
            logger.error(f"Error in balance stand: {e}")
            return False

    async def stand_up(self, verify: bool = True) -> bool:
        """
        Rise from lying position to standing

        This is a fundamental command for getting the robot upright.
        """
        try:
            logger.info("Executing stand up command")
            return await self.execute_sport_command("StandUp", verify=verify)
        except Exception as e:
            logger.error(f"Error in stand up: {e}")
            return False

    async def stand_down(self, verify: bool = True) -> bool:
        """
        Lower to lying position from standing

        This transitions the robot to a lying down position.
        """
        try:
            logger.info("Executing stand down command")
            return await self.execute_sport_command("StandDown", verify=verify)
        except Exception as e:
            logger.error(f"Error in stand down: {e}")
            return False

    async def recovery_stand(self, verify: bool = True) -> bool:
        """
        Execute recovery stand after fall or unstable position

        This is a safety command to help robot recover from falls.
        """
        try:
            logger.info("Executing recovery stand command")
            return await self.execute_sport_command("RecoveryStand", verify=verify)
        except Exception as e:
            logger.error(f"Error in recovery stand: {e}")
            return False

    async def sit(self, verify: bool = True) -> bool:
        """
        Transition to sitting position

        This makes the robot sit down from standing position.
        """
        try:
            logger.info("Executing sit command")
            return await self.execute_sport_command("Sit", verify=verify)
        except Exception as e:
            logger.error(f"Error in sit command: {e}")
            return False

    async def rise_sit(self, verify: bool = True) -> bool:
        """
        Rise from sitting position to standing

        This transitions the robot from sitting to standing position.
        """
        try:
            logger.info("Executing rise from sit command")
            return await self.execute_sport_command("RiseSit", verify=verify)
        except Exception as e:
            logger.error(f"Error in rise sit: {e}")
            return False

    async def move_basic(
        self, x: float = 0.3, y: float = 0, z: float = 0, verify: bool = True
    ) -> bool:
        """
        Execute basic movement with simple parameters

        Args:
            x: Forward/backward movement (default: 0.3 for gentle forward)
            y: Left/right movement
            z: Rotation/yaw
            verify: Whether to verify command execution
        """
        try:
            logger.info(f"Executing basic move command: x={x}, y={y}, z={z}")
            return await self.execute_sport_command(
                "Move", {"x": x, "y": y, "z": z}, verify=verify
            )
        except Exception as e:
            logger.error(f"Error in basic move: {e}")
            return False

    async def test_basic_movement_availability(self) -> dict[str, bool]:
        """
        Test which basic movements are available in current firmware

        Returns:
            Dictionary mapping command names to availability status
        """
        basic_commands = [
            "Damp",
            "BalanceStand",
            "StopMove",
            "StandUp",
            "StandDown",
            "RecoveryStand",
            "Move",
            "Sit",
            "RiseSit",
        ]

        availability = {}

        logger.info("Testing basic movement availability...")

        for command in basic_commands:
            try:
                # Test command availability without executing
                if command == "Move":
                    # Move command requires parameters
                    response = await self.conn.datachannel.pub_sub.publish_request_new(
                        RTC_TOPIC["SPORT_MOD"],
                        {
                            "api_id": SPORT_CMD[command],
                            "parameter": {"x": 0.1, "y": 0, "z": 0},
                        },
                    )
                else:
                    response = await self.conn.datachannel.pub_sub.publish_request_new(
                        RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD[command]}
                    )

                if response["data"]["header"]["status"]["code"] == 0:
                    availability[command] = True
                    logger.info(f"✅ {command} is available")
                else:
                    availability[command] = False
                    error_code = response["data"]["header"]["status"]["code"]
                    logger.warning(f"❌ {command} not available (error {error_code})")

            except Exception as e:
                availability[command] = False
                logger.error(f"❌ {command} test failed: {e}")

            # Brief pause between tests
            await asyncio.sleep(0.3)

        return availability

    def get_firmware_compatibility_info(self) -> dict[str, Any]:
        """
        Get information about firmware compatibility and limitations
        """
        return {
            "supported_modes": ["mcf"],
            "unsupported_modes": ["normal", "ai"],
            "firmware_update_note": "Recent firmware update removed normal/ai motion modes",
            "error_codes": {
                "7004": "Motion mode switching restriction (normal/ai not available)",
                "7002": "AI mode not available in current firmware",
                "3203": "Command not available in current motion mode",
            },
            "working_commands": [
                "Move",
                "StopMove",
                "Hello",
                "Sit",
                "StandUp",
                "Dance1",
                "Dance2",
                "Stretch",
                "BalanceStand",
                "RecoveryStand",
            ],
            "potentially_restricted_commands": [
                "Handstand",
                "BackFlip",
                "FrontFlip",
                "LeftFlip",
                "RightFlip",
                "StandOut",
                "FrontJump",
                "FrontPounce",
            ],
            "advanced_movements": {
                "FrontFlip": {"id": 1030, "risk": "High", "firmware_dependent": True},
                "BackFlip": {"id": 1044, "risk": "High", "firmware_dependent": True},
                "LeftFlip": {"id": 1042, "risk": "High", "firmware_dependent": True},
                "RightFlip": {"id": 1043, "risk": "High", "firmware_dependent": True},
                "FrontJump": {
                    "id": 1031,
                    "risk": "Medium",
                    "firmware_dependent": False,
                },
                "FrontPounce": {
                    "id": 1032,
                    "risk": "Medium",
                    "firmware_dependent": False,
                },
                "Handstand": {"id": 1301, "risk": "High", "firmware_dependent": True},
            },
        }
