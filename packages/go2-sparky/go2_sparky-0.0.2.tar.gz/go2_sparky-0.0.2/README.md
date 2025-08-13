#  Sparky - Go2 Robot Control

**Fast, simple robot control optimized for Vision Pro integration and real-time applications.**

Perfect for Python beginners, researchers, and Vision Pro developers who need responsive robot control.

![Sparky CLI Banner](docs/cli_banner.png)

---

##  **Vision Pro Ready**

```python
from sparky import Robot

async def vision_pro_control():
    async with Robot() as robot:
        await robot.connect()
        await robot.hello()                    # Wave gesture
        await robot.move('forward', 0.3, 2.0)  # Move forward
        status = await robot.get_status()      # Real-time monitoring
```

##  **Quick Start**

### Installation
```bash
# From project directory
pip install -e .

# Or with Poetry
poetry install

# For development (with all tools)
poetry install --extras dev
# or using Task
task install
```

### Simple Demo
```python
import asyncio
from sparky import Robot

async def demo():
    robot = Robot()
    await robot.connect()         # Auto-connects via robot WiFi
    await robot.hello()           # Wave hello
    await robot.sit()             # Sit down
    await robot.stand_up()        # Stand up
    await robot.disconnect()      # Clean disconnect

asyncio.run(demo())
```

##  **Why Sparky?**

- ** Vision Pro Optimized** - Perfect for gesture-based control
- ** Real-time Focus** - No verification overhead, maximum speed
- ** Beginner Friendly** - Simple async/await patterns  
- ** Mobile Ready** - Lightweight, responsive API
- ** Auto-connection** - Handles connection methods automatically

##  **Examples**

### For Vision Pro Apps
- [`examples/vision_pro_example.py`](examples/vision_pro_example.py) - Perfect integration patterns
- Simple async/await control
- Real-time status monitoring
- Context manager support

### For Beginners
- [`examples/simple_robot_control.py`](examples/simple_robot_control.py) - Interactive demo
- [`examples/basic/`](examples/basic/) - Getting started examples

### Advanced Examples  
- [`examples/data_streaming/`](examples/data_streaming/) - Data collection & analytics
- [`examples/testing/`](examples/testing/) - Robot testing & diagnostics
- [`examples/advanced/`](examples/advanced/) - Complex demonstrations

## 🌐 **Connection Methods**

Sparky automatically tries connection methods in order:

1. **LocalAP** (default) - Robot's WiFi hotspot
2. **Router** - Shared network (if robot IP provided)

```python
# Default (LocalAP)
await robot.connect()

# Specific method  
from sparky import ConnectionMethod
await robot.connect(ConnectionMethod.ROUTER, ip="192.168.1.100")
```

##  **Available Commands**

### Basic Movements
```python
await robot.move('forward', speed=0.3, duration=2.0)
await robot.move('backward', speed=0.3, duration=2.0) 
await robot.move('left', speed=0.3, duration=2.0)
await robot.move('right', speed=0.3, duration=2.0)
await robot.move('turn-left', speed=0.3, duration=2.0)
await robot.move('turn-right', speed=0.3, duration=2.0)
```

### Gestures & Commands
```python
await robot.hello()        # Wave hello
await robot.sit()          # Sit down  
await robot.stand_up()     # Stand up
await robot.dance(1)       # Dance routine
```

### Advanced Patterns
```python
await robot.walk_square(0.5)   # Walk in square
await robot.spin_360('right')  # Spin 360 degrees
```

##  **Real-time Monitoring**

```python
# Basic status
status = await robot.get_status()
is_moving = await robot.is_moving()

# Data streaming
await robot.start_data_stream()
sensor_data = await robot.get_current_sensor_data()
await robot.stop_data_stream()
```

##  **Firmware Compatibility**

**Current Go2 firmware operates in "mcf" mode only:**

-  **All basic movements work perfectly**
-  **Most gesture commands work** (hello, sit, stand, dance)
-  **Advanced commands unavailable** (handstand, flips)
-  **Motion mode switching disabled**

## 🛠 **Advanced Usage**

For power users, the full API is available:

```python
from sparky import Go2Connection, MotionController, DataCollector
from sparky.utils.constants import ConnectionMethod, MovementDirection

# Direct component access
connection = Go2Connection(ConnectionMethod.LOCALAP)
motion = MotionController(connection.conn)
data = DataCollector(connection.conn)
```

## 🤝 **Need Help?**

### Getting Started
1. **New to robotics?** → [`examples/simple_robot_control.py`](examples/simple_robot_control.py)
2. **Building Vision Pro apps?** → [`examples/vision_pro_example.py`](examples/vision_pro_example.py) 
3. **Need real-time data?** → [`examples/basic/data_stream_basic_example.py`](examples/basic/data_stream_basic_example.py)

### Common Issues
- **Connection fails?** → Check robot is powered on and WiFi accessible
- **Commands don't work?** → Run `task test-robot` or `python examples/testing/motion_test.py` 
- **Import errors?** → Ensure `task install` or `pip install -e .` was run successfully

### Examples Structure
- **`examples/`** - All examples, organized by complexity and use case
  - **Main examples** - Vision Pro integration, beginner demos
  - **`basic/`** - Getting started examples
  - **`data_streaming/`** - Data collection & analytics
  - **`testing/`** - Robot testing & diagnostics  
  - **`advanced/`** - Complex demonstrations
- **`driver_examples/`** - Hardware reference (audio, video, sensors)

## 🛠 **Development & Testing**

### Task Automation
We use [Task](https://taskfile.dev/) for streamlined development workflows:

```bash
# Development setup
task dev                 # Set up development environment
task install            # Install all dependencies

# Code quality
task format             # Format code with ruff
task check              # Run all quality checks
task ci                 # Run full CI checks locally

# Build & test
task build              # Build package
task clean              # Clean artifacts

# Robot testing
task run-examples       # List available examples
task test-robot         # Quick robot connectivity test
task run-example examples/simple_robot_control.py
```

### GitHub CI/CD
Automated workflows ensure code quality and seamless publishing:

- **Quality Checks** - Automatic testing on push/PR (ruff, mypy, pytest, safety)
- **Test Reports** - Coverage reporting and test results in PRs
- **Auto Publishing** - PyPI deployment on git tags

See all available tasks: `task --list`

## 🏗 **Architecture**

```
sparky/
├── Robot              #  Simple API (start here!)
├── ConnectionMethod   # 🌐 Connection types  
├── core/             #  Advanced components
│   ├── connection.py # WebRTC management
│   ├── motion.py     # Robot control  
│   ├── data_collector.py # Sensor streaming
│   └── analytics_engine.py # Real-time analysis
└── utils/            # 📦 Constants & exceptions
```

---

**Perfect for:** Vision Pro apps • Real-time control • Python beginners • Research • Mobile robotics

**Built with:** WebRTC • AsyncIO • Python 3.11+ • Poetry • Task • GitHub Actions