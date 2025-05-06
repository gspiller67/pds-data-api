from typing import List, Dict, Any, Optional, Union
import logging
from fastapi import HTTPException
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from sqlalchemy.orm import Session
from .models import QdrantCollection, QdrantPoint
import uuid

class QdrantService:
    def __init__(self, db: Session, host: str = "localhost", port: int = 6333):
        """Initialize the Qdrant service with connection details."""
        # Construct URL from host and port
        url = f"http://{host}:{port}"
        self.client = QdrantClient(url=url)
        self.db = db
        self.logger = logging.getLogger(__name__)

    def create_collection(self, name: str, vector_size: int, distance: str = "Cosine", on_disk_payload: bool = True) -> QdrantCollection:
        """Create a new collection in Qdrant."""
        try:
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance[distance])
            )

            # Create collection record in PostgreSQL
            collection = QdrantCollection(
                name=name,
                vector_size=vector_size,
                distance=distance,
                on_disk_payload=on_disk_payload
            )
            self.db.add(collection)
            self.db.commit()
            self.db.refresh(collection)
            return collection
        except Exception as e:
            self.logger.error(f"Error creating collection: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to create collection: {str(e)}")

    def delete_collection(self, name: str) -> bool:
        """Delete a collection from Qdrant."""
        try:
            self.client.delete_collection(collection_name=name)

            # Delete collection record from PostgreSQL
            collection = self.db.query(QdrantCollection).filter(QdrantCollection.name == name).first()
            if collection:
                self.db.delete(collection)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting collection: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete collection: {str(e)}")

    def list_collections(self) -> List[QdrantCollection]:
        """List all collections in Qdrant."""
        try:
            return self.db.query(QdrantCollection).all()
        except Exception as e:
            self.logger.error(f"Error listing collections: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")

    def get_collection(self, name: str) -> Optional[QdrantCollection]:
        """Get collection info from Qdrant."""
        try:
            return self.db.query(QdrantCollection).filter(QdrantCollection.name == name).first()
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to get collection info: {str(e)}")

    def upsert_points(self, collection_name: str, points: List[Dict[str, Any]]) -> List[QdrantPoint]:
        """Upsert points into a collection."""
        try:
            collection = self.get_collection(collection_name)
            if not collection:
                raise ValueError(f"Collection {collection_name} not found")

            # Prepare points for Qdrant
            qdrant_points = []
            for point in points:
                point_id = str(uuid.uuid4()) if 'id' not in point else point['id']
                qdrant_points.append(PointStruct(
                    id=point_id,
                    vector=point['vector'],
                    payload=point.get('payload', {})
                ))

            # Upsert points in Qdrant
            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )

            # Create point records in PostgreSQL
            db_points = []
            for point, qdrant_point in zip(points, qdrant_points):
                db_point = QdrantPoint(
                    collection_id=collection.id,
                    point_id=str(qdrant_point.id),
                    vector=point['vector'],
                    payload=point.get('payload', {})
                )
                self.db.add(db_point)
                db_points.append(db_point)

            self.db.commit()
            return db_points
        except Exception as e:
            self.logger.error(f"Error upserting points: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to upsert points: {str(e)}")

    def search_points(self, collection_name: str, query_vector: List[float], limit: int = 10, score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """Search for points in a collection."""
        try:
            search_params = {}
            if score_threshold is not None:
                search_params['score_threshold'] = score_threshold

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                **search_params
            )

            return [
                {
                    'id': str(result.id),
                    'score': result.score,
                    'payload': result.payload
                }
                for result in results
            ]
        except Exception as e:
            self.logger.error(f"Error searching points: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to search points: {str(e)}")

    def delete_points(self, collection_name: str, point_ids: List[str]) -> bool:
        """Delete points from a collection by IDs."""
        try:
            # Delete points from Qdrant
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=point_ids)
            )

            # Delete points from PostgreSQL
            collection = self.get_collection(collection_name)
            if collection:
                self.db.query(QdrantPoint).filter(
                    QdrantPoint.collection_id == collection.id,
                    QdrantPoint.point_id.in_(point_ids)
                ).delete(synchronize_session=False)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting points: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to delete points: {str(e)}")

    def get_points(self, collection_name: str, point_ids: List[str], with_payload: bool = True) -> List[Dict[str, Any]]:
        """Get points by their IDs."""
        try:
            points = self.client.retrieve(
                collection_name=collection_name,
                ids=point_ids,
                with_payload=with_payload
            )
            return [
                {
                    'id': str(point.id),
                    'vector': point.vector,
                    'payload': point.payload if with_payload else None
                }
                for point in points
            ]
        except Exception as e:
            self.logger.error(f"Error retrieving points: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve points: {str(e)}")

    def scroll_points(self, collection_name: str, limit: int = 10, offset: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Scroll through points in a collection."""
        try:
            scroll_response = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset
            )

            points = [
                {
                    'id': str(point.id),
                    'vector': point.vector,
                    'payload': point.payload
                }
                for point in scroll_response[0]
            ]

            return {
                'points': points,
                'next_page_offset': scroll_response[1]
            }
        except Exception as e:
            self.logger.error(f"Error scrolling points: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to scroll points: {str(e)}")

    def count_points(self, collection_name: str) -> int:
        """Count points in a collection."""
        try:
            collection_info = self.client.get_collection(collection_name=collection_name)
            return collection_info.vectors_count
        except Exception as e:
            self.logger.error(f"Error counting points: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to count points: {str(e)}")

    def close(self):
        """Close the Qdrant client."""
        self.client.close() 