# ASTRA-GUARD

### AI-Powered Onboard Monitoring and Protocol Validation System

ASTRA-GUARD is a prototype system for monitoring experimental activities and validating them against a predefined mission protocol.

It combines computer vision, hand tracking, protocol-aware perception, deterministic decision logic, and real-time guidance.

## Key Capabilities

- Real-time webcam perception
- YOLO object detection
- MediaPipe hand tracking
- Protocol-aware object mapping
- Mission state machine
- Sequence validation
- Deviation detection
- Confidence-based uncertainty handling
- Recovery guidance
- Live decision overlay
- Controlled demonstration mode
- Automated testing

## System Flow

```text
Webcam
   ↓
YOLO Object Detection
   ↓
MediaPipe Hand Tracking
   ↓
Perception Event
   ↓
Protocol-Aware Mapping
   ↓
Decision Engine
   ↓
CORRECT / DEVIATION / UNCERTAIN
   ↓
Guidance