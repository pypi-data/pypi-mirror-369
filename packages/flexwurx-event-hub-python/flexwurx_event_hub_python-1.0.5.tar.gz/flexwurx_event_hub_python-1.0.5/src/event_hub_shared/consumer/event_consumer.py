"""Event Hub consumer with blob checkpoint store."""

from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore  # Remove 'aio'
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential


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
        print(f"Creating consumer for {hub_name} in group {consumer_group}")
        try:
            blob_service_client = BlobServiceClient(
                account_url=f"https://{self._storage_account_name}.blob.core.windows.net",
                credential=self._credential
            )
        except Exception as e:
            print(f"Error creating blob service client: {e}")
            raise e from e
        print(f"Blob service client created for {self._storage_account_name}")
        
        # Create checkpoint store
        print(f"Creating checkpoint store for {self._checkpoint_container}")
        try:
            checkpoint_store = BlobCheckpointStore(
                blob_service_client=blob_service_client,
                # blob_account_url=f"https://{self._storage_account_name}.blob.core.windows.net",
                container_name=self._checkpoint_container,
            )
        except Exception as e:
            print(f"Error creating checkpoint store: {e}")
            raise e from e
        print(f"Checkpoint store created for {self._checkpoint_container}")
        
        print(f"Creating EventHubConsumerClient for {self._namespace} {hub_name} {consumer_group}")
        try:
            return EventHubConsumerClient(
                fully_qualified_namespace=self._namespace,
                eventhub_name=hub_name,
                consumer_group=consumer_group,
                credential=self._credential,
                checkpoint_store=checkpoint_store
            )
        except Exception as e:
            print(f"Error creating EventHubConsumerClient: {e}")
            raise e from e