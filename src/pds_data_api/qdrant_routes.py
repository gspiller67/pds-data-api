from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from .qdrant_service import QdrantService
from sqlalchemy.orm import Session
from .database import get_db

router = APIRouter(prefix="/qdrant", tags=["qdrant"])

# Pydantic models for request/response validation
class CollectionCreate(BaseModel):
    collection_name: str
    vector_size: int
    distance: str = "Cosine"
    on_disk_payload: bool = True

class Point(BaseModel):
    id: str
    vector: List[float]
    payload: Dict[str, Any] = Field(default_factory=dict)

class SearchRequest(BaseModel):
    vector: List[float]
    limit: int = 10
    filter: Optional[Dict[str, Any]] = None
    with_payload: bool = True

class ScrollRequest(BaseModel):
    limit: int = 100
    offset: Optional[Dict[str, Any]] = None
    filter: Optional[Dict[str, Any]] = None
    with_payload: bool = True

# Dependency for QdrantService
def get_qdrant_service(db: Session = Depends(get_db)):
    service = QdrantService(db)
    try:
        yield service
    finally:
        service.close()

@router.post("/collections/{collection_name}")
def create_collection(
    collection_params: CollectionCreate,
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Create a new collection in Qdrant."""
    return qdrant.create_collection(
        collection_name=collection_params.collection_name,
        vector_size=collection_params.vector_size,
        distance=collection_params.distance,
        on_disk_payload=collection_params.on_disk_payload
    )

@router.delete("/collections/{collection_name}")
def delete_collection(
    collection_name: str,
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Delete a collection from Qdrant."""
    return qdrant.delete_collection(collection_name)

@router.get("/collections")
def list_collections(
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """List all collections in Qdrant."""
    return qdrant.list_collections()

@router.get("/collections/{collection_name}")
def get_collection(
    collection_name: str,
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Get collection info from Qdrant."""
    return qdrant.get_collection(collection_name)

@router.put("/collections/{collection_name}/points")
def upsert_points(
    collection_name: str,
    points: List[Point],
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Upsert points into a collection."""
    points_data = [
        {
            "id": point.id,
            "vector": point.vector,
            "payload": point.payload
        }
        for point in points
    ]
    return qdrant.upsert_points(collection_name, points_data)

@router.post("/collections/{collection_name}/points/search")
def search_points(
    collection_name: str,
    search_request: SearchRequest,
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Search for points in a collection."""
    return qdrant.search_points(
        collection_name=collection_name,
        query_vector=search_request.vector,
        limit=search_request.limit,
        score_threshold=search_request.filter.get('score_threshold') if search_request.filter else None
    )

@router.post("/collections/{collection_name}/points/delete")
def delete_points(
    collection_name: str,
    points: Union[List[str], Dict[str, Any]],
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Delete points from a collection by IDs or filter."""
    return qdrant.delete_points(collection_name, points)

@router.get("/collections/{collection_name}/points")
def get_points(
    collection_name: str,
    point_ids: List[str],
    with_payload: bool = True,
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Retrieve points by their IDs."""
    return qdrant.get_points(
        collection_name=collection_name,
        point_ids=point_ids,
        with_payload=with_payload
    )

@router.post("/collections/{collection_name}/points/scroll")
def scroll_points(
    collection_name: str,
    scroll_request: ScrollRequest,
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Scroll through points in a collection."""
    return qdrant.scroll_points(
        collection_name=collection_name,
        limit=scroll_request.limit,
        offset=scroll_request.offset
    )

@router.post("/collections/{collection_name}/points/count")
def count_points(
    collection_name: str,
    filter: Optional[Dict[str, Any]] = None,
    qdrant: QdrantService = Depends(get_qdrant_service)
):
    """Count points in a collection, optionally filtered."""
    return qdrant.count_points(collection_name) 