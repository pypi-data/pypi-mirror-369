"""Base handler for event processing."""

from abc import ABC, abstractmethod
from typing import Any
import logging

from ..emitter.event_emitter import EventEmitter
from ..utils.correlation import generate_correlation_id

logger = logging.getLogger(__name__)


class BaseHandler(ABC):
    """Abstract base class for all event handlers."""
    
    def __init__(self, event_emitter: EventEmitter):
        """Initialize base handler.
        
        Args:
            event_emitter: Event emitter for publishing events
        """
        self._event_emitter = event_emitter
    
    @abstractmethod
    async def handle(self, event: Any, context: Any) -> None:
        """Process an event - must be implemented by subclasses.
        
        Args:
            event: Event data from Event Hub
            context: Partition context
        """
        pass
    
    async def emit_event(
        self,
        hub_name: str,
        event_type: str,
        data: Any,
        partition_key: str = None
    ) -> None:
        """Emit a new event to the Event Hub.
        
        Args:
            hub_name: Name of the Event Hub to emit to
            event_type: Type of event to emit
            data: Event data
            partition_key: Optional partition key override
        """
        await self._event_emitter.emit(hub_name, event_type, data, partition_key)
    
    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for tracking."""
        return generate_correlation_id()
    
    def log_error(self, error: Exception, event: Any, context: str = None) -> None:
        """Log error with event context.
        
        Args:
            error: Error that occurred
            event: Event being processed
            context: Additional context
        """
        event_type = getattr(event, 'body', {}).get('event_type', 'unknown')
        sequence_number = getattr(event, 'sequence_number', 'unknown')
        
        logger.error(
            f"Handler error: {error}",
            extra={
                "event_type": event_type,
                "sequence_number": sequence_number,
                "context": context,
                "error": str(error)
            }
        )