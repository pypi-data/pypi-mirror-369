"""Event filtering utilities."""

import re
from typing import List, Any
from ..types.handlers import EventFilter


class EventFilterUtil(EventFilter):
    """Filter events by service-specific patterns."""
    
    def __init__(self, patterns: List[re.Pattern[str]]):
        """Initialize event filter.
        
        Args:
            patterns: List of regex patterns to match
        """
        self._patterns = patterns
    
    @property
    def patterns(self) -> List[re.Pattern[str]]:
        """Regex patterns that this service cares about."""
        return self._patterns
    
    def is_relevant(self, event_type: str) -> bool:
        """Check if this service should process the given event type.
        
        Args:
            event_type: Event type to check
            
        Returns:
            True if event matches any pattern
        """
        return any(pattern.match(event_type) for pattern in self._patterns)
    
    def add_pattern(self, pattern: re.Pattern[str]) -> None:
        """Add a new pattern to filter for.
        
        Args:
            pattern: Regex pattern to add
        """
        self._patterns.append(pattern)
    
    def filter_events(self, events: List[Any]) -> List[Any]:
        """Filter array of events to only relevant ones.
        
        Args:
            events: Events to filter
            
        Returns:
            Only events that match patterns
        """
        return [
            event for event in events
            if self.is_relevant(event.body.get("event_type", ""))
        ]