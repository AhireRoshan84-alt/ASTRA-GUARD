"""
Phase 11 - Mission-aware live decision overlay.

Displays ASTRA-GUARD perception, protocol expectations,
decision status, guidance, and mission progress on
the webcam frame.

This module only visualizes existing results.
It does not perform detection or make decisions.
"""

from __future__ import annotations

from typing import Any, Dict

import cv2
import numpy as np


class LiveOverlay:
    """Draw ASTRA-GUARD information on a video frame."""

    @staticmethod
    def _safe_text(
        value: Any,
        default: str = "UNKNOWN",
    ) -> str:
        """Convert a value to display-safe text."""

        if value is None:
            return default

        text = str(value).strip()

        if not text:
            return default

        return text

    @staticmethod
    def _safe_confidence(
        value: Any,
    ) -> float:
        """Convert confidence to a value between 0 and 1."""

        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.0

        return max(
            0.0,
            min(1.0, confidence),
        )

    @staticmethod
    def _safe_progress(
        progress: Any,
    ) -> float:
        """Convert mission progress to a value between 0 and 100."""

        try:
            value = float(progress)
        except (TypeError, ValueError):
            return 0.0

        return max(
            0.0,
            min(100.0, value),
        )

    def draw(
        self,
        frame: np.ndarray,
        result: Dict[str, Any],
        mission_status: Dict[str, Any] | None = None,
    ) -> np.ndarray:
        """
        Draw protocol decision and mission status information.

        Parameters
        ----------
        frame:
            OpenCV BGR video frame.

        result:
            Current protocol decision result.

        mission_status:
            Dashboard-ready mission status returned by MissionStatus.
        """

        if frame is None:
            raise ValueError(
                "frame cannot be None"
            )

        if (
            not isinstance(frame, np.ndarray)
            or frame.ndim != 3
            or frame.shape[2] != 3
        ):
            raise ValueError(
                "frame must be an OpenCV BGR image"
            )

        if not isinstance(result, dict):
            raise TypeError(
                "result must be a dictionary"
            )

        if mission_status is not None and not isinstance(
            mission_status,
            dict,
        ):
            raise TypeError(
                "mission_status must be a dictionary or None"
            )

        annotated = frame.copy()

        # ---------------------------------------------------------
        # Perception
        # ---------------------------------------------------------

        perception = result.get(
            "perception",
            {},
        )

        if not isinstance(
            perception,
            dict,
        ):
            perception = {}

        activity = self._safe_text(
            perception.get("activity"),
        )

        detected_object = self._safe_text(
            perception.get("object"),
        )

        confidence = self._safe_confidence(
            perception.get("confidence", 0.0)
        )

        # ---------------------------------------------------------
        # Protocol decision
        # ---------------------------------------------------------

        decision_status = self._safe_text(
            result.get("status"),
        )

        step_id = self._safe_text(
            result.get("step_id"),
        )

        expected_activity = self._safe_text(
            result.get("expected_activity"),
        )

        expected_object = self._safe_text(
            result.get("expected_object"),
        )

        deviation_type = self._safe_text(
            result.get(
                "deviation_type"
            ),
            default="NONE",
        )

        guidance = self._safe_text(
            result.get("guidance"),
            default="No guidance",
        )

        # ---------------------------------------------------------
        # Mission status
        # ---------------------------------------------------------

        if mission_status is None:
            mission_status = {}

        progress_data = mission_status.get(
            "progress",
            {},
        )

        if not isinstance(
            progress_data,
            dict,
        ):
            progress_data = {}

        completed_steps = progress_data.get(
            "completed_steps",
            0,
        )

        total_steps = progress_data.get(
            "total_steps",
            0,
        )

        progress_percent = self._safe_progress(
            progress_data.get(
                "progress_percent",
                0.0,
            )
        )

        mission_completed = bool(
            progress_data.get(
                "completed",
                False,
            )
        )

        # ---------------------------------------------------------
        # Main information panel
        # ---------------------------------------------------------

        lines = [
            "ASTRA-GUARD",
            f"Step: {step_id}",
            f"Activity: {activity}",
            f"Object: {detected_object}",
            f"Confidence: {confidence:.2f}",
            f"Expected Activity: {expected_activity}",
            f"Expected Object: {expected_object}",
            f"Status: {decision_status}",
            f"Deviation: {deviation_type}",
            f"Guidance: {guidance}",
            (
                f"Mission Progress: "
                f"{completed_steps}/{total_steps} "
                f"({progress_percent:.1f}%)"
            ),
            (
                "Mission: COMPLETED"
                if mission_completed
                else "Mission: ACTIVE"
            ),
            "Press Q to quit",
        ]

        x = 20
        y = 35
        line_height = 27

        # ---------------------------------------------------------
        # Background panel
        # ---------------------------------------------------------

        panel_width = 700
        panel_height = 25 + (
            len(lines) * line_height
        )

        overlay = annotated.copy()

        cv2.rectangle(
            overlay,
            (10, 10),
            (
                10 + panel_width,
                10 + panel_height,
            ),
            (0, 0, 0),
            -1,
        )

        annotated = cv2.addWeighted(
            overlay,
            0.55,
            annotated,
            0.45,
            0,
        )

        # ---------------------------------------------------------
        # Text
        # ---------------------------------------------------------

        for index, line in enumerate(lines):

            cv2.putText(
                annotated,
                line,
                (
                    x,
                    y + index * line_height,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        return annotated