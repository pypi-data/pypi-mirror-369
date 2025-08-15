"""Idempotency utilities for event processing."""

from datetime import datetime, timezone, timedelta
from typing import Any, List


def is_event_too_old(event: Any, max_age_minutes: int = 10) -> bool:
    """Check if an event is too old to process (prevents reprocessing old events on restart).
    
    Args:
        event: Event to check
        max_age_minutes: Maximum age in minutes (default: 10)
        
    Returns:
        True if event should be skipped
    """
    if not hasattr(event, 'enqueued_time_utc'):
        return False
    
    event_time = event.enqueued_time_utc
    if isinstance(event_time, str):
        event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
    return event_time < cutoff_time


def is_event_data_too_old(event_data: Any, max_age_minutes: int = 5) -> bool:
    """Check if event data has a recent timestamp.
    
    Args:
        event_data: Event body data
        max_age_minutes: Maximum age in minutes (default: 5)
        
    Returns:
        True if data timestamp is too old
    """
    timestamp = None
    
    if isinstance(event_data, dict):
        timestamp = event_data.get('timestamp')
    elif hasattr(event_data, 'timestamp'):
        timestamp = event_data.timestamp
    
    if not timestamp:
        return False  # No timestamp, assume it's current
    
    if isinstance(timestamp, str):
        data_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    else:
        data_time = timestamp
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
    return data_time < cutoff_time


def filter_recent_events(events: List[Any], max_age_minutes: int = 10) -> List[Any]:
    """Filter out events that are too old to process.
    
    Args:
        events: Array of events
        max_age_minutes: Maximum age in minutes
        
    Returns:
        Filtered events
    """
    return [event for event in events if not is_event_too_old(event, max_age_minutes)]