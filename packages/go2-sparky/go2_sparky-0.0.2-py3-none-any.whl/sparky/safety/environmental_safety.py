"""
Environmental Safety Monitoring System for Sparky Robot
Comprehensive hazard detection and environmental risk assessment

This system protects expensive Go2 robot hardware by monitoring:
- Terrain conditions and surface safety
- Environmental hazards (water, obstacles, cliffs)
- Boundary violations and safe zone management
- External threats and collision risks
- Weather and temperature conditions

Real-time environmental analysis prevents costly damage from environmental hazards.
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


class EnvironmentalRisk(Enum):
    """Environmental risk assessment levels"""

    SAFE = 0  # Environment is safe for operation
    CAUTION = 1  # Minor environmental concerns
    WARNING = 2  # Significant environmental hazards
    DANGER = 3  # Immediate environmental threats
    CRITICAL = 4  # Critical environmental emergency


class HazardType(Enum):
    """Types of environmental hazards"""

    TERRAIN = "terrain"  # Unsafe ground conditions
    OBSTACLE = "obstacle"  # Physical obstacles
    CLIFF = "cliff"  # Drop-offs and edges
    WATER = "water"  # Water hazards
    TEMPERATURE = "temperature"  # Extreme temperatures
    BOUNDARY = "boundary"  # Safe zone violations
    COLLISION = "collision"  # Imminent collision risk
    SURFACE = "surface"  # Slippery/unstable surfaces
    SLOPE = "slope"  # Excessive slopes
    DEBRIS = "debris"  # Hazardous debris
    WEATHER = "weather"  # Weather conditions
    CROWD = "crowd"  # Crowded areas


@dataclass
class BoundaryZone:
    """Safe zone boundary definition"""

    center_x: float
    center_y: float
    radius: float
    zone_type: str = "safe"  # "safe", "warning", "forbidden"
    active: bool = True


@dataclass
class TerrainData:
    """Terrain condition information"""

    slope_angle: float = 0.0  # Degrees
    surface_roughness: float = 0.0  # 0.0 = smooth, 1.0 = very rough
    stability: float = 1.0  # 0.0 = unstable, 1.0 = stable
    friction: float = 1.0  # 0.0 = slippery, 1.0 = high friction
    timestamp: float = 0.0


@dataclass
class EnvironmentalConditions:
    """Current environmental conditions"""

    temperature: float = 20.0  # Celsius
    humidity: float = 50.0  # Percentage
    lighting: float = 1.0  # 0.0 = dark, 1.0 = bright
    air_quality: float = 1.0  # 0.0 = poor, 1.0 = excellent
    timestamp: float = 0.0


@dataclass
class HazardEvent:
    """Environmental hazard event record"""

    hazard_type: HazardType
    risk_level: EnvironmentalRisk
    location: tuple[float, float]  # x, y coordinates
    distance: float  # Distance to hazard (meters)
    severity: float  # 0.0 = minor, 1.0 = severe
    message: str
    timestamp: float
    response_taken: str | None = None
    resolved: bool = False


@dataclass
class SafetyLimits:
    """Environmental safety limits"""

    # Terrain limits
    max_safe_slope: float = 15.0  # Maximum slope angle (degrees)
    min_surface_stability: float = 0.7  # Minimum terrain stability
    min_surface_friction: float = 0.5  # Minimum friction coefficient

    # Distance limits
    min_obstacle_distance: float = 0.5  # Minimum distance to obstacles (meters)
    cliff_detection_distance: float = 1.0  # Distance for cliff detection
    collision_warning_distance: float = 1.5  # Collision warning distance

    # Environmental limits
    min_operating_temp: float = -10.0  # Minimum temperature (Celsius)
    max_operating_temp: float = 40.0  # Maximum temperature (Celsius)
    max_humidity: float = 90.0  # Maximum humidity (%)
    min_lighting: float = 0.3  # Minimum lighting level

    # Timing limits
    monitoring_interval: float = 0.1  # Environmental monitoring frequency
    hazard_timeout: float = 5.0  # Time to resolve hazards


class EnvironmentalSafetySystem:
    """
    Comprehensive environmental safety monitoring system

    Provides real-time environmental hazard detection and risk assessment
    to protect expensive robot hardware from environmental damage.
    """

    def __init__(self, connection, limits: SafetyLimits | None = None):
        self.conn = connection
        self.limits = limits or SafetyLimits()

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
        self.current_risk_level = EnvironmentalRisk.SAFE

        # Environmental data
        self.terrain_data = TerrainData()
        self.environmental_conditions = EnvironmentalConditions()
        self.detected_hazards: dict[HazardType, HazardEvent] = {}
        self.hazard_history: list[HazardEvent] = []

        # Safe zones and boundaries
        self.safe_zones: list[BoundaryZone] = []
        self.current_position = (0.0, 0.0)  # x, y
        self.position_history = deque(maxlen=100)  # 10 seconds at 10Hz

        # Sensor data buffers
        self.lidar_data = deque(maxlen=10)  # Recent LIDAR scans
        self.visual_data = deque(maxlen=10)  # Recent camera data
        self.sensor_timestamps = deque(maxlen=50)

        # Statistics
        self.stats = {
            "hazards_detected": 0,
            "hazards_avoided": 0,
            "boundary_violations": 0,
            "environmental_warnings": 0,
            "monitoring_uptime": 0,
            "start_time": time.time(),
        }

        logger.info(
            "Environmental Safety System initialized - protecting against external hazards"
        )

    async def start_monitoring(self):
        """Start environmental safety monitoring"""
        if self.is_monitoring:
            logger.warning("Environmental safety already monitoring")
            return

        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info("🌍 Environmental Safety monitoring started - scanning for hazards")

    async def stop_monitoring(self):
        """Stop environmental safety monitoring"""
        self.is_monitoring = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Environmental Safety monitoring stopped")

    async def _monitoring_loop(self):
        """Main environmental monitoring loop"""
        try:
            while self.is_monitoring:
                try:
                    # Update statistics
                    self.stats["monitoring_uptime"] = (
                        time.time() - self.stats["start_time"]
                    )

                    # Collect environmental data
                    await self._collect_environmental_data()

                    # Analyze terrain conditions
                    await self._analyze_terrain()

                    # Scan for obstacles and hazards
                    await self._scan_hazards()

                    # Check boundary compliance
                    await self._check_boundaries()

                    # Assess overall environmental risk
                    await self._assess_environmental_risk()

                    # Take protective actions if needed
                    await self._execute_environmental_protection()

                    # Clean up resolved hazards
                    await self._cleanup_resolved_hazards()

                    # 10Hz monitoring for environmental assessment
                    await asyncio.sleep(self.limits.monitoring_interval)

                except Exception as e:
                    logger.error(f"Error in environmental monitoring loop: {e}")
                    await asyncio.sleep(0.2)  # Slower cycle on errors

        except asyncio.CancelledError:
            logger.info("Environmental monitoring loop cancelled")
        except Exception as e:
            logger.critical(f"Critical error in environmental monitoring: {e}")

    async def _collect_environmental_data(self):
        """Collect environmental sensor data"""
        try:
            current_time = time.time()

            # In real implementation, this would read from:
            # - rt/utlidar/voxel_map for LIDAR data
            # - Video streams for visual hazard detection
            # - rt/lf/lowstate for robot position and orientation
            # - rt/gas_sensor for air quality
            # - System sensors for temperature

            # Update position (placeholder - would read from actual odometry)
            # self.current_position = await self._get_robot_position()
            self.position_history.append(
                {"position": self.current_position, "timestamp": current_time}
            )

            # Update environmental conditions (placeholder)
            self.environmental_conditions = EnvironmentalConditions(
                temperature=20.0,  # Would read from temperature sensors
                humidity=50.0,  # Would read from humidity sensors
                lighting=1.0,  # Would analyze camera brightness
                air_quality=1.0,  # Would read from gas sensors
                timestamp=current_time,
            )

            self.sensor_timestamps.append(current_time)

        except Exception as e:
            logger.error(f"Failed to collect environmental data: {e}")

    async def _analyze_terrain(self):
        """Analyze current terrain conditions"""
        try:
            # In real implementation, this would analyze LIDAR point clouds
            # to determine terrain characteristics

            current_time = time.time()

            # Placeholder terrain analysis
            # Would process LIDAR data to calculate:
            # - Surface slope angles
            # - Surface roughness
            # - Terrain stability
            # - Surface friction estimates

            self.terrain_data = TerrainData(
                slope_angle=0.0,  # Would calculate from point cloud
                surface_roughness=0.1,  # Would analyze surface variation
                stability=0.9,  # Would assess terrain stability
                friction=0.8,  # Would estimate friction
                timestamp=current_time,
            )

            # Check for terrain hazards
            if self.terrain_data.slope_angle > self.limits.max_safe_slope:
                await self._create_hazard_event(
                    HazardType.SLOPE,
                    EnvironmentalRisk.WARNING,
                    f"Excessive slope detected: {self.terrain_data.slope_angle:.1f}°",
                )

            if self.terrain_data.stability < self.limits.min_surface_stability:
                await self._create_hazard_event(
                    HazardType.SURFACE,
                    EnvironmentalRisk.CAUTION,
                    f"Unstable terrain detected: stability {self.terrain_data.stability:.2f}",
                )

        except Exception as e:
            logger.error(f"Terrain analysis error: {e}")

    async def _scan_hazards(self):
        """Scan for environmental hazards using sensors"""
        try:
            # In real implementation, this would:
            # 1. Process LIDAR data for obstacles and cliffs
            # 2. Analyze camera data for visual hazards
            # 3. Check sensor readings for environmental conditions

            await self._detect_obstacles()
            await self._detect_cliffs()
            await self._check_environmental_conditions()

        except Exception as e:
            logger.error(f"Hazard scanning error: {e}")

    async def _detect_obstacles(self):
        """Detect obstacles using LIDAR and visual data"""
        try:
            # Placeholder obstacle detection
            # Would process LIDAR point clouds to find:
            # - Static obstacles (walls, furniture, etc.)
            # - Dynamic obstacles (people, other robots)
            # - Small obstacles (debris, steps)

            # Example: detect obstacle at 0.8 meters ahead
            obstacle_distance = 0.8  # Would calculate from LIDAR

            if obstacle_distance < self.limits.collision_warning_distance:
                severity = max(
                    0.0,
                    1.0 - (obstacle_distance / self.limits.collision_warning_distance),
                )

                if obstacle_distance < self.limits.min_obstacle_distance:
                    risk_level = EnvironmentalRisk.DANGER
                else:
                    risk_level = EnvironmentalRisk.WARNING

                await self._create_hazard_event(
                    HazardType.OBSTACLE,
                    risk_level,
                    f"Obstacle detected at {obstacle_distance:.2f}m",
                    distance=obstacle_distance,
                    severity=severity,
                )

        except Exception as e:
            logger.error(f"Obstacle detection error: {e}")

    async def _detect_cliffs(self):
        """Detect cliffs and drop-offs"""
        try:
            # Placeholder cliff detection
            # Would analyze LIDAR data to detect:
            # - Sudden elevation changes
            # - Missing ground returns
            # - Edge detection

            # Example: Check for ground disappearance ahead
            ground_detected = True  # Would analyze LIDAR returns
            cliff_distance = 2.0  # Would calculate actual distance

            if (
                not ground_detected
                and cliff_distance < self.limits.cliff_detection_distance
            ):
                await self._create_hazard_event(
                    HazardType.CLIFF,
                    EnvironmentalRisk.DANGER,
                    f"Cliff detected at {cliff_distance:.2f}m ahead",
                    distance=cliff_distance,
                    severity=0.9,
                )

        except Exception as e:
            logger.error(f"Cliff detection error: {e}")

    async def _check_environmental_conditions(self):
        """Check environmental conditions for safety"""
        try:
            conditions = self.environmental_conditions

            # Temperature checks
            if (
                conditions.temperature < self.limits.min_operating_temp
                or conditions.temperature > self.limits.max_operating_temp
            ):
                await self._create_hazard_event(
                    HazardType.TEMPERATURE,
                    EnvironmentalRisk.WARNING,
                    f"Temperature outside safe range: {conditions.temperature:.1f}°C",
                )

            # Humidity checks
            if conditions.humidity > self.limits.max_humidity:
                await self._create_hazard_event(
                    HazardType.WEATHER,
                    EnvironmentalRisk.CAUTION,
                    f"High humidity detected: {conditions.humidity:.1f}%",
                )

            # Lighting checks
            if conditions.lighting < self.limits.min_lighting:
                await self._create_hazard_event(
                    HazardType.WEATHER,
                    EnvironmentalRisk.CAUTION,
                    f"Low light conditions: {conditions.lighting:.2f}",
                )

        except Exception as e:
            logger.error(f"Environmental conditions check error: {e}")

    async def _check_boundaries(self):
        """Check if robot is within safe boundaries"""
        try:
            if not self.safe_zones:
                return  # No boundaries defined

            current_pos = self.current_position

            for zone in self.safe_zones:
                if not zone.active:
                    continue

                # Calculate distance from zone center
                distance = math.sqrt(
                    (current_pos[0] - zone.center_x) ** 2
                    + (current_pos[1] - zone.center_y) ** 2
                )

                if zone.zone_type == "safe":
                    # Should be inside safe zone
                    if distance > zone.radius:
                        await self._create_hazard_event(
                            HazardType.BOUNDARY,
                            EnvironmentalRisk.WARNING,
                            f"Outside safe zone by {distance - zone.radius:.2f}m",
                            distance=distance,
                        )
                        self.stats["boundary_violations"] += 1

                elif zone.zone_type == "forbidden":
                    # Should be outside forbidden zone
                    if distance < zone.radius:
                        await self._create_hazard_event(
                            HazardType.BOUNDARY,
                            EnvironmentalRisk.DANGER,
                            f"Inside forbidden zone by {zone.radius - distance:.2f}m",
                            distance=distance,
                        )
                        self.stats["boundary_violations"] += 1

        except Exception as e:
            logger.error(f"Boundary check error: {e}")

    async def _assess_environmental_risk(self):
        """Assess overall environmental risk level"""
        try:
            if not self.detected_hazards:
                self.current_risk_level = EnvironmentalRisk.SAFE
                return

            # Find highest risk level among active hazards
            max_risk = max(
                hazard.risk_level
                for hazard in self.detected_hazards.values()
                if not hazard.resolved
            )

            old_risk_level = self.current_risk_level
            self.current_risk_level = max_risk

            # Log risk level changes
            if self.current_risk_level != old_risk_level:
                logger.warning(
                    f"Environmental risk changed: {old_risk_level.name} → {self.current_risk_level.name}"
                )

                if self.current_risk_level.value > EnvironmentalRisk.CAUTION.value:
                    self.stats["environmental_warnings"] += 1

        except Exception as e:
            logger.error(f"Risk assessment error: {e}")

    async def _execute_environmental_protection(self):
        """Execute protective actions based on environmental risks"""
        try:
            if self.current_risk_level == EnvironmentalRisk.CAUTION:
                await self._cautious_navigation()

            elif self.current_risk_level == EnvironmentalRisk.WARNING:
                await self._defensive_positioning()

            elif self.current_risk_level == EnvironmentalRisk.DANGER:
                await self._emergency_avoidance()

            elif self.current_risk_level == EnvironmentalRisk.CRITICAL:
                await self._environmental_emergency_stop()

        except Exception as e:
            logger.error(f"Environmental protection error: {e}")

    async def _cautious_navigation(self):
        """Implement cautious navigation for minor risks"""
        try:
            logger.info("⚠️ Implementing cautious navigation")

            # Reduce movement speed for safety
            # This would integrate with motion control to slow down
            # await self._reduce_movement_speed(0.5)

        except Exception as e:
            logger.error(f"Cautious navigation error: {e}")

    async def _defensive_positioning(self):
        """Implement defensive positioning for moderate risks"""
        try:
            logger.warning("🛡️ Implementing defensive positioning")

            # Stop movement and assess situation
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
            )

            # Enable balance stand for stability
            await asyncio.sleep(0.2)
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )

        except Exception as e:
            logger.error(f"Defensive positioning error: {e}")

    async def _emergency_avoidance(self):
        """Execute emergency avoidance maneuvers"""
        try:
            logger.critical("🚨 Executing emergency environmental avoidance")

            # Immediate stop
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
            )

            # Engage safe stabilization maintaining leg stiffness
            # NOTE: Previously used dangerous Damp which causes leg collapse
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["BalanceStand"]}
            )
            logger.info(
                "🛡️ Applied BalanceStand for environmental stability (avoiding dangerous Damp)"
            )

            self.stats["hazards_avoided"] += 1

        except Exception as e:
            logger.error(f"Emergency avoidance error: {e}")

    async def _environmental_emergency_stop(self):
        """Critical environmental emergency stop"""
        try:
            logger.critical("🚨 ENVIRONMENTAL EMERGENCY - Immediate stop")

            # Full emergency sequence
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["StopMove"]}
            )

            # Use safe stabilization instead of dangerous Damp
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["RecoveryStand"]}
            )
            logger.info(
                "🛡️ Applied RecoveryStand for collision response (avoiding dangerous Damp)"
            )

            # Try to achieve safest possible position
            await asyncio.sleep(0.5)
            await self.conn.datachannel.pub_sub.publish_request_new(
                RTC_TOPIC["SPORT_MOD"], {"api_id": SPORT_CMD["Sit"]}
            )

        except Exception as e:
            logger.critical(f"Environmental emergency stop error: {e}")

    async def _create_hazard_event(
        self,
        hazard_type: HazardType,
        risk_level: EnvironmentalRisk,
        message: str,
        distance: float = 0.0,
        severity: float = 0.5,
    ):
        """Create environmental hazard event"""
        try:
            event = HazardEvent(
                hazard_type=hazard_type,
                risk_level=risk_level,
                location=self.current_position,
                distance=distance,
                severity=severity,
                message=message,
                timestamp=time.time(),
            )

            self.detected_hazards[hazard_type] = event
            self.hazard_history.append(event)
            self.stats["hazards_detected"] += 1

            logger.warning(
                f"Environmental hazard detected: {hazard_type.value} - {message}"
            )

        except Exception as e:
            logger.error(f"Error creating hazard event: {e}")

    async def _cleanup_resolved_hazards(self):
        """Remove resolved or expired hazards"""
        current_time = time.time()
        resolved_hazards = []

        for hazard_type, event in self.detected_hazards.items():
            # Auto-resolve old hazards
            if current_time - event.timestamp > self.limits.hazard_timeout:
                event.resolved = True
                resolved_hazards.append(hazard_type)

        for hazard_type in resolved_hazards:
            del self.detected_hazards[hazard_type]
            logger.info(f"Hazard auto-resolved: {hazard_type.value}")

    def add_safe_zone(
        self, center_x: float, center_y: float, radius: float, zone_type: str = "safe"
    ):
        """Add a safe zone boundary"""
        zone = BoundaryZone(
            center_x=center_x, center_y=center_y, radius=radius, zone_type=zone_type
        )
        self.safe_zones.append(zone)
        logger.info(
            f"Added {zone_type} zone at ({center_x}, {center_y}) with radius {radius}m"
        )

    def clear_safe_zones(self):
        """Clear all safe zone boundaries"""
        self.safe_zones.clear()
        logger.info("All safe zones cleared")

    async def manual_hazard_scan(self) -> dict[str, Any]:
        """Perform manual environmental hazard scan"""
        await self._collect_environmental_data()
        await self._analyze_terrain()
        await self._scan_hazards()
        await self._check_boundaries()
        await self._assess_environmental_risk()

        return self.get_environmental_status()

    def get_environmental_status(self) -> dict[str, Any]:
        """Get comprehensive environmental status"""
        return {
            "risk_level": self.current_risk_level.name,
            "monitoring_active": self.is_monitoring,
            "current_position": self.current_position,
            "terrain_conditions": {
                "slope_angle": self.terrain_data.slope_angle,
                "surface_stability": self.terrain_data.stability,
                "surface_friction": self.terrain_data.friction,
            },
            "environmental_conditions": {
                "temperature": self.environmental_conditions.temperature,
                "humidity": self.environmental_conditions.humidity,
                "lighting": self.environmental_conditions.lighting,
                "air_quality": self.environmental_conditions.air_quality,
            },
            "active_hazards": {
                hazard_type.value: {
                    "risk_level": event.risk_level.name,
                    "message": event.message,
                    "distance": event.distance,
                    "severity": event.severity,
                    "age": time.time() - event.timestamp,
                }
                for hazard_type, event in self.detected_hazards.items()
                if not event.resolved
            },
            "safe_zones": [
                {
                    "center": (zone.center_x, zone.center_y),
                    "radius": zone.radius,
                    "type": zone.zone_type,
                    "active": zone.active,
                }
                for zone in self.safe_zones
            ],
            "recent_hazards": [
                {
                    "type": event.hazard_type.value,
                    "risk_level": event.risk_level.name,
                    "message": event.message,
                    "timestamp": event.timestamp,
                    "resolved": event.resolved,
                }
                for event in self.hazard_history[-10:]  # Last 10 events
            ],
            "stats": self.stats.copy(),
        }

    async def test_environmental_system(self) -> dict[str, bool]:
        """Test environmental safety system functionality"""
        logger.info("Testing environmental safety system...")

        results = {}

        try:
            # Test data collection
            await self._collect_environmental_data()
            results["data_collection"] = True

            # Test terrain analysis
            await self._analyze_terrain()
            results["terrain_analysis"] = True

            # Test hazard scanning
            await self._scan_hazards()
            results["hazard_scanning"] = True

            # Test boundary checking (if zones exist)
            await self._check_boundaries()
            results["boundary_checking"] = True

            # Test risk assessment
            await self._assess_environmental_risk()
            results["risk_assessment"] = True

            logger.info(f"Environmental safety test results: {results}")

        except Exception as e:
            logger.error(f"Environmental safety test failed: {e}")
            results["test_error"] = True

        return results

    def __del__(self):
        """Cleanup when environmental safety system is destroyed"""
        if self.is_monitoring:
            logger.warning(
                "Environmental safety destroyed while monitoring - this could be unsafe"
            )
