"""
Mission event history for ASTRA-GUARD.

The EventStore keeps a chronological record of protocol decisions
during the current mission session.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MissionEvent:
    """A single event recorded during mission execution."""

    timestamp: str
    step_id: Optional[str]
    activity: Optional[str]
    detected_object: Optional[str]
    confidence: Optional[float]
    status: str
    deviation: Optional[str]
    guidance: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        """Return the event as a dictionary."""
        return asdict(self)


class EventStore:
    """In-memory chronological store for mission events."""

    def __init__(self) -> None:
        self._events: List[MissionEvent] = []

    def record(
        self,
        *,
        step_id: Optional[str],
        activity: Optional[str],
        detected_object: Optional[str],
        confidence: Optional[float],
        status: str,
        deviation: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> MissionEvent:
        """
        Record a mission event and return the created event.
        """

        event = MissionEvent(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            step_id=step_id,
            activity=activity,
            detected_object=detected_object,
            confidence=confidence,
            status=status,
            deviation=deviation,
            guidance=guidance,
        )

        self._events.append(event)
        return event

    def get_all(self) -> List[MissionEvent]:
        """Return all recorded events in chronological order."""
        return list(self._events)

    def get_latest(self) -> Optional[MissionEvent]:
        """Return the most recent event, if available."""
        if not self._events:
            return None

        return self._events[-1]

    def count(self) -> int:
        """Return the number of recorded events."""
        return len(self._events)

    def clear(self) -> None:
        """Clear all events from the current mission session."""
        self._events.clear()