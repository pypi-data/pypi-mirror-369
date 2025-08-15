"""FlexWurx Event Hub Shared Library for Python."""

from .types.events import BaseEventData, TaskEventData
from .types.handlers import EventHandler, PartitionKeyExtractor
from .registry.event_registry import EventRegistry
from .emitter.event_emitter import EventEmitter
from .consumer.event_consumer import EventConsumer
from .scheduler.service_bus_scheduler import ServiceBusScheduler, ScheduledTask
from .deadletter.dead_letter_handler import DeadLetterHandler, DeadLetterEvent
from .handlers.base_handler import BaseHandler
from .utils.filtering import EventFilterUtil
from .utils.correlation import generate_correlation_id, validate_correlation_id
from .utils.partitioning import get_partition_key, add_partitioning_rule
from .utils.idempotency import is_event_too_old, filter_recent_events

__version__ = "1.0.0"

__all__ = [
    # Types
    "BaseEventData",
    "TaskEventData", 
    "EventHandler",
    "PartitionKeyExtractor",
    "ScheduledTask",
    "DeadLetterEvent",
    
    # Core classes
    "EventRegistry",
    "EventEmitter", 
    "EventConsumer",
    "ServiceBusScheduler",
    "DeadLetterHandler",
    "BaseHandler",
    "EventFilterUtil",
    
    # Utilities
    "generate_correlation_id",
    "validate_correlation_id",
    "get_partition_key",
    "add_partitioning_rule", 
    "is_event_too_old",
    "filter_recent_events",
]