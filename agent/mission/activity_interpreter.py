"""
ASTRA-GUARD activity interpreter.

Phase 7.5.2:
Converts perception observations into protocol activity IDs.

This is a deterministic prototype interpreter.
It does not use an LLM or train a new model.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class ActivityInterpreter:
    """Interpret perception signals using the current protocol step."""

    def __init__(self) -> None:
        self._activity_by_step = {
            "S001": "CHECK_EQUIPMENT",
            "S002": "RETRIEVE_SAMPLE",
            "S003": "OPEN_CONTAINER",
            "S004": "TRANSFER_SAMPLE",
            "S005": "START_EXPERIMENT",
            "S006": "RECORD_RESULT",
            "S007": "SECURE_SAMPLE",
            "S008": "COMPLETE_EXPERIMENT",
        }

    def interpret(
        self,
        step_id: str,
        detected_object: Optional[str],
        hand_interaction: bool = False,
        confidence: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Convert the current step and perception signals
        into a protocol activity.

        The current prototype uses the protocol state as the
        activity context and perception to confirm object/interaction.
        """

        activity = self._activity_by_step.get(step_id)

        if activity is None:
            return {
                "activity": "UNKNOWN",
                "confidence": 0.0,
                "reason": "unknown_step",
            }

        try:
            confidence = max(0.0, min(1.0, float(confidence)))
        except (TypeError, ValueError):
            confidence = 0.0

        if detected_object is None:
            return {
                "activity": "UNKNOWN",
                "confidence": 0.0,
                "reason": "no_object_detected",
            }

        if hand_interaction:
            activity_confidence = confidence
            reason = "object_hand_interaction"
        else:
            activity_confidence = confidence * 0.80
            reason = "object_detected_without_hand_interaction"

        return {
            "activity": activity,
            "confidence": activity_confidence,
            "reason": reason,
        }