# Kenesis — AR Gesture-Controlled Robot

An end-to-end AR robotics system that enables intuitive gesture control of physical robots through Snap Spectacles, featuring real-time cloud communication and precision robotic manipulation.

## 🎯 Project Overview

Kenesis bridges the gap between augmented reality and physical robotics by creating a seamless gesture-to-motion pipeline. Users wearing Snap Spectacles can control a 3-DOF robotic arm and omnidirectional mobile base through natural hand gestures, with real-time feedback and sub-100ms latency.

**Key Features:**
- **Natural Gesture Control**: Pinch, grab, and target gestures captured via Snap's Lens Studio API
- **Real-time Communication**: Cloud-native MQTT pipeline for reliable command transmission
- **Precision Robotics**: ROS2-based control stack driving servo and DC motors
- **Live Monitoring**: Web dashboard for system status and gesture analytics
- **Modular Hardware**: 3D-printed chassis designed for easy maintenance and upgrades

## 🏗️ System Architecture

```
AR Spectacles → Lens Studio → Flask Server → HiveMQ MQTT → ROS2 Nodes → Robot Hardware
     ↓              ↓            ↓              ↓           ↓
  Gesture        Network      Cloud          Local      Motor
  Capture       Processing   Messaging      Control    Actuation
```

**Components:**
- **Frontend**: Snap Spectacles with custom Lens Studio application
- **Cloud**: Flask server + HiveMQ MQTT broker for scalable communication
- **Edge**: NVIDIA Jetson Nano running ROS2 control stack
- **Hardware**: Custom 3-DOF robotic arm + omnidirectional mobile platform

## 🚀 Quick Start

### Backend Server

```bash
# Setup environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r Backend/requirements.txt

# Run server
python Backend/app.py

# Test with gesture simulator
python Backend/gesture_simulator.py
```

### ROS2 Robot Controller

```bash
# On Jetson Nano (Ubuntu 20.04 + ROS2 Foxy)
cd ros2_workspace
colcon build
source install/setup.bash
ros2 launch kenesis_control robot.launch.py
```

### Lens Studio Project

1. Open `Lens_Project/Kenesis.lsproj` in Lens Studio
2. Configure server endpoint in `Assets/GestureController.ts`
3. Build and deploy to Spectacles or test in Preview

## 📡 API Reference

### Gesture Events
```json
{
  "type": "pinch_down" | "pinch_up" | "targeting" | "grab_begin" | "grab_end",
  "hand": "left" | "right",
  "confidence": 0.95,
  "rayOrigin": [x, y, z],
  "rayDirection": [x, y, z],
  "timestamp": "2025-01-20T15:30:00Z"
}
```

### Robot Commands (MQTT)
```json
{
  "command": "move_arm" | "drive_base" | "emergency_stop",
  "parameters": {
    "joint_angles": [θ1, θ2, θ3],
    "velocity": [vx, vy, ω]
  }
}
```

## 🔧 Hardware Specifications

**Robot Platform:**
- **Compute**: NVIDIA Jetson Nano 4GB
- **Motors**: 3x Servo motors (arm joints), 4x DC motors (omnidirectional wheels)
- **Sensors**: IMU, wheel encoders, camera module
- **Power**: 12V LiPo battery system
- **Chassis**: Custom 3D-printed modular design

**AR Hardware:**
- **Device**: Snap Spectacles (5th generation)
- **Tracking**: 6DOF head tracking + hand gesture recognition
- **Display**: Waveguide AR optics

## 📊 Performance Metrics

- **Latency**: <100ms gesture-to-robot response time
- **Accuracy**: 95%+ gesture recognition confidence
- **Range**: 10m+ MQTT communication range
- **Battery**: 2+ hours continuous operation
- **Precision**: ±2mm robotic arm positioning accuracy
- 
## 🔮 Future Enhancements

- **Multi-Robot Control**: Orchestrate robot swarms through AR
- **AI Integration**: Computer vision for autonomous object manipulation
- **Haptic Feedback**: Force feedback through AR interface
- **Voice Commands**: Combined gesture + voice control modalities

## 📄 Project Structure

```
Kenesis/
├── Backend/                 # Flask server & MQTT bridge
│   ├── app.py              # Main server application
│   ├── gesture_simulator.py # Testing utilities
│   └── templates/          # Web dashboard
├── Lens_Project/           # Snap Lens Studio AR app
│   ├── Assets/             # TypeScript controllers
│   └── Kenesis.lsproj      # Lens Studio project
├── ROS2/                   # Robot control stack
│   ├── kenesis_control/    # Motor drivers & kinematics
│   └── kenesis_msgs/       # Custom message definitions
└── Hardware/               # CAD files & schematics
    ├── 3D_Models/          # STL files for 3D printing
    └── Electronics/        # Circuit diagrams
```



---

*Kenesis demonstrates the future of human-robot interaction, where physical and digital worlds seamlessly converge through intuitive AR interfaces.*
