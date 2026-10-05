from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.load.qdrant_loader import QdrantLoader
from src.transform.embedding_generator import EmbeddingGenerator

app = FastAPI(
    title="CortexFlow API",
    description="Семантический поиск воспоминаний роботов",
    version="1.0.0"
)

qdrant_loader = QdrantLoader()
embedding_generator = EmbeddingGenerator()


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3


class SearchResult(BaseModel):
    context: str
    score: float
    vehicle_id: str
    timestamp: str
    event_id: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int


@app.get("/")
def root():
    return {"message": "CortexFlow API работает", "docs": "/docs"}


@app.get("/health")
def health_check():
    try:
        info = qdrant_loader.client.get_collection(qdrant_loader.collection_name)
        return {
            "status": "healthy",
            "qdrant": {
                "status": "connected",
                "collection": qdrant_loader.collection_name,
                "points_count": info.points_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@app.post("/search", response_model=SearchResponse)
def search_memories(request: SearchRequest):
    try:
        query_vector = embedding_generator.generate(request.query)
        results = qdrant_loader.client.query_points(
            collection_name=qdrant_loader.collection_name,
            query=query_vector,
            limit=request.top_k,
        )

        search_results = []
        for point in results.points:
            search_results.append(SearchResult(
                context=point.payload.get("context", ""),
                score=point.score,
                vehicle_id=point.payload.get("vehicle_id", ""),
                timestamp=point.payload.get("timestamp", ""),
                event_id=point.payload.get("event_id")
            ))

        return SearchResponse(
            query=request.query,
            results=search_results,
            total=len(search_results)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")