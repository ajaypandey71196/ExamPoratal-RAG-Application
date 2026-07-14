"""Qdrant vector database service."""

import logging
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)


class QdrantService:
    """Service for interacting with Qdrant vector database."""

    def __init__(self, url: str, api_key: Optional[str] = None):
        """Initialize Qdrant client."""
        self.url = url
        self.api_key = api_key
        logger.info(f"Connecting to Qdrant at {url}")
        
        try:
            self.client = QdrantClient(
                url=url,
                api_key=api_key,
                timeout=30
            )
            logger.info("✅ Connected to Qdrant")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {e}")
            raise

    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        try:
            self.client.get_collection(collection_name)
            return True
        except:
            return False

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance_metric: str = "Cosine"
    ) -> bool:
        """Create a new collection."""
        try:
            if self.collection_exists(collection_name):
                logger.info(f"Collection {collection_name} already exists")
                return True

            self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE if distance_metric == "Cosine" else Distance.EUCLID
                )
            )
            logger.info(f"✅ Created collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creating collection: {e}")
            raise

    def upsert_vectors(
        self,
        collection_name: str,
        points: List[PointStruct]
    ) -> bool:
        """Insert or update vectors in collection."""
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"✅ Upserted {len(points)} vectors into {collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error upserting vectors: {e}")
            raise

    def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: float = 0.0,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            # Build filter if provided
            filter_obj = None
            if filter_conditions:
                filter_obj = Filter(
                    must=[
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                        for key, value in filter_conditions.items()
                    ]
                )

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_obj
            )

            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"❌ Error searching vectors: {e}")
            raise

    def delete_points(
        self,
        collection_name: str,
        point_ids: List[str]
    ) -> bool:
        """Delete points from collection."""
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids
            )
            logger.info(f"✅ Deleted {len(point_ids)} points from {collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting points: {e}")
            raise

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information."""
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "points_count": info.points_count,
                "vectors_count": info.vectors_count,
                "config": str(info.config)
            }
        except Exception as e:
            logger.error(f"❌ Error getting collection info: {e}")
            raise

    def delete_collection(self, collection_name: str) -> bool:
        """Delete entire collection."""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"✅ Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting collection: {e}")
            raise


# Global Qdrant service instance
_qdrant_service: Optional[QdrantService] = None


def get_qdrant_service(url: str, api_key: Optional[str] = None) -> QdrantService:
    """Get or create Qdrant service."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService(url, api_key)
    return _qdrant_service
