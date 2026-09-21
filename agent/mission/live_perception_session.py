"""Phase 7.4 live perception session.

Connects the live perception pipeline to the Phase 7.3
perception-to-decision adapter.

This module does not open the webcam itself.
It accepts PerceptionEvent objects produced by the
existing perception layer.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agent.mission.perception_decision import PerceptionDecisionAdapter
from agent.perception.perception_event import PerceptionEvent


class LivePerceptionSession:
    """Process live perception events through the mission engine."""

    def __init__(
        self,
        adapter: PerceptionDecisionAdapter,
    ) -> None:
        if not isinstance(adapter, PerceptionDecisionAdapter):
            raise TypeError(
                "adapter must be a PerceptionDecisionAdapter"
            )

        self.adapter = adapter
        self.event_count = 0
        self.last_result: Optional[Dict[str, Any]] = None

    def process_event(
        self,
        event: PerceptionEvent,
    ) -> Dict[str, Any]:
        """Process one live perception event."""

        if not isinstance(event, PerceptionEvent):
            raise TypeError(
                "event must be a PerceptionEvent"
            )

        self.event_count += 1

        result = self.adapter.decide(event)

        self.last_result = result

        return result

    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """Return the most recent decision result."""

        return self.last_result

    def reset(self) -> None:
        """Reset session-level event tracking."""

        self.event_count = 0
        self.last_result = None