"""Partition key utilities."""

import re
from typing import Any, Dict, Optional
from ..types.handlers import PartitionKeyExtractor

# Map of domain patterns to their partition key extraction logic
_PARTITIONING_MAP: Dict[re.Pattern[str], PartitionKeyExtractor] = {
    re.compile(r'^task\..*'): lambda event_type, data: None,  # Task events - distribute evenly
}


def get_partition_key(event_type: str, data: Any) -> Optional[str]:
    """Determine which partition an event should be routed to based on event type and data.
    
    Args:
        event_type: Event type string (e.g., 'task.create.notification')
        data: Event data object
        
    Returns:
        Partition key string or None for round-robin distribution
    """
    for pattern, extractor in _PARTITIONING_MAP.items():
        if pattern.match(event_type):
            return extractor(event_type, data)
    
    # Default: distribute evenly across partitions
    return None


def add_partitioning_rule(pattern: re.Pattern[str], extractor: PartitionKeyExtractor) -> None:
    """Add a new partitioning rule for a specific event pattern.
    
    Args:
        pattern: Regex pattern to match event types
        extractor: Function to extract partition key from event data
    """
    _PARTITIONING_MAP[pattern] = extractor
