"""Event data type definitions."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class BaseEventData(BaseModel):
    """Base event data structure."""
    
    event_type: str = Field(description="Event type identifier for routing and filtering")
    timestamp: datetime = Field(description="When the event was created")
    correlation_id: Optional[str] = Field(default=None, description="Unique ID for tracking requests across services")
    
    class Config:
        extra = "allow"  # Allow additional fields


class TaskEventData(BaseEventData):
    """Task-specific event data."""
    
    task_id: Optional[str] = Field(default=None, description="Unique identifier for the task")
    threat_id: Optional[str] = Field(default=None, description="ID of the threat that triggered this task")
    property_id: Optional[str] = Field(default=None, description="Property where the task applies")
    org_id: Optional[str] = Field(default=None, description="Organization that owns the task")
    status: Optional[str] = Field(default=None, description="Current status of the task")
    responsible_entity: Optional[str] = Field(default=None, description="Who is responsible for handling this task")
    responsible_entity_id: Optional[str] = Field(default=None, description="Specific ID of the entity responsible")
    reason: Optional[str] = Field(default=None, description="Explanation for why this action occurred")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional task-specific data and results")