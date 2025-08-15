"""Dead letter queue handler for failed events."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import logging

from azure.servicebus.aio import ServiceBusClient, ServiceBusSender
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DeadLetterEvent(BaseModel):
    """Dead letter event structure."""
    
    original_event: Dict[str, Any]
    error: str
    error_stack: Optional[str] = None
    attempt_count: int
    failed_at: datetime
    partition_id: Optional[str] = None
    sequence_number: Optional[int] = None


class DeadLetterHandler:
    """Handle failed Event Hub events by sending to Service Bus dead letter queue."""
    
    def __init__(
        self,
        namespace: str,
        queue_name: str = "event-hub-dead-letters"
    ):
        """Initialize dead letter handler.
        
        Args:
            namespace: Service Bus namespace
            queue_name: Dead letter queue name
        """
        self._namespace = namespace
        self._queue_name = queue_name
        self._credential = DefaultAzureCredential()
        self._client = ServiceBusClient(
            fully_qualified_namespace=f"{namespace}.servicebus.windows.net",
            credential=self._credential
        )
        self._sender: Optional[ServiceBusSender] = None
    
    async def send_to_dead_letter(
        self,
        event: Any,
        error: Exception,
        attempt_count: int = 1
    ) -> None:
        """Send failed Event Hub event to dead letter queue.
        
        Args:
            event: Original Event Hub event that failed
            error: Error that occurred
            attempt_count: Number of processing attempts
        """
        dead_letter_event = DeadLetterEvent(
            original_event=event.body if hasattr(event, 'body') else event,
            error=str(error),
            error_stack=getattr(error, '__traceback__', None),
            attempt_count=attempt_count,
            failed_at=datetime.now(timezone.utc),
            partition_id=getattr(event, 'partition_key', None),
            sequence_number=getattr(event, 'sequence_number', None)
        )
        
        message = ServiceBusMessage(
            body=dead_letter_event.model_dump(),
            message_id=f"failed-{dead_letter_event.sequence_number}-{datetime.now().timestamp()}",
            subject=f"Failed: {dead_letter_event.original_event.get('event_type', 'unknown')}",
            application_properties={
                "original_event_type": dead_letter_event.original_event.get('event_type', 'unknown'),
                "error_type": type(error).__name__,
                "failure_reason": str(error)
            }
        )
        
        try:
            sender = await self._get_sender()
            await sender.send_messages(message)
            logger.info(f"📨 Sent to dead letter: {dead_letter_event.original_event.get('event_type')} (sequence: {dead_letter_event.sequence_number})")
        except Exception as dlq_error:
            logger.error(f"❌ Failed to send to dead letter queue: {dlq_error}")
    
    async def _get_sender(self) -> ServiceBusSender:
        """Get or create sender for dead letter queue."""
        if self._sender is None:
            self._sender = self._client.get_queue_sender(self._queue_name)
        return self._sender
    
    async def close(self) -> None:
        """Close dead letter handler."""
        if self._sender:
            await self._sender.close()
        await self._client.close()