"""
ASTRA-GUARD live webcam demo.

Phase 7.5.3 Step 4:
Connects the real webcam with:

Webcam
    ↓
YOLO + MediaPipe
    ↓
PerceptionEvent
    ↓
Protocol Object Mapping
    ↓
Protocol Object Validation
    ↓
Protocol Bridge
    ↓
Decision Engine
    ↓
Mission Status
    ↓
Live Visualization
    ↓
Mission Summary
"""

from __future__ import annotations

import cv2

from agent.mission.protocol_loader import ProtocolLoader
from agent.mission.decision_engine import DecisionEngine
from agent.mission.deviation_detector import DeviationDetector
from agent.mission.live_perception_session import LivePerceptionSession
from agent.mission.mission_status import MissionStatus
from agent.mission.perception_decision import PerceptionDecisionAdapter
from agent.mission.perception_bridge import PerceptionProtocolBridge
from agent.mission.sequence_validator import SequenceValidator
from agent.mission.state_machine import ProtocolStateMachine
from agent.mission.step_manager import StepManager

from agent.perception.hand_tracker import HandTracker
from agent.perception.live_overlay import LiveOverlay
from agent.perception.live_processor import LivePerceptionProcessor
from agent.perception.object_detector import ObjectDetector
from agent.perception.webcam_runtime import WebcamRuntime


def build_mission_session() -> LivePerceptionSession:
    """Build the ASTRA-GUARD mission using EXP001_TARDIGRADE."""

    protocol_path = "experiments/EXP001_TARDIGRADE"

    print(f"Loading protocol: {protocol_path}")

    protocol = ProtocolLoader(protocol_path).load()

    steps = protocol.get_steps()
    activities = protocol.get_activities()
    objects = protocol.get_objects()
    rules = protocol.get_rules()

    print(
        f"Protocol loaded: "
        f"{protocol.get_experiment().get('experiment_id')} - "
        f"{protocol.get_experiment().get('experiment_name')}"
    )

    print(f"Steps loaded: {len(steps)}")
    print(f"Activities loaded: {len(activities)}")
    print(f"Objects loaded: {len(objects)}")
    print(f"Rules loaded: {len(rules)}")

    # ---------------------------------------------------------
    # Protocol state
    # ---------------------------------------------------------

    state_machine = ProtocolStateMachine(
        steps
    )

    # ---------------------------------------------------------
    # Step management
    # ---------------------------------------------------------

    step_manager = StepManager(
        steps,
        state_machine,
        rules,
    )

    # ---------------------------------------------------------
    # Sequence validation
    # ---------------------------------------------------------

    validator = SequenceValidator(
        steps,
        activities,
    )

    # ---------------------------------------------------------
    # Deviation detection
    # ---------------------------------------------------------

    deviation_detector = DeviationDetector(
        steps,
        activities,
    )

    # ---------------------------------------------------------
    # Decision engine
    # ---------------------------------------------------------

    decision_engine = DecisionEngine(
        state_machine,
        step_manager,
        validator,
        deviation_detector,
        rules=rules,
    )

    # ---------------------------------------------------------
    # Connect protocol objects to perception bridge
    # ---------------------------------------------------------

    bridge = PerceptionProtocolBridge(
        protocol_objects=objects
    )

    # ---------------------------------------------------------
    # Perception → Decision adapter
    # ---------------------------------------------------------

    adapter = PerceptionDecisionAdapter(
        decision_engine,
        bridge=bridge,
        protocol_aware=True,
    )

    # ---------------------------------------------------------
    # Live perception session
    # ---------------------------------------------------------

    return LivePerceptionSession(
        adapter
    )


def main() -> None:
    """Start the ASTRA-GUARD live webcam demo."""

    print()
    print("=" * 60)
    print("ASTRA-GUARD LIVE DEMO")
    print("=" * 60)
    print()

    # ---------------------------------------------------------
    # Initialize mission system
    # ---------------------------------------------------------

    print("Initializing mission system...")

    session = build_mission_session()

    # Phase 11:
    # MissionStatus provides mission monitoring information.
    mission_status = MissionStatus(session)

    # ---------------------------------------------------------
    # Initialize YOLO
    # ---------------------------------------------------------

    print("Loading YOLO...")

    object_detector = ObjectDetector(
        model_path="yolo11n.pt",
        confidence_threshold=0.40,
    )

    # ---------------------------------------------------------
    # Initialize MediaPipe
    # ---------------------------------------------------------

    print("Loading MediaPipe hand tracker...")

    hand_tracker = HandTracker()

    # ---------------------------------------------------------
    # Live perception processor
    # ---------------------------------------------------------

    processor = LivePerceptionProcessor(
        object_detector,
        hand_tracker,
        session,
    )

    # ---------------------------------------------------------
    # Live overlay
    # ---------------------------------------------------------

    overlay = LiveOverlay()

    # ---------------------------------------------------------
    # Webcam runtime
    # ---------------------------------------------------------

    runtime = WebcamRuntime(
        processor,
        camera_index=0,
        width=1280,
        height=720,
    )

    print()
    print("ASTRA-GUARD is ready.")
    print("Press Q in the webcam window to exit.")
    print()

    try:
        runtime.open()

        while True:

            # -------------------------------------------------
            # Process one webcam frame
            # -------------------------------------------------

            result = runtime.process_once()

            # Original frame
            frame = result["frame"]

            # Perception event
            event = result["event"]

            # Protocol decision
            decision = result["result"]

            # -------------------------------------------------
            # Phase 11:
            # Get current mission status and progress
            # -------------------------------------------------

            status_data = mission_status.get_current_status()

            progress = status_data["progress"]

            # -------------------------------------------------
            # 1. Draw YOLO object detections
            # -------------------------------------------------

            display_frame = object_detector.draw_detections(
                frame,
                event.objects,
            )

            # -------------------------------------------------
            # 2. Draw MediaPipe hand landmarks
            # -------------------------------------------------

            display_frame = hand_tracker.draw_landmarks(
                display_frame,
                event.hands,
            )

            # -------------------------------------------------
            # 3. Draw ASTRA-GUARD decision + mission status
            # -------------------------------------------------

            display_frame = overlay.draw(
                display_frame,
                decision,
                mission_status=status_data,
            )

            # -------------------------------------------------
            # 4. Display final annotated frame
            # -------------------------------------------------

            cv2.imshow(
                "ASTRA-GUARD",
                display_frame,
            )

            # -------------------------------------------------
            # 5. Terminal mission status
            # -------------------------------------------------

            print(
                f"\r"
                f"Step: {status_data.get('step_id', 'UNKNOWN')} | "
                f"Status: {status_data.get('status', 'UNKNOWN')} | "
                f"Activity: {status_data.get('activity', 'UNKNOWN')} | "
                f"Object: {status_data.get('detected_object', 'NONE')} | "
                f"Progress: "
                f"{progress.get('progress_percent', 0)}%",
                end="",
                flush=True,
            )

            # -------------------------------------------------
            # 6. Check keyboard input
            # -------------------------------------------------

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    except KeyboardInterrupt:
        print()
        print()
        print("Stopping ASTRA-GUARD...")

    finally:
        # -----------------------------------------------------
        # Release webcam and perception resources
        # -----------------------------------------------------

        runtime.release()
        processor.close()
        cv2.destroyAllWindows()

        # -----------------------------------------------------
        # Phase 11 Step 6:
        # Display mission summary
        # -----------------------------------------------------

        summary = mission_status.get_summary()
        progress = mission_status.get_progress()

        print()
        print()
        print("=" * 60)
        print("              ASTRA-GUARD MISSION SUMMARY")
        print("=" * 60)
        print()

        print(
            f"Total Events: {summary['total_events']}"
        )

        print(
            f"Correct:      {summary['correct']}"
        )

        print(
            f"Deviations:   {summary['deviations']}"
        )

        print(
            f"Uncertain:    {summary['uncertain']}"
        )

        print(
            f"Completed:    {summary['completed']}"
        )

        print()

        print(
            f"Progress:     "
            f"{progress['completed_steps']}/"
            f"{progress['total_steps']} steps "
            f"({progress['progress_percent']:.1f}%)"
        )

        print()

        if progress["completed"]:
            print("Mission Status: COMPLETED")
        else:
            print("Mission Status: INCOMPLETE")

        print()
        print("=" * 60)
        print("ASTRA-GUARD stopped.")
        print("=" * 60)


if __name__ == "__main__":
    main()