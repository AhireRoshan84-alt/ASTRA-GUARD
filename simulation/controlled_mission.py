
"""
ASTRA-GUARD Controlled Mission Demonstration.

Uses the real ASTRA-GUARD perception-to-decision pipeline
with controlled perception events.

Demonstrates:
- CORRECT
- DEVIATION
- UNCERTAIN
- Recovery
- Complete protocol progression
"""

from __future__ import annotations

from agent.mission.protocol_loader import ProtocolLoader
from agent.mission.decision_engine import DecisionEngine
from agent.mission.deviation_detector import DeviationDetector
from agent.mission.live_perception_session import LivePerceptionSession
from agent.mission.perception_bridge import PerceptionProtocolBridge
from agent.mission.perception_decision import PerceptionDecisionAdapter
from agent.mission.sequence_validator import SequenceValidator
from agent.mission.state_machine import ProtocolStateMachine
from agent.mission.step_manager import StepManager
from agent.perception.perception_event import PerceptionEvent


PROTOCOL_PATH = "experiments/EXP001_TARDIGRADE"


def build_session() -> LivePerceptionSession:
    """Build the real ASTRA-GUARD mission stack."""

    protocol = ProtocolLoader(PROTOCOL_PATH).load()

    steps = protocol.get_steps()
    activities = protocol.get_activities()
    objects = protocol.get_objects()
    rules = protocol.get_rules()

    state_machine = ProtocolStateMachine(steps)

    step_manager = StepManager(
        steps,
        state_machine,
        rules,
    )

    validator = SequenceValidator(
        steps,
        activities,
    )

    deviation_detector = DeviationDetector(
        steps,
        activities,
    )

    decision_engine = DecisionEngine(
        state_machine,
        step_manager,
        validator,
        deviation_detector,
        rules=rules,
    )

    bridge = PerceptionProtocolBridge(
        protocol_objects=objects
    )

    adapter = PerceptionDecisionAdapter(
        decision_engine,
        bridge=bridge,
        protocol_aware=True,
    )

    return LivePerceptionSession(adapter)


def create_event(
    object_name: str,
    confidence: float = 0.95,
    hand_interaction: bool = True,
) -> PerceptionEvent:
    """Create a controlled perception event."""

    objects = [
        {
            "class_name": object_name,
            "confidence": confidence,
            "bbox": [300, 200, 500, 400],
        }
    ]

    hands = []

    if hand_interaction:
        hands = [
            {
                "confidence": 0.98,
                "center": [400, 300],
            }
        ]

    return PerceptionEvent(
        timestamp="controlled-demo",
        source="camera",
        objects=objects,
        hands=hands,
    )


def print_result(
    label: str,
    result: dict,
) -> None:
    """Print one controlled mission decision."""

    print()
    print("-" * 70)
    print(label)
    print("-" * 70)

    print(f"Step:              {result.get('step_id')}")
    print(f"Expected Activity: {result.get('expected_activity')}")
    print(f"Detected Activity: {result.get('detected_activity')}")
    print(f"Expected Object:   {result.get('expected_object')}")
    print(f"Detected Object:   {result.get('detected_object')}")

    perception = result.get("perception") or {}

    print(
        f"Confidence:        "
        f"{perception.get('confidence', 0.0):.2f}"
    )

    print(f"Status:             {result.get('status')}")
    print(
        f"Deviation:          "
        f"{result.get('deviation_type')}"
    )
    print(
        f"Guidance:           "
        f"{result.get('guidance')}"
    )


def run_demo() -> None:
    """Run the complete controlled mission."""

    print()
    print("=" * 70)
    print("                    ASTRA-GUARD")
    print("               CONTROLLED MISSION DEMO")
    print("=" * 70)

    session = build_session()

    print()
    print("Protocol: EXP001 - Tardigrade Sample Observation")
    print("Environment: Microgravity")
    print("Protocol Type: Synthetic")
    print("Mode: Controlled Demonstration")
    print()

    # =========================================================
    # S001 — CORRECT
    # =========================================================

    result = session.process_event(
        create_event(
            "experiment_container",
            confidence=0.98,
        )
    )

    print_result(
        "[1] CORRECT — Equipment Check",
        result,
    )

    # =========================================================
    # S002 — CORRECT
    # =========================================================

    result = session.process_event(
        create_event(
            "biological_sample",
            confidence=0.98,
        )
    )

    print_result(
        "[2] CORRECT — Retrieve Sample",
        result,
    )

    # =========================================================
    # S003 — DEVIATION
    # Wrong object detected
    # =========================================================

    result = session.process_event(
        create_event(
            "experiment_controller",
            confidence=0.98,
        )
    )

    print_result(
        "[3] DEVIATION — Wrong Object",
        result,
    )

    # =========================================================
    # S003 — UNCERTAIN
    # Correct object detected with low effective confidence
    #
    # Object confidence = 0.45
    # No hand interaction
    # Effective confidence = 0.45 * 0.80 = 0.36
    # =========================================================

    result = session.process_event(
        create_event(
            "sample_chamber",
            confidence=0.45,
            hand_interaction=False,
        )
    )

    print_result(
        "[4] UNCERTAIN — Low Confidence",
        result,
    )

    # =========================================================
    # S003 — CORRECT RECOVERY
    # =========================================================

    result = session.process_event(
        create_event(
            "sample_chamber",
            confidence=0.98,
        )
    )

    print_result(
        "[5] CORRECT — Recovery",
        result,
    )

    # =========================================================
    # S004 — CORRECT
    # =========================================================

    result = session.process_event(
        create_event(
            "sample_chamber",
            confidence=0.98,
        )
    )

    print_result(
        "[6] CORRECT — Transfer Sample",
        result,
    )

    # =========================================================
    # S005 — CORRECT
    # =========================================================

    result = session.process_event(
        create_event(
            "experiment_controller",
            confidence=0.98,
        )
    )

    print_result(
        "[7] CORRECT — Start Experiment",
        result,
    )

    # =========================================================
    # S006 — CORRECT
    # =========================================================

    result = session.process_event(
        create_event(
            "observation_interface",
            confidence=0.98,
        )
    )

    print_result(
        "[8] CORRECT — Record Result",
        result,
    )

    # =========================================================
    # S007 — CORRECT
    # =========================================================

    result = session.process_event(
        create_event(
            "sample_chamber",
            confidence=0.98,
        )
    )

    print_result(
        "[9] CORRECT — Secure Sample",
        result,
    )

    # =========================================================
    # S008 — COMPLETE
    # =========================================================

    result = session.process_event(
        create_event(
            "experiment_controller",
            confidence=0.98,
        )
    )

    print_result(
        "[10] COMPLETED — Complete Experiment",
        result,
    )

    # =========================================================
    # SUMMARY
    # =========================================================

    events = session.get_event_history()

    correct = sum(
        event.status == "CORRECT"
        for event in events
    )

    deviations = sum(
        event.status == "DEVIATION"
        for event in events
    )

    uncertain = sum(
        event.status == "UNCERTAIN"
        for event in events
    )

    completed = sum(
        event.status == "COMPLETED"
        for event in events
    )

    mission_completed = (
        session.adapter.engine.sm.is_complete()
    )

    print()
    print()
    print("=" * 70)
    print("                    MISSION SUMMARY")
    print("=" * 70)
    print()

    print(f"Total Events:       {len(events)}")
    print(f"Correct:            {correct}")
    print(f"Deviations:         {deviations}")
    print(f"Uncertain:          {uncertain}")
    print(f"Completed Events:   {completed}")

    print()

    if mission_completed:
        print("Mission Status:     COMPLETED")
        print("Protocol Progress:  8/8 steps")
    else:
        print("Mission Status:     INCOMPLETE")

    print()
    print("=" * 70)
    print("              ASTRA-GUARD DEMO FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()

