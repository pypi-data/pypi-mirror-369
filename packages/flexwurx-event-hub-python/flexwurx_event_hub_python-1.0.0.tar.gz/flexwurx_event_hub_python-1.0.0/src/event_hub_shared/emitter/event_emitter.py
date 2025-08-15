"""Event emission to Azure Event Hubs."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import logging

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from azure.identity.aio import DefaultAzureCredential

from ..utils.correlation import generate_correlation_id
from ..utils.partitioning import get_partition_key

logger = logging.getLogger(__name__)


class EventEmitter:
    """Centralized event publishing with automatic partitioning."""
    
    def __init__(self, namespace: str):
        """Initialize event emitter.
        
        Args:
            namespace: Event Hub namespace (e.g., 'namespace.servicebus.windows.net')
        """
        self._namespace = namespace
        self._credential = DefaultAzureCredential()
        self._producers: Dict[str, EventHubProducerClient] = {}
    
    async def emit(
        self, 
        hub_name: str, 
        event_type: str, 
        data: Any, 
        partition_key: Optional[str] = None
    ) -> None:
        """Emit an event to the specified Event Hub.
        
        Args:
            hub_name: Name of the Event Hub
            event_type: Type of event to emit
            data: Event data
            partition_key: Optional partition key override
        """
        producer = await self._get_producer(hub_name)
        
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "correlation_id": generate_correlation_id(),
            **data
        }
        
        event = EventData(event_data)
        if partition_key or get_partition_key(event_type, data):
            event.partition_key = partition_key or get_partition_key(event_type, data)
        
        async with producer:
            event_data_batch = await producer.create_batch()
            event_data_batch.add(event)
            await producer.send_batch(event_data_batch)
        
        logger.info(f"Emitted event: {event_type} to {hub_name}")
    
    async def emit_batch(
        self,
        hub_name: str,
        events: List[Dict[str, Any]],
        default_partition_key: Optional[str] = None
    ) -> None:
        """Emit a batch of events to the specified Event Hub.
        
        Args:
            hub_name: Name of the Event Hub
            events: List of events with event_type and data
            default_partition_key: Optional default partition key
        """
        producer = await self._get_producer(hub_name)
        
        async with producer:
            event_data_batch = await producer.create_batch()
            
            for event_info in events:
                event_data = {
                    "event_type": event_info["event_type"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "correlation_id": generate_correlation_id(),
                    **event_info["data"]
                }
                
                event = EventData(event_data)
                partition_key = (
                    event_info.get("partition_key") or 
                    default_partition_key or 
                    get_partition_key(event_info["event_type"], event_info["data"])
                )
                if partition_key:
                    event.partition_key = partition_key
                
                try:
                    event_data_batch.add(event)
                except ValueError as e:
                    logger.error(f"Event too large for batch: {event_info['event_type']}: {e}")
                    raise
            
            if len(event_data_batch) == 0:
                raise ValueError("No events added to batch")
            
            await producer.send_batch(event_data_batch)
        
        logger.info(f"Emitted batch of {len(events)} events to {hub_name}")
    
    async def _get_producer(self, hub_name: str) -> EventHubProducerClient:
        """Get or create producer for Event Hub."""
        if hub_name not in self._producers:
            self._producers[hub_name] = EventHubProducerClient(
                fully_qualified_namespace=self._namespace,
                eventhub_name=hub_name,
                credential=self._credential
            )
        return self._producers[hub_name]
    
    async def close(self) -> None:
        """Close all producers."""
        for producer in self._producers.values():
            await producer.close()
        self._producers.clear()