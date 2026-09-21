import numpy as np
import pytest

from agent.perception.webcam_runtime import WebcamRuntime


class FakeProcessor:
    def __init__(self):
        self.received_frames = []

    def process_frame(self, frame):
        self.received_frames.append(frame)

        return {
            "event": "fake_event",
            "result": {
                "status": "CORRECT",
            },
        }


def test_runtime_requires_processor():
    with pytest.raises(TypeError):
        WebcamRuntime(object())


def test_runtime_initial_state():
    processor = FakeProcessor()

    runtime = WebcamRuntime(
        processor,
        camera_index=0,
        width=1280,
        height=720,
    )

    assert runtime.camera_index == 0
    assert runtime.width == 1280
    assert runtime.height == 720
    assert runtime.capture is None


def test_read_frame_requires_open_camera():
    processor = FakeProcessor()

    runtime = WebcamRuntime(processor)

    with pytest.raises(RuntimeError):
        runtime.read_frame()


def test_process_once_sends_frame_to_processor(monkeypatch):
    processor = FakeProcessor()

    runtime = WebcamRuntime(processor)

    fake_frame = np.zeros(
        (720, 1280, 3),
        dtype=np.uint8,
    )

    class FakeCapture:
        def read(self):
            return True, fake_frame

    runtime.capture = FakeCapture()

    result = runtime.process_once()

    assert result["result"]["status"] == "CORRECT"

    assert len(
        processor.received_frames
    ) == 1

    assert (
        processor.received_frames[0] is fake_frame
    )


def test_failed_camera_read_is_rejected():
    processor = FakeProcessor()

    runtime = WebcamRuntime(processor)

    class FakeCapture:
        def read(self):
            return False, None

    runtime.capture = FakeCapture()

    with pytest.raises(RuntimeError):
        runtime.read_frame()


def test_release_clears_capture():
    processor = FakeProcessor()

    runtime = WebcamRuntime(processor)

    class FakeCapture:
        def __init__(self):
            self.released = False

        def release(self):
            self.released = True

    capture = FakeCapture()

    runtime.capture = capture

    runtime.release()

    assert capture.released is True
    assert runtime.capture is None