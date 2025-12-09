from fastapi import APIRouter, Query, Request
from .connectors.mock_connector import MockConnector
from .connectors.serpapi_connector import SerpAPIJobsConnector
from .schemas import JobOut
from typing import List, Optional
import os

router = APIRouter()

# Initialize connectors
mock = MockConnector()

# SerpAPI connector (will be None if API key not set)
try:
    serpapi = SerpAPIJobsConnector()
except ValueError:
    serpapi = None
    print("SerpAPI key not found. Set SERPAPI_KEY environment variable to enable.")

@router.get("/search", response_model=List[JobOut])
async def search(
    request: Request,
    q: str = Query(..., description="Search keywords"), 
    location: Optional[str] = Query(None, description="Location to search in"),
    gl: str = Query("us", description="Country code (e.g., us, uk, il)"),
    hl: str = Query("en", description="Language code (e.g., en, es, he)"),
    page: int = Query(1, ge=1, le=10, description="Page number")
):
    """Search for jobs across available sources."""
    results = []
    
    # Try SerpAPI first if available
    if serpapi:
        try:
            serpapi_jobs = serpapi.search(
                query=q,
                location=location,
                gl=gl,
                hl=hl
            )
            
            # Convert to dict format for response
            for job in serpapi_jobs:
                results.append({
                    "id": job.url,  # Use URL as unique ID
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "description": job.description,
                    "url": job.url,
                    "source": job.source,
                    "posted_date": job.posted_date.isoformat() if job.posted_date else None,
                    "salary": job.salary
                })
        except Exception as e:
            print(f"Error fetching from SerpAPI: {e}")
    
    # Fallback to mock data if no real results
    if not results:
        mock_jobs = mock.search(q, page)
        for job in mock_jobs:
            results.append({
                "id": job.url,
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "description": job.description,
                "url": job.url,
                "source": job.source,
                "posted_date": job.posted_date.isoformat() if job.posted_date else None,
                "salary": job.salary
            })
    
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
