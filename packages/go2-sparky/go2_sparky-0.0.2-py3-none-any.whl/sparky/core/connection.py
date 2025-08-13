"""
Sparky Connection Manager
Handles WebRTC connections to Go2 robots
"""

import logging
from typing import Any

from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod

logger = logging.getLogger(__name__)


class Go2Connection:
    """
    Manages WebRTC connection to Go2 robot
    Supports different connection methods and provides connection status
    """

    def __init__(
        self,
        connection_method: WebRTCConnectionMethod = WebRTCConnectionMethod.LocalAP,
        ip: str | None = None,
        serial_number: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        """
        Initialize connection manager

        Args:
            connection_method: WebRTC connection method
            ip: Robot IP address (for LocalSTA)
            serial_number: Robot serial number (for LocalSTA/Remote)
            username: Username (for Remote)
            password: Password (for Remote)
        """
        self.connection_method = connection_method
        self.ip = ip
        self.serial_number = serial_number
        self.username = username
        self.password = password
        self.conn = None
        self.is_connected = False
        self.connection_status = "disconnected"

    async def connect(self) -> bool:
        """Establish WebRTC connection to robot"""
        try:
            logger.info("Establishing WebRTC connection...")

            # Create connection based on method
            if self.connection_method == WebRTCConnectionMethod.LocalAP:
                self.conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)
            elif self.connection_method == WebRTCConnectionMethod.LocalSTA:
                if not self.ip and not self.serial_number:
                    raise ValueError(
                        "IP or serial number required for LocalSTA connection"
                    )
                if self.ip:
                    self.conn = Go2WebRTCConnection(
                        WebRTCConnectionMethod.LocalSTA, ip=self.ip
                    )
                else:
                    self.conn = Go2WebRTCConnection(
                        WebRTCConnectionMethod.LocalSTA, serialNumber=self.serial_number
                    )
            elif self.connection_method == WebRTCConnectionMethod.Remote:
                if not all([self.serial_number, self.username, self.password]):
                    raise ValueError(
                        "Serial number, username, and password required for Remote connection"
                    )
                self.conn = Go2WebRTCConnection(
                    WebRTCConnectionMethod.Remote,
                    serialNumber=self.serial_number,
                    username=self.username,
                    password=self.password,
                )
            else:
                raise ValueError(
                    f"Unsupported connection method: {self.connection_method}"
                )

            # Connect
            await self.conn.connect()
            self.is_connected = True
            self.connection_status = "connected"
            logger.info("WebRTC connection established successfully")
            return True

        except Exception as e:
            self.is_connected = False
            self.connection_status = "failed"
            logger.error(f"Failed to establish connection: {e}")
            return False

    async def disconnect(self) -> bool:
        """Disconnect from robot"""
        try:
            if self.conn:
                # Close connection if available
                if hasattr(self.conn, "close"):
                    await self.conn.close()
                self.conn = None

            self.is_connected = False
            self.connection_status = "disconnected"
            logger.info("Disconnected from robot")
            return True

        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
            return False

    def get_connection_info(self) -> dict[str, Any]:
        """Get connection information"""
        return {
            "connection_method": str(self.connection_method),
            "ip": self.ip,
            "serial_number": self.serial_number,
            "is_connected": self.is_connected,
            "connection_status": self.connection_status,
        }

    def is_ready(self) -> bool:
        """Check if connection is ready for commands"""
        return self.is_connected and self.conn is not None

    async def test_connection(self) -> bool:
        """Test if connection is working by sending a simple request"""
        try:
            if not self.is_ready():
                return False

            # Try to get motion mode as a connection test
            response = await self.conn.datachannel.pub_sub.publish_request_new(
                "rt/api/sport/request",  # Using a simple topic
                {"api_id": 1001},  # Simple request
            )

            return response["data"]["header"]["status"]["code"] == 0

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


# Connection factory functions for easy setup
async def create_local_ap_connection() -> Go2Connection:
    """Create connection using LocalAP method"""
    return Go2Connection(WebRTCConnectionMethod.LocalAP)


async def create_local_sta_connection(ip: str) -> Go2Connection:
    """Create connection using LocalSTA method with IP"""
    return Go2Connection(WebRTCConnectionMethod.LocalSTA, ip=ip)


async def create_local_sta_connection_by_serial(serial_number: str) -> Go2Connection:
    """Create connection using LocalSTA method with serial number"""
    return Go2Connection(WebRTCConnectionMethod.LocalSTA, serial_number=serial_number)


async def create_remote_connection(
    serial_number: str, username: str, password: str
) -> Go2Connection:
    """Create connection using Remote method"""
    return Go2Connection(
        WebRTCConnectionMethod.Remote,
        serial_number=serial_number,
        username=username,
        password=password,
    )
