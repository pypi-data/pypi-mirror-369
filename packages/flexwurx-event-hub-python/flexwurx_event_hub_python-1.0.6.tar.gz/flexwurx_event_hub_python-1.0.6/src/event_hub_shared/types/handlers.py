"""Handler interfaces and types."""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, Protocol
import re


class EventHandler(Protocol):
    """Protocol for event handlers."""
    
    async def handle(self, event: Any, context: Any) -> None:
        """Process a single event with its context."""
        ...


PartitionKeyExtractor = Callable[[str, Any], Optional[str]]
"""Function that determines which partition an event should go to."""


class EventFilter(ABC):
    """Interface for event filtering."""
    
    @property
    @abstractmethod
    def patterns(self) -> List[re.Pattern[str]]:
        """Regex patterns that this service cares about."""
        ...
    
    @abstractmethod
    def is_relevant(self, event_type: str) -> bool:
        """Check if this service should process the given event type."""
        ...