"""Phase 7.4 live perception session.

Connects the live perception pipeline to the Phase 7.3
perception-to-decision adapter.

The session records mission decisions using EventStore
and keeps a rolling window using ShortTermMemory.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.memory.event_store import EventStore, MissionEvent
from agent.memory.short_term_memory import ShortTermMemory
from agent.mission.perception_decision import PerceptionDecisionAdapter
from agent.perception.perception_event import PerceptionEvent


class LivePerceptionSession:
    """Process live perception events through the mission engine."""

    def __init__(
        self,
        adapter: PerceptionDecisionAdapter,
        event_store: EventStore | None = None,
        short_term_memory: ShortTermMemory | None = None,
    ) -> None:
        if not isinstance(adapter, PerceptionDecisionAdapter):
            raise TypeError(
                "adapter must be a PerceptionDecisionAdapter"
            )

        if event_store is not None and not isinstance(
            event_store,
            EventStore,
        ):
            raise TypeError(
                "event_store must be an EventStore"
            )

        if short_term_memory is not None and not isinstance(
            short_term_memory,
            ShortTermMemory,
        ):
            raise TypeError(
                "short_term_memory must be a ShortTermMemory"
            )

        self.adapter = adapter
        self.event_store = event_store or EventStore()
        self.short_term_memory = (
            short_term_memory or ShortTermMemory()
        )

        self.event_count = 0
        self.last_result: Optional[Dict[str, Any]] = None

    def process_event(
        self,
        event: PerceptionEvent,
    ) -> Dict[str, Any]:
        """Process one live perception event and record its decision."""

        if not isinstance(event, PerceptionEvent):
            raise TypeError(
                "event must be a PerceptionEvent"
            )

        self.event_count += 1

        result = self.adapter.decide(event)

        self.last_result = result

        mission_event = self._record_decision(result)

        self.short_term_memory.add(mission_event)

        return result

    def _record_decision(
        self,
        result: Dict[str, Any],
    ) -> MissionEvent:
        """Record a decision result in the mission event store."""

        perception = result.get("perception") or {}

        return self.event_store.record(
            step_id=result.get("step_id"),
            activity=(
                result.get("detected_activity")
                or perception.get("activity")
            ),
            detected_object=(
                result.get("detected_object")
                or perception.get("object")
            ),
            confidence=perception.get("confidence"),
            status=str(
                result.get("status", "UNKNOWN")
            ),
            deviation=result.get("deviation_type"),
            guidance=result.get("guidance"),
        )

    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """Return the most recent decision result."""

        return self.last_result

    def get_event_history(self) -> List[MissionEvent]:
        """Return all recorded mission events."""

        return self.event_store.get_all()

    def get_latest_event(self) -> Optional[MissionEvent]:
        """Return the most recently recorded mission event."""

        return self.event_store.get_latest()

    def get_recent_events(self) -> List[MissionEvent]:
        """Return events currently held in short-term memory."""

        return self.short_term_memory.get_recent()

    def get_latest_recent_event(
        self,
    ) -> Optional[MissionEvent]:
        """Return the latest event from short-term memory."""

        return self.short_term_memory.get_latest()

    def reset(self) -> None:
        """Reset session state and both memory layers."""

        self.event_count = 0
        self.last_result = None
        self.event_store.clear()
        self.short_term_memory.clear()