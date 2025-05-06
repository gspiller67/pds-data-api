from qdrant_client import QdrantClient as BaseQdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class SafeQdrantClient:
    def __init__(self, host: str, port: int, api_key: Optional[str] = None, **kwargs):
        """Initialize a safe Qdrant client with only essential parameters."""
        # Log all kwargs being passed
        logger.info(f"QdrantClient kwargs: {kwargs}")
        
        # Construct URL from host and port
        url = f"http://{host}:{port}"
        
        # Log the exact configuration being passed
        config = {
            'url': url,
            'api_key': api_key
        }
        logger.info(f"QdrantClient config: {json.dumps(config, default=str)}")
        
        # Initialize with URL and API key only
        self.client = BaseQdrantClient(
            url=url,
            api_key=api_key
        )
    
    def get_collection(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information."""
        return self.client.get_collection(collection_name)
    
    def create_collection(self, collection_name: str):
        """Create a new collection with default settings."""
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1536,  # OpenAI embedding size
                distance=models.Distance.COSINE
            ),
            optimizers_config=models.OptimizersConfigDiff(
                indexing_threshold=0,
                memmap_threshold=20000,
                max_optimization_threads=4
            ),
            hnsw_config=models.HnswConfigDiff(
                m=16,
                ef_construct=100
            )
        )
    
    def upsert(self, collection_name: str, points: List[models.PointStruct]):
        """Upsert points to a collection."""
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
    
    def search(self, collection_name: str, query_vector: List[float], limit: int = 10):
        """Search for similar vectors."""
        return self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit
        ) 