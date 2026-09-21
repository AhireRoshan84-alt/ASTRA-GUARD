"""
Phase 7.4 single-frame live perception processor.

Connects the existing Phase 6 YOLO + MediaPipe perception
components to the Phase 7.4 live mission session.

This module processes one frame at a time.
It does not open or control the webcam.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

import numpy as np

from agent.mission.live_perception_session import LivePerceptionSession
from agent.perception.perception_event import PerceptionEvent


class LivePerceptionProcessor:
    """Convert one camera frame into a mission decision."""

    def __init__(
        self,
        object_detector: Any,
        hand_tracker: Any,
        session: LivePerceptionSession,
    ) -> None:
        if not hasattr(object_detector, "detect"):
            raise TypeError(
                "object_detector must provide a detect(frame) method"
            )

        if not hasattr(hand_tracker, "process"):
            raise TypeError(
                "hand_tracker must provide a process(frame) method"
            )

        if not hasattr(session, "process_event"):
            raise TypeError(
                "session must provide a process_event(event) method"
            )

        self.object_detector = object_detector
        self.hand_tracker = hand_tracker
        self.session = session

    def process_frame(
        self,
        frame: np.ndarray,
    ) -> Dict[str, Any]:
        """Process one OpenCV BGR frame."""

        if frame is None:
            raise ValueError(
                "process_frame received None frame"
            )

        if (
            not isinstance(frame, np.ndarray)
            or frame.ndim != 3
            or frame.shape[2] != 3
        ):
            raise ValueError(
                "process_frame expects an OpenCV BGR frame"
            )

        # Detect objects using YOLO.
        objects = self.object_detector.detect(frame)

        # Detect hands using MediaPipe.
        hands = self.hand_tracker.process(frame)

        # Convert MediaPipe normalized hand landmarks
        # into pixel-space hand centers.
        frame_height, frame_width = frame.shape[:2]

        for hand in hands:
            landmarks = hand.get("landmarks", [])

            if not landmarks:
                continue

            pixel_points = []

            for landmark in landmarks:
                try:
                    x = float(landmark["x"]) * frame_width
                    y = float(landmark["y"]) * frame_height
                    pixel_points.append((x, y))
                except (KeyError, TypeError, ValueError):
                    continue

            if pixel_points:
                hand["center"] = [
                    sum(point[0] for point in pixel_points)
                    / len(pixel_points),
                    sum(point[1] for point in pixel_points)
                    / len(pixel_points),
                ]

        # Create a perception event.
        event = PerceptionEvent(
            timestamp=datetime.now().isoformat(),
            source="camera",
            objects=objects,
            hands=hands,
        )

        # Send perception into the mission decision system.
        result = self.session.process_event(event)

        # Return the original frame as well as the
        # perception event and protocol decision.
        return {
            "frame": frame,
            "event": event,
            "result": result,
        }

    def close(self) -> None:
        """Release the hand tracker if it supports close()."""

        close_method = getattr(
            self.hand_tracker,
            "close",
            None,
        )

        if callable(close_method):
            close_method()