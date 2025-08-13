"""
Sparky Interfaces
Abstract base classes defining the public API contracts
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class ConnectionMethod(Enum):
    """Available connection methods"""

    LOCAL_AP = "localap"
    LOCAL_STA = "localsta"
    REMOTE = "remote"


class ConnectionInterface(ABC):
    """Abstract interface for robot connections"""

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to robot"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from robot"""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if currently connected"""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if connection is working properly"""
        pass

    @abstractmethod
    def get_connection_info(self) -> dict[str, Any]:
        """Get connection information and status"""
        pass


class MotionInterface(ABC):
    """Abstract interface for robot motion control"""

    @abstractmethod
    async def move_forward(
        self, speed: float, duration: float, verify: bool = True
    ) -> bool:
        """Move robot forward"""
        pass

    @abstractmethod
    async def move_backward(
        self, speed: float, duration: float, verify: bool = True
    ) -> bool:
        """Move robot backward"""
        pass

    @abstractmethod
    async def move_left(
        self, speed: float, duration: float, verify: bool = True
    ) -> bool:
        """Move robot left"""
        pass

    @abstractmethod
    async def move_right(
        self, speed: float, duration: float, verify: bool = True
    ) -> bool:
        """Move robot right"""
        pass

    @abstractmethod
    async def turn_left(
        self, speed: float, duration: float, verify: bool = True
    ) -> bool:
        """Turn robot left"""
        pass

    @abstractmethod
    async def turn_right(
        self, speed: float, duration: float, verify: bool = True
    ) -> bool:
        """Turn robot right"""
        pass

    @abstractmethod
    async def stop(self) -> bool:
        """Stop all robot movement"""
        pass

    @abstractmethod
    async def execute_sport_command(self, command: str, verify: bool = True) -> bool:
        """Execute a sport command"""
        pass

    @abstractmethod
    async def get_motion_mode(self) -> str | None:
        """Get current motion mode"""
        pass

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Get motion controller status"""
        pass


class DataInterface(ABC):
    """Abstract interface for data collection and streaming"""

    @abstractmethod
    async def start_collection(self) -> None:
        """Start data collection"""
        pass

    @abstractmethod
    async def stop_collection(self) -> None:
        """Stop data collection"""
        pass

    @abstractmethod
    async def get_latest_data(self) -> Any | None:
        """Get most recent sensor data"""
        pass

    @abstractmethod
    async def get_data_history(self, count: int) -> list[Any]:
        """Get recent data history"""
        pass

    @abstractmethod
    async def export_data(self, format_type: str) -> Any:
        """Export collected data"""
        pass

    @abstractmethod
    def get_collection_stats(self) -> dict[str, Any]:
        """Get data collection statistics"""
        pass


class AnalyticsInterface(ABC):
    """Abstract interface for movement analytics"""

    @abstractmethod
    async def is_robot_moving(self) -> bool:
        """Check if robot is currently moving"""
        pass

    @abstractmethod
    async def get_movement_direction(self) -> str:
        """Get current movement direction"""
        pass

    @abstractmethod
    async def get_movement_quality(self) -> str | None:
        """Get movement quality assessment"""
        pass

    @abstractmethod
    async def analyze_recent_performance(
        self, duration_seconds: float
    ) -> dict[str, Any]:
        """Analyze recent performance metrics"""
        pass

    @abstractmethod
    async def start_analysis(self) -> None:
        """Start analytics processing"""
        pass

    @abstractmethod
    async def stop_analysis(self) -> None:
        """Stop analytics processing"""
        pass


class RobotInterface(ABC):
    """High-level robot interface combining all functionality"""

    @abstractmethod
    async def connect(
        self, method: ConnectionMethod = ConnectionMethod.LOCAL_AP, **kwargs
    ) -> bool:
        """Connect to robot using specified method"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from robot"""
        pass

    @abstractmethod
    async def move(
        self, direction: str, speed: float = 0.5, duration: float = 2.0
    ) -> bool:
        """Move robot in specified direction"""
        pass

    @abstractmethod
    async def command(self, command: str) -> bool:
        """Execute a robot command"""
        pass

    @abstractmethod
    async def is_moving(self) -> bool:
        """Check if robot is moving"""
        pass

    @abstractmethod
    async def get_status(self) -> dict[str, Any]:
        """Get comprehensive robot status"""
        pass

    @abstractmethod
    async def start_data_stream(self) -> None:
        """Start data streaming and analytics"""
        pass

    @abstractmethod
    async def stop_data_stream(self) -> None:
        """Stop data streaming and analytics"""
        pass

    @abstractmethod
    async def export_data(self, format_type: str = "json") -> Any:
        """Export collected data"""
        pass
