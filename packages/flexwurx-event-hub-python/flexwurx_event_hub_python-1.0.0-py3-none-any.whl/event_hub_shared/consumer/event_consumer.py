"""Event Hub consumer with blob checkpoint store."""

from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore  # Remove 'aio'
from azure.storage.blob.aio import BlobServiceClient
from azure.identity.aio import DefaultAzureCredential


class EventConsumer:
    """Managed consumer setup with blob checkpointing."""
    
    def __init__(
        self,
        namespace: str,
        storage_account_name: str,
        checkpoint_container: str
    ):
        """Initialize event consumer.
        
        Args:
            namespace: Event Hub namespace
            storage_account_name: Storage account for checkpoints
            checkpoint_container: Blob container for checkpoints
        """
        self._namespace = namespace
        self._storage_account_name = storage_account_name
        self._checkpoint_container = checkpoint_container
        self._credential = DefaultAzureCredential()
    
    async def create_consumer(
        self, 
        hub_name: str, 
        consumer_group: str
    ) -> EventHubConsumerClient:
        """Create consumer with blob checkpoint store.
        
        Args:
            hub_name: Event Hub name
            consumer_group: Consumer group name
            
        Returns:
            Configured EventHubConsumerClient
        """
        # Create blob service client
        blob_service_client = BlobServiceClient(
            account_url=f"https://{self._storage_account_name}.blob.core.windows.net",
            credential=self._credential
        )
        
        # Create checkpoint store
        checkpoint_store = BlobCheckpointStore(
            blob_service_client=blob_service_client,
            container_name=self._checkpoint_container
        )
        
        return EventHubConsumerClient(
            fully_qualified_namespace=self._namespace,
            eventhub_name=hub_name,
            consumer_group=consumer_group,
            credential=self._credential,
            checkpoint_store=checkpoint_store
        )