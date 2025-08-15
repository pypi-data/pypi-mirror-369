# FlexWurx Event Hub Python Library

A Python library for building event-driven microservices with Azure Event Hubs and Service Bus.

## Development Process

### Publishing New Features

1. **Make changes** to your code
2. **Test locally** - `uv run pytest` (if you have tests)
3. **Bump version** in pyproject.toml (1.0.0 → 1.0.1)
4. **Commit and push** to GitHub
5. **GitHub Actions** automatically builds and publishes
6. **Services update** with `uv add flexwurx-event-hub-python@latest`

### Manual Publishing

```bash
uv build
uv publish
```

## Installation

```bash
# Using UV (recommended)
uv add flexwurx-event-hub-python

# Upgrading
uv sync --upgrade-package flexwurx-event-hub-python

# Using pip
pip install flexwurx-event-hub-python
```

## Quick Start

```python
import asyncio
from event_hub_shared import (
    EventEmitter, EventConsumer, ServiceBusScheduler,
    EventRegistry, BaseHandler, EventFilterUtil
)

# Setup
emitter = EventEmitter('your-namespace.servicebus.windows.net')
consumer = EventConsumer(
    'your-namespace.servicebus.windows.net',
    'storageaccount',
    'checkpoints-container'
)
scheduler = ServiceBusScheduler('your-servicebus-namespace', emitter)
```

## AI Service Implementation Example

```python
import re
from event_hub_shared import BaseHandler, EventRegistry, EventFilterUtil

class AITaskHandler(BaseHandler):
    """Handle AI processing tasks."""

    async def handle(self, event, context):
        event_type = event.body.get("event_type", "")
        domain, action, entity = event_type.split('.')

        if action == "process" and entity == "ai":
            await self.process_ai_request(event.body)
        elif action == "generate" and entity == "response":
            await self.generate_ai_response(event.body)

    async def process_ai_request(self, data):
        # Your AI processing logic
        response = await self.run_ai_model(data.get("input"))

        # Emit response event
        await self.emit_event("sms-events", "sms.response.generated", {
            "phone_number": data.get("phone_number"),
            "response": response,
            "original_message_id": data.get("message_id")
        })

# Setup registry
registry = EventRegistry()
ai_handler = AITaskHandler(emitter)
registry.register_pattern(re.compile(r'^sms\.(process|generate)\..*'), ai_handler)

# Event filtering for AI service
ai_filter = EventFilterUtil([
    re.compile(r'^sms\.process\.ai),
    re.compile(r'^task\.execute\.ai.*')
])

# Main event processor
async def process_events(events, context):
    relevant_events = ai_filter.filter_events(events)

    for event in relevant_events:
        try:
            await registry.route(event, context)
            await context.update_checkpoint(event)
        except Exception as error:
            print(f"Error processing event: {error}")
            await context.update_checkpoint(event)

# Start AI service
async def start_ai_service():
    client = await consumer.create_consumer('sms-events', 'ai-service')

    async with client:
        await client.receive(on_event=process_events)

if __name__ == "__main__":
    asyncio.run(start_ai_service())
```

## SMS Processing Workflow

```python
# AI Service processes incoming SMS
class SMSAIHandler(BaseHandler):
    async def handle(self, event, context):
        if event.body.get("event_type") == "sms.process.ai":
            phone_number = event.body.get("phone_number")
            message = event.body.get("message")

            # Process with AI
            ai_response = await self.generate_response(message)

            # Check if response should be delayed
            if ai_response.get("delay_minutes"):
                # Schedule delayed response
                correlation_id = await self.scheduler.schedule_task({
                    "event_type": "sms.send.tenant",
                    "data": {
                        "phone_number": phone_number,
                        "message": ai_response["text"]
                    },
                    "execute_at": datetime.now() + timedelta(minutes=ai_response["delay_minutes"])
                })
            else:
                # Send immediately
                await self.emit_event("sms-events", "sms.send.tenant", {
                    "phone_number": phone_number,
                    "message": ai_response["text"]
                })
```

## Environment Configuration

```bash
# Event Hub
EVENT_HUB_NAMESPACE=your-namespace.servicebus.windows.net
STORAGE_ACCOUNT=yourstorageaccount
CHECKPOINT_CONTAINER=eventhub-checkpoints

# Service Bus
SERVICE_BUS_NAMESPACE=your-servicebus-namespace

# Azure credentials
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

## Development Setup

```bash
# Clone repository
git clone https://github.com/flexwurx/event-hub-python.git
cd event-hub-python

# Install with UV
uv sync

# Install development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run black src/

# Type checking
uv run mypy src/
```

## Key Features

✅ **Event Hub Integration** - Full async support with blob checkpointing  
✅ **Service Bus Scheduling** - Schedule tasks with correlation ID cancellation  
✅ **Dead Letter Handling** - Failed events go to Service Bus for analysis  
✅ **Type Safety** - Pydantic models for all event data  
✅ **Async/Await** - Modern Python async patterns  
✅ **Event Filtering** - Service-specific pattern matching  
✅ **Auto Partitioning** - Intelligent event distribution
