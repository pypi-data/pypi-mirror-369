"""Correlation ID utilities."""

import time
import random
import string
import re
from typing import Any


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for tracking requests across services.
    
    Returns:
        Unique correlation ID string
    """
    timestamp = int(time.time() * 1000)  # milliseconds
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
    return f"{timestamp}-{random_part}"


def validate_correlation_id(correlation_id: str) -> bool:
    """Validate correlation ID format.
    
    Args:
        correlation_id: ID to validate
        
    Returns:
        True if valid format
    """
    pattern = r'^\d{13}-[a-z0-9]{9}$'
    return bool(re.match(pattern, correlation_id))


def extract_correlation_id(event_data: Any) -> str:
    """Extract correlation ID from event data.
    
    Args:
        event_data: Event data object
        
    Returns:
        Correlation ID or None
    """
    if hasattr(event_data, 'correlation_id'):
        return event_data.correlation_id
    
    if hasattr(event_data, 'body') and isinstance(event_data.body, dict):
        return event_data.body.get('correlation_id')
    
    return None