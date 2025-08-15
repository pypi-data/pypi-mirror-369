"""Service Bus scheduler for delayed task execution."""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
import logging

from azure.servicebus.aio import ServiceBusClient, ServiceBusSender, ServiceBusReceiver
from azure.servicebus import ServiceBusMessage
from azure.identity.aio import DefaultAzureCredential
from pydantic import BaseModel

from ..emitter.event_emitter import EventEmitter

logger = logging.getLogger(__name__)


class ScheduledTask(BaseModel):
    """Scheduled task definition."""
    
    event_type: str
    data: Dict[str, Any]
    execute_at: datetime
    hub_name: Optional[str] = "threats"
    partition_key: Optional[str] = None


class ServiceBusScheduler:
    """Schedule tasks for future execution using Service Bus."""
    
    def __init__(
        self,
        namespace: str,
        event_emitter: EventEmitter,
        queue_name: str = "scheduled-tasks"
    ):
        """Initialize scheduler.
        
        Args:
            namespace: Service Bus namespace
            event_emitter: Event emitter for publishing scheduled tasks
            queue_name: Service Bus queue name
        """
        self._namespace = namespace
        self._event_emitter = event_emitter
        self._queue_name = queue_name
        self._credential = DefaultAzureCredential()
        self._client = ServiceBusClient(
            fully_qualified_namespace=f"{namespace}.servicebus.windows.net",
            credential=self._credential
        )
        self._senders: Dict[str, ServiceBusSender] = {}
        self._receivers: Dict[str, ServiceBusReceiver] = {}
    
    async def schedule_task(
        self, 
        task: ScheduledTask, 
        correlation_id: Optional[str] = None
    ) -> str:
        """Schedule a task to be executed at a specific time.
        
        Args:
            task: Task to schedule
            correlation_id: Optional correlation ID for cancellation
            
        Returns:
            Correlation ID for cancellation
        """
        sender = await self._get_sender(self._queue_name)
        message_correlation_id = correlation_id or f"{task.event_type}-{datetime.now().timestamp()}"
        
        message_body = {
            "event_type": task.event_type,
            "data": task.data,
            "hub_name": task.hub_name,
            "partition_key": task.partition_key,
            "scheduled_for": task.execute_at.isoformat()
        }
        
        message = ServiceBusMessage(
            body=message_body,
            correlation_id=message_correlation_id,
            scheduled_enqueue_time=task.execute_at
        )
        
        await sender.send_messages(message)
        logger.info(f"Scheduled task: {task.event_type} for {task.execute_at} (correlation: {message_correlation_id})")
        
        return message_correlation_id
    
    async def start_task_processor(self) -> None:
        """Start listening for scheduled tasks."""
        receiver = await self._get_receiver(self._queue_name)
        logger.info("🚀 Starting scheduled task processor...")
        
        async with receiver:
            async for message in receiver:
                try:
                    body = message.body
                    event_type = body["event_type"]
                    data = body["data"]
                    hub_name = body["hub_name"]
                    partition_key = body.get("partition_key")
                    
                    logger.info(f"⏰ Executing scheduled task: {event_type}")
                    
                    # Emit to Event Hub for processing
                    await self._event_emitter.emit(hub_name, event_type, data, partition_key)
                    
                    # Complete the message
                    await receiver.complete_message(message)
                    logger.info(f"✅ Completed scheduled task: {event_type}")
                    
                except Exception as error:
                    logger.error(f"❌ Error processing scheduled task: {error}")
                    
                    # Dead letter the message after retries
                    await receiver.dead_letter_message(
                        message,
                        reason="ProcessingError",
                        error_description=str(error)
                    )
    
    async def cancel_scheduled_task(self, correlation_id: str) -> None:
        """Cancel scheduled tasks by correlation ID.
        
        Args:
            correlation_id: Correlation ID to cancel
        """
        receiver = await self._get_receiver(self._queue_name)
        
        try:
            # Peek messages to find matching correlation ID
            messages = await receiver.peek_messages(max_message_count=100)
            
            for message in messages:
                if message.correlation_id == correlation_id:
                    # Create a new receiver to receive and cancel the specific message
                    specific_receiver = self._client.get_queue_receiver(
                        queue_name=self._queue_name,
                        receive_mode="PeekLock"
                    )
                    
                    async with specific_receiver:
                        received_messages = await specific_receiver.receive_messages(
                            max_message_count=1,
                            max_wait_time=1
                        )
                        
                        for received_message in received_messages:
                            if received_message.sequence_number == message.sequence_number:
                                await specific_receiver.dead_letter_message(
                                    received_message,
                                    reason="Cancelled",
                                    error_description=f"Task with correlation ID {correlation_id} was cancelled"
                                )
                                logger.info(f"✅ Cancelled scheduled task: {correlation_id}")
                                return
            
        except Exception as error:
            logger.error(f"❌ Error cancelling scheduled task {correlation_id}: {error}")
            raise
    
    async def _get_sender(self, queue_name: str) -> ServiceBusSender:
        """Get or create sender for Service Bus queue."""
        if queue_name not in self._senders:
            self._senders[queue_name] = self._client.get_queue_sender(queue_name)
        return self._senders[queue_name]
    
    async def _get_receiver(self, queue_name: str) -> ServiceBusReceiver:
        """Get or create receiver for Service Bus queue."""
        if queue_name not in self._receivers:
            self._receivers[queue_name] = self._client.get_queue_receiver(queue_name)
        return self._receivers[queue_name]
    
    async def close(self) -> None:
        """Close all Service Bus connections."""
        for sender in self._senders.values():
            await sender.close()
        for receiver in self._receivers.values():
            await receiver.close()
        await self._client.close()
        self._senders.clear()
        self._receivers.clear()