"""Event registry for routing events to handlers."""

import re
from typing import Dict, List, Tuple, Any
import logging

from ..types.handlers import EventHandler

logger = logging.getLogger(__name__)


class EventRegistry:
    """Routes events to appropriate handlers based on type matching."""
    
    def __init__(self):
        self._handlers: Dict[str, EventHandler] = {}
        self._patterns: List[Tuple[re.Pattern[str], EventHandler]] = []
    
    def register(self, event_type: str, handler: EventHandler) -> None:
        """Register handler for exact event type match.
        
        Args:
            event_type: Exact event type string
            handler: Handler to process the event
        """
        self._handlers[event_type] = handler
    
    def register_pattern(self, pattern: re.Pattern[str], handler: EventHandler) -> None:
        """Register handler for event type pattern.
        
        Args:
            pattern: Regex pattern to match event types
            handler: Handler to process matching events
        """
        self._patterns.append((pattern, handler))
    
    async def route(self, event: Any, context: Any) -> None:
        """Route event to appropriate handler.
        
        Args:
            event: Event data from Event Hub
            context: Partition context
        """
        event_type = event.body.get("eventType")
        if not event_type:
            logger.warning("Event missing event_type field")
            return
        
        # Try exact match first
        exact_handler = self._handlers.get(event_type)
        if exact_handler:
            await exact_handler.handle(event, context)
            return
        
        # Try pattern matching
        for pattern, handler in self._patterns:
            if pattern.match(event_type):
                await handler.handle(event, context)
                return
        
        logger.warning(f"No handler found for event type: {event_type}")