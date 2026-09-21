# ASTRA-GUARD

### AI-Powered Onboard Monitoring and Protocol Validation System

ASTRA-GUARD is a prototype system for monitoring experimental activities and validating them against a predefined mission protocol.

It combines computer vision, hand tracking, protocol-aware perception, deterministic decision logic, and real-time guidance.

## Key Capabilities

* Real-time webcam perception
* YOLO object detection
* MediaPipe hand tracking
* Protocol-aware object mapping
* Mission state machine
* Sequence validation
* Deviation detection
* Confidence-based uncertainty handling
* Recovery guidance
* Live decision overlay
* Controlled demonstration mode
* Automated testing

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
```

## Demonstration Protocol

The main prototype uses:

**EXP001 - TARDIGRADE**

Domain: Biological Science
Environment: Microgravity
Protocol Type: Synthetic

The protocol contains eight steps:

```text
S001  CHECK_EQUIPMENT
S002  RETRIEVE_SAMPLE
S003  OPEN_CONTAINER
S004  TRANSFER_SAMPLE
S005  START_EXPERIMENT
S006  RECORD_RESULT
S007  SECURE_SAMPLE
S008  COMPLETE_EXPERIMENT
```

The protocol is synthetic and is not an official ISRO flight procedure or proprietary operational protocol.

## Decision Outcomes

### CORRECT

The observation matches the expected protocol condition.

### DEVIATION

The observation violates the expected protocol condition.

Examples include:

* Wrong object
* Wrong sequence
* Skipped step
* Premature action
* Unknown action

### UNCERTAIN

The system does not have sufficient confidence for a reliable decision and requests verification.

## Technology Stack

| Technology       | Purpose                     |
| ---------------- | --------------------------- |
| Python           | Core application            |
| OpenCV           | Camera and image processing |
| Ultralytics YOLO | Object detection            |
| MediaPipe        | Hand tracking               |
| PyYAML           | Protocol configuration      |
| PyTorch          | ML runtime                  |
| pytest           | Automated testing           |

## Running the Project

### Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### Main Demo Launcher

```powershell
python run.py
```

The launcher provides:

```text
1. Live Webcam Demo
2. Controlled Protocol Demo
3. Exit
```

### Controlled Protocol Demo

```powershell
python demo.py
```

This demonstrates:

```text
CORRECT
DEVIATION
UNCERTAIN
```

without requiring a webcam.

### Live Webcam Demo

```powershell
python run_live.py
```

Press `Q` in the webcam window to exit.

## Testing

Run the complete automated test suite:

```powershell
python -m pytest -q
```

Current regression result:

```text
124 passed
```

The test suite covers protocol loading, state management, sequence validation, deviation handling, perception integration, decision logic, simulation, and related components.

## Architecture

```text
Perception Layer
      ↓
Object + Hand Detection
      ↓
Perception Event
      ↓
Protocol Integration
      ↓
Mission State Machine
      ↓
Sequence Validation
      ↓
Deviation Detection
      ↓
Decision Engine
      ↓
Guidance / Recovery
```

## Project Structure

```text
ASTRA-GUARD/
├── agent/
├── backend/
├── data/
├── deployment/
├── docs/
├── experiments/
├── frontend/
├── models/
├── scripts/
├── simulation/
├── tests/
├── training/
├── video/
├── demo.py
├── run.py
├── run_live.py
├── requirements.txt
└── yolo11n.pt
```

## Protocol Configuration

The main synthetic protocol is located at:

```text
experiments/EXP001_TARDIGRADE/
```

It contains:

```text
activities.yaml
experiment.yaml
objects.yaml
rules.yaml
steps.yaml
```

These files define the experiment metadata, activities, protocol objects, validation rules, and ordered mission steps.

## Prototype Limitations

The current prototype uses a generic YOLO model with deterministic mapping to protocol-level objects.

It is **not** a custom astronaut-specific object detection model.

The current activity interpreter uses protocol state and perception signals rather than a trained human-action recognition model.

The system should therefore be understood as a protocol-aware prototype combining generic visual perception with deterministic interpretation and validation.

The decision engine is deterministic and rule-based.

The current prototype does **not** use an LLM for activity interpretation or decision making.

## Vision and Object Mapping

The prototype uses a generic YOLO model for object detection.

Detected generic objects are mapped to protocol-level objects where applicable.

```text
Generic Detection
      ↓
Object Mapping
      ↓
Protocol Object
```

This allows the prototype to demonstrate protocol validation without claiming a specialized mission-trained vision model.

## Controlled Demonstration

The controlled demonstration is designed to show three decision outcomes:

```text
Expected Action
      ↓
   CORRECT
```

```text
Wrong Object / Sequence
      ↓
   DEVIATION
```

```text
Low Confidence
      ↓
   UNCERTAIN
```

This provides a deterministic presentation path even when specialized protocol objects are not directly detectable by the generic YOLO model.

## Live Demonstration

The live webcam pipeline follows:

```text
Webcam
   ↓
YOLO + MediaPipe
   ↓
Perception Processing
   ↓
Protocol-Aware Mapping
   ↓
Decision Adapter
   ↓
Decision Engine
   ↓
Live Overlay
```

The overlay displays information such as:

* Current protocol step
* Detected activity
* Detected object
* Confidence
* Expected activity
* Expected object
* Decision status
* Deviation reason
* Guidance

## Documentation

Detailed project documentation is available in:

```text
docs/
```

Documentation includes:

```text
docs/
├── README.md
├── architecture/
├── development/
├── experiment/
├── deployment/
├── demo/
└── images/
```

See `docs/README.md` for the documentation index and recommended reading order.

## Development and Deployment

Development setup:

```text
docs/development/setup.md
```

Development guide:

```text
docs/development/development-guide.md
```

Deployment guide:

```text
docs/deployment/deployment-guide.md
```

Demo guide:

```text
docs/demo/demo-guide.md
```

## Future Development

Potential future improvements include:

* Domain-specific object detection
* Advanced action recognition
* Astronaut pose estimation
* Temporal activity recognition
* Edge-device optimization
* Voice guidance
* Mission telemetry integration
* Additional experimental protocols
* Onboard/offline deployment
* Specialized space-environment datasets

## Project Status

**Prototype: Operational**

The implemented prototype includes:

* Protocol loading
* Mission state management
* Sequence validation
* Deviation detection
* Rule-based decision making
* Synthetic protocol simulation
* Generic object perception
* Hand tracking
* Perception-to-protocol integration
* Live webcam processing
* Decision overlay
* Controlled demonstration
* Automated testing

Current automated regression:

```text
124 passed
```

## Academic / Prototype Disclaimer

ASTRA-GUARD is an academic research and demonstration prototype.

The included `EXP001 - TARDIGRADE` protocol is synthetic and is not an official ISRO flight procedure, operational mission procedure, or proprietary protocol.

The system is intended to demonstrate the concept of protocol-aware monitoring and validation.

## License

This repository is intended for academic, educational, and demonstration purposes.

Add an explicit open-source license such as MIT only if the project team has decided to release the code under that license.
