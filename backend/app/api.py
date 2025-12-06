from fastapi import APIRouter, Query
from .connectors.mock_connector import MockConnector
from .schemas import JobOut
from typing import List, Optional
import os

router = APIRouter()

# Initialize mock connector
mock = MockConnector()

@router.get("/search", response_model=List[JobOut])
async def search(q: str = Query(..., description="Search keywords"), page: int = 1):
    """Search for jobs across available sources."""
    results = []
    
    # Use mock data (can add real connectors later)
    results.extend(mock.search(q, page))
    
    # Simple deduplication by url or id
    seen = set()
    deduped = []
    for r in results:
        key = r.get("id") or r.get("url")
        if key and key not in seen:
            seen.add(key)
            deduped.append(r)
    
    return deduped

@router.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
