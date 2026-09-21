"""
Phase 7.4 Step 3 - Real webcam runtime.

Connects the real OpenCV webcam to the existing
LivePerceptionProcessor.

This module does not contain protocol logic.
It only handles webcam capture and frame processing.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import cv2

from agent.perception.live_processor import LivePerceptionProcessor


class WebcamRuntime:
    """Run ASTRA-GUARD perception on a live webcam."""

    def __init__(
        self,
        processor: LivePerceptionProcessor,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
    ) -> None:

        if not hasattr(processor, "process_frame"):
            raise TypeError(
                "processor must provide a process_frame(frame) method"
            )

        self.processor = processor
        self.camera_index = int(camera_index)
        self.width = int(width)
        self.height = int(height)

        self.capture: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        """Open the webcam."""

        self.capture = cv2.VideoCapture(
            self.camera_index
        )

        if not self.capture.isOpened():
            self.capture.release()
            self.capture = None

            raise RuntimeError(
                f"Unable to open webcam index {self.camera_index}"
            )

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.width,
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.height,
        )

    def read_frame(self):
        """Read one frame from the webcam."""

        if self.capture is None:
            raise RuntimeError(
                "Webcam is not open. Call open() first."
            )

        success, frame = self.capture.read()

        if not success or frame is None:
            raise RuntimeError(
                "Unable to read frame from webcam"
            )

        return frame

    def process_once(self) -> Dict[str, Any]:
        """Capture and process exactly one webcam frame."""

        frame = self.read_frame()

        return self.processor.process_frame(
            frame
        )

    def release(self) -> None:
        """Release the webcam."""

        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def run(self) -> None:
        """Run the live webcam loop.

        Press Q to stop the runtime.
        """

        self.open()

        try:
            while True:

                result = self.process_once()

                frame = result.get(
                    "frame"
                )

                if frame is not None:
                    cv2.imshow(
                        "ASTRA-GUARD",
                        frame,
                    )

                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break

        finally:
            self.release()
            cv2.destroyAllWindows()