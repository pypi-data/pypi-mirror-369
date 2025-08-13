"""
Safe Action Queue System for Sparky Robot
Ultra-safe queue logic to prevent race conditions and protect expensive robot hardware

This system ensures:
- One command executes at a time (no race conditions)
- Safety validation before each command
- Emergency commands bypass queue for immediate execution
- Rate limiting to prevent too-rapid command sequences
- Integration with existing safety systems

Critical for protecting $15k+ Go2 robot investments.
"""

import asyncio
import logging
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any

logger = logging.getLogger(__name__)


class ActionPriority(IntEnum):
    """Action priority levels - higher numbers execute first"""

    EMERGENCY = 100  # Emergency stop, safety responses - bypass queue
    HIGH = 50  # Recovery commands, safety actions
    NORMAL = 10  # Regular movement commands
    LOW = 1  # Background tasks, non-critical actions


class ActionType(Enum):
    """Types of actions that can be queued"""

    MOVEMENT = "movement"  # Basic movements (forward, backward, etc.)
    SPORT_COMMAND = "sport_command"  # Sport commands (sit, stand, etc.)
    SAFETY_ACTION = "safety_action"  # Safety-related actions
    EMERGENCY = "emergency"  # Emergency responses
    SYSTEM = "system"  # System commands


class ActionStatus(Enum):
    """Status of actions in the queue"""

    PENDING = "pending"  # Waiting in queue
    VALIDATING = "validating"  # Safety validation in progress
    EXECUTING = "executing"  # Currently executing
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"  # Failed execution
    CANCELLED = "cancelled"  # Cancelled due to safety or conflict


@dataclass
class QueuedAction:
    """Action queued for execution"""

    action_id: str
    action_type: ActionType
    priority: ActionPriority
    command: str
    parameters: dict[str, Any]
    callback: Callable | None = None
    timestamp: float = None
    status: ActionStatus = ActionStatus.PENDING
    error_message: str | None = None
    execution_time: float | None = None
    safety_validated: bool = False

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class QueueConfig:
    """Configuration for the action queue"""

    # Timing constraints
    min_action_interval: float = 0.2  # Minimum time between actions (200ms)
    emergency_bypass_delay: float = 0.05  # Brief delay for emergency actions (50ms)
    safety_validation_timeout: float = 1.0  # Max time for safety validation
    command_execution_timeout: float = 5.0  # Max time for command execution

    # Queue limits
    max_queue_size: int = 50  # Maximum queued actions
    max_emergency_queue_size: int = 10  # Maximum emergency actions

    # Safety integration
    require_safety_validation: bool = True  # Require safety checks before execution
    auto_stop_on_danger: bool = True  # Auto-stop queue on safety danger
    safety_manager_required: bool = True  # Require SafetyManager integration


class SafeActionQueue:
    """
    Ultra-safe action queue system for robot command execution

    Prevents race conditions by serializing all commands and integrating
    with safety systems to protect expensive robot hardware.
    """

    def __init__(self, safety_manager=None, config: QueueConfig | None = None):
        self.safety_manager = safety_manager
        self.config = config or QueueConfig()

        # Queue management
        self.action_queue = asyncio.PriorityQueue(maxsize=self.config.max_queue_size)
        self.emergency_queue = asyncio.Queue(
            maxsize=self.config.max_emergency_queue_size
        )
        self.active_action: QueuedAction | None = None

        # State management
        self.is_running = False
        self.is_paused = False
        self.queue_task: asyncio.Task | None = None
        self.last_execution_time = 0
        self.action_counter = 0

        # Action tracking
        self.action_history = deque(maxlen=100)  # Keep last 100 actions
        self.pending_actions: dict[str, QueuedAction] = {}

        # Statistics
        self.stats = {
            "actions_queued": 0,
            "actions_executed": 0,
            "actions_failed": 0,
            "actions_cancelled": 0,
            "safety_blocks": 0,
            "emergency_bypasses": 0,
            "queue_start_time": 0,
        }

        # Validation
        if self.config.safety_manager_required and not self.safety_manager:
            logger.warning(
                "SafeActionQueue: No SafetyManager provided - some safety features disabled"
            )

        logger.info(
            "SafeActionQueue initialized - ultra-safe command execution enabled"
        )

    async def start(self):
        """Start the action queue processing"""
        if self.is_running:
            logger.warning("SafeActionQueue already running")
            return

        self.is_running = True
        self.stats["queue_start_time"] = time.time()
        self.queue_task = asyncio.create_task(self._queue_processor())

        logger.info(
            "🛡️ SafeActionQueue started - protecting robot with safe command execution"
        )

    async def stop(self):
        """Stop the action queue processing"""
        self.is_running = False

        if self.queue_task:
            self.queue_task.cancel()
            try:
                await self.queue_task
            except asyncio.CancelledError:
                pass

        # Cancel all pending actions
        await self._cancel_all_pending_actions("Queue stopped")

        logger.info("SafeActionQueue stopped")

    async def pause(self):
        """Pause queue processing (emergency actions still execute)"""
        self.is_paused = True
        logger.warning("⏸️ SafeActionQueue paused - only emergency actions will execute")

    async def resume(self):
        """Resume queue processing"""
        self.is_paused = False
        logger.info("▶️ SafeActionQueue resumed - normal processing active")

    async def queue_action(
        self,
        command: str,
        action_type: ActionType = ActionType.MOVEMENT,
        priority: ActionPriority = ActionPriority.NORMAL,
        parameters: dict[str, Any] | None = None,
        callback: Callable | None = None,
        bypass_queue: bool = False,
    ) -> str:
        """
        Queue an action for safe execution

        Args:
            command: Command to execute
            action_type: Type of action
            priority: Action priority level
            parameters: Command parameters
            callback: Optional callback when complete
            bypass_queue: If True, execute immediately (emergency only)

        Returns:
            action_id: Unique identifier for tracking
        """
        # Generate unique action ID
        self.action_counter += 1
        action_id = f"action_{self.action_counter}_{int(time.time() * 1000)}"

        # Create queued action
        action = QueuedAction(
            action_id=action_id,
            action_type=action_type,
            priority=priority,
            command=command,
            parameters=parameters or {},
            callback=callback,
        )

        # Safety check for emergency bypass
        if bypass_queue and priority != ActionPriority.EMERGENCY:
            logger.warning(
                f"Bypass requested for non-emergency action {command} - denying bypass"
            )
            bypass_queue = False

        try:
            if bypass_queue and priority == ActionPriority.EMERGENCY:
                # Emergency actions bypass main queue
                await self.emergency_queue.put(action)
                self.stats["emergency_bypasses"] += 1
                logger.critical(f"🚨 Emergency action queued (bypass): {command}")
            else:
                # Normal queue with priority
                await self.action_queue.put(
                    (priority.value * -1, action.timestamp, action)
                )
                self.stats["actions_queued"] += 1
                logger.info(
                    f"Action queued: {command} (priority: {priority.name}, id: {action_id})"
                )

            self.pending_actions[action_id] = action
            return action_id

        except asyncio.QueueFull as e:
            logger.error(f"Queue full - cannot queue action: {command}")
            raise RuntimeError("Action queue is full - system may be overloaded") from e

    async def cancel_action(
        self, action_id: str, reason: str = "User cancelled"
    ) -> bool:
        """Cancel a pending action"""
        if action_id not in self.pending_actions:
            return False

        action = self.pending_actions[action_id]

        if action.status == ActionStatus.EXECUTING:
            logger.warning(f"Cannot cancel executing action: {action_id}")
            return False

        action.status = ActionStatus.CANCELLED
        action.error_message = reason

        del self.pending_actions[action_id]
        self.action_history.append(action)
        self.stats["actions_cancelled"] += 1

        logger.info(f"Action cancelled: {action_id} - {reason}")
        return True

    async def emergency_stop_queue(self, reason: str = "Emergency stop"):
        """Emergency stop - clear queue and halt execution"""
        logger.critical(f"🚨 EMERGENCY STOP QUEUE: {reason}")

        # Pause queue
        await self.pause()

        # Cancel all pending actions
        await self._cancel_all_pending_actions(f"Emergency stop: {reason}")

        # Queue emergency stop action
        await self.queue_action(
            command="StopMove",
            action_type=ActionType.EMERGENCY,
            priority=ActionPriority.EMERGENCY,
            bypass_queue=True,
        )

    def get_queue_status(self) -> dict[str, Any]:
        """Get comprehensive queue status"""
        return {
            "running": self.is_running,
            "paused": self.is_paused,
            "queue_size": self.action_queue.qsize(),
            "emergency_queue_size": self.emergency_queue.qsize(),
            "pending_actions": len(self.pending_actions),
            "active_action": {
                "action_id": self.active_action.action_id,
                "command": self.active_action.command,
                "status": self.active_action.status.value,
                "elapsed_time": time.time() - self.active_action.timestamp,
            }
            if self.active_action
            else None,
            "last_execution": self.last_execution_time,
            "stats": self.stats.copy(),
            "config": {
                "min_action_interval": self.config.min_action_interval,
                "max_queue_size": self.config.max_queue_size,
                "require_safety_validation": self.config.require_safety_validation,
            },
        }

    def get_action_status(self, action_id: str) -> dict[str, Any] | None:
        """Get status of specific action"""
        if action_id in self.pending_actions:
            action = self.pending_actions[action_id]
        else:
            # Check history
            for action in reversed(self.action_history):
                if action.action_id == action_id:
                    break
            else:
                return None

        return {
            "action_id": action.action_id,
            "command": action.command,
            "action_type": action.action_type.value,
            "priority": action.priority.name,
            "status": action.status.value,
            "timestamp": action.timestamp,
            "execution_time": action.execution_time,
            "error_message": action.error_message,
            "safety_validated": action.safety_validated,
        }

    async def _queue_processor(self):
        """Main queue processing loop"""
        logger.info("SafeActionQueue processor started")

        try:
            while self.is_running:
                try:
                    # Check for emergency actions first (always execute)
                    if not self.emergency_queue.empty():
                        action = await self.emergency_queue.get()
                        await self._execute_action(action, is_emergency=True)
                        continue

                    # Skip normal queue if paused
                    if self.is_paused:
                        await asyncio.sleep(0.1)
                        continue

                    # Check for normal actions
                    if not self.action_queue.empty():
                        # Get highest priority action
                        (
                            priority_value,
                            timestamp,
                            action,
                        ) = await self.action_queue.get()

                        # Enforce minimum interval between actions
                        time_since_last = time.time() - self.last_execution_time
                        if time_since_last < self.config.min_action_interval:
                            delay = self.config.min_action_interval - time_since_last
                            logger.debug(
                                f"Rate limiting: waiting {delay:.3f}s before next action"
                            )
                            await asyncio.sleep(delay)

                        await self._execute_action(action)
                    else:
                        # No actions in queue - brief sleep
                        await asyncio.sleep(0.05)

                except Exception as e:
                    logger.error(f"Error in queue processor: {e}")
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("Queue processor cancelled")
        except Exception as e:
            logger.critical(f"Critical error in queue processor: {e}")

    async def _execute_action(self, action: QueuedAction, is_emergency: bool = False):
        """Execute a single action with safety validation"""
        self.active_action = action
        action.status = ActionStatus.EXECUTING
        execution_start = time.time()

        try:
            logger.info(
                f"{'🚨 EMERGENCY' if is_emergency else '🎯'} Executing: {action.command} (id: {action.action_id})"
            )

            # Safety validation (skip for emergency actions)
            if not is_emergency and self.config.require_safety_validation:
                action.status = ActionStatus.VALIDATING

                if not await self._validate_action_safety(action):
                    action.status = ActionStatus.FAILED
                    action.error_message = "Safety validation failed"
                    self.stats["safety_blocks"] += 1
                    logger.warning(
                        f"❌ Action blocked by safety validation: {action.command}"
                    )
                    return False

                action.safety_validated = True

            # Execute the actual command
            action.status = ActionStatus.EXECUTING
            success = await self._perform_command_execution(action)

            if success:
                action.status = ActionStatus.COMPLETED
                self.stats["actions_executed"] += 1
                logger.info(f"✅ Action completed: {action.command}")

                # Call callback if provided
                if action.callback:
                    try:
                        await action.callback(action, True, None)
                    except Exception as e:
                        logger.error(f"Error in action callback: {e}")
            else:
                action.status = ActionStatus.FAILED
                self.stats["actions_failed"] += 1
                logger.error(f"❌ Action failed: {action.command}")

                # Call callback with failure
                if action.callback:
                    try:
                        await action.callback(action, False, action.error_message)
                    except Exception as e:
                        logger.error(f"Error in failure callback: {e}")

            # Brief delay for emergency actions
            if is_emergency:
                await asyncio.sleep(self.config.emergency_bypass_delay)

            return success

        except Exception as e:
            action.status = ActionStatus.FAILED
            action.error_message = str(e)
            self.stats["actions_failed"] += 1
            logger.error(f"❌ Exception executing action {action.command}: {e}")
            return False

        finally:
            action.execution_time = time.time() - execution_start
            self.last_execution_time = time.time()

            # Move to history and remove from pending
            if action.action_id in self.pending_actions:
                del self.pending_actions[action.action_id]
            self.action_history.append(action)

            self.active_action = None

    async def _validate_action_safety(self, action: QueuedAction) -> bool:
        """Validate action against safety constraints"""

        # CRITICAL SAFETY CHECK: Block dangerous Damp commands
        if action.command == "Damp" or action.command.lower() == "damp":
            logger.critical(
                "🚨 DAMP COMMAND BLOCKED: This command causes robot leg collapse and damage!"
            )
            logger.critical(
                "💡 SAFETY RECOMMENDATION: Use 'BalanceStand' or 'RecoveryStand' for safe stabilization"
            )
            logger.critical(
                "⚠️  Damp reduces leg stiffness causing immediate robot collapse"
            )
            action.error_message = (
                "Damp command blocked by safety system - causes robot damage"
            )
            self.stats["safety_blocks"] += 1
            return False

        if not self.safety_manager:
            logger.debug("No safety manager - skipping validation")
            return True

        try:
            # Get current safety status
            safety_status = self.safety_manager.get_safety_status()

            # Block actions if emergency stop is active
            if safety_status.get("emergency_stop_active", False):
                logger.warning("Safety validation failed: Emergency stop active")
                return False

            # Block non-emergency actions in danger/emergency states
            if action.priority != ActionPriority.EMERGENCY:
                current_state = safety_status.get("state", "unknown")
                if current_state in ["danger", "emergency"]:
                    logger.warning(
                        f"Safety validation failed: Robot in {current_state} state"
                    )
                    return False

            # Check for conflicting active triggers
            active_triggers = safety_status.get("active_triggers", {})
            if active_triggers:
                logger.debug(f"Active safety triggers: {list(active_triggers.keys())}")

                # Block movement commands if there are active triggers
                if action.action_type == ActionType.MOVEMENT and active_triggers:
                    logger.warning(
                        "Safety validation failed: Active safety triggers present"
                    )
                    return False

            logger.debug(f"Safety validation passed for: {action.command}")
            return True

        except Exception as e:
            logger.error(f"Error in safety validation: {e}")
            return False  # Fail safe

    async def _perform_command_execution(self, action: QueuedAction) -> bool:
        """Perform the actual command execution - to be implemented by integration"""
        # This is a placeholder that will be implemented when integrating with MotionController
        logger.warning(f"Command execution not implemented: {action.command}")
        return False

    async def _cancel_all_pending_actions(self, reason: str):
        """Cancel all pending actions"""
        cancelled_count = 0

        for action_id in list(self.pending_actions.keys()):
            if await self.cancel_action(action_id, reason):
                cancelled_count += 1

        # Clear any remaining items in queues
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        while not self.emergency_queue.empty():
            try:
                self.emergency_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        logger.info(f"Cancelled {cancelled_count} pending actions: {reason}")
