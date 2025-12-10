from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import FileResponse
from .connectors.mock_connector import MockConnector
from .connectors.serpapi_connector import SerpAPIJobsConnector
from .schemas import JobOut, KeywordRequest, KeywordResponse, CsvFileInfo, CollectionStatus, ScheduleConfigRequest, ScheduleConfigResponse
from .storage import load_keywords, add_keyword, remove_keyword, list_csv_files, get_csv_file_path
from .scheduler import get_next_collection_time, get_last_collection_time, load_schedule_config, update_scheduler_interval
from typing import List, Optional
from datetime import datetime
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
                    "post_date": job.posted_date.isoformat() if job.posted_date else None,
                    "diploma_required": job.diploma_required,
                    "years_experience": job.years_experience,
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
                "post_date": job.posted_date.isoformat() if job.posted_date else None,
                "diploma_required": job.diploma_required,
                "years_experience": job.years_experience,
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


# Keywords management endpoints

@router.get("/api/keywords", response_model=KeywordResponse)
async def get_keywords():
    """Get all configured keywords."""
    keywords = load_keywords()
    return KeywordResponse(keywords=keywords)


@router.post("/api/keywords", response_model=KeywordResponse)
async def add_keyword_endpoint(request: KeywordRequest):
    """Add a new keyword for job collection."""
    if not request.keyword or not request.keyword.strip():
        raise HTTPException(status_code=400, detail="Keyword cannot be empty")
    
    success = add_keyword(request.keyword)
    keywords = load_keywords()
    
    if not success:
        raise HTTPException(status_code=409, detail="Keyword already exists")
    
    return KeywordResponse(keywords=keywords)


@router.delete("/api/keywords/{keyword}", response_model=KeywordResponse)
async def delete_keyword_endpoint(keyword: str):
    """Remove a keyword from job collection."""
    success = remove_keyword(keyword)
    keywords = load_keywords()
    
    if not success:
        raise HTTPException(status_code=404, detail="Keyword not found")
    
    return KeywordResponse(keywords=keywords)


# CSV files endpoints

@router.get("/api/csv-files", response_model=List[CsvFileInfo])
async def get_csv_files():
    """Get list of all collected CSV files."""
    files = list_csv_files()
    return files


@router.get("/api/csv-files/{filename}")
async def download_csv_file(filename: str):
    """Download a specific CSV file."""
    # Validate filename to prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    filepath = get_csv_file_path(filename)
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="text/csv"
    )


# Collection status endpoint

@router.get("/api/next-collection", response_model=CollectionStatus)
async def get_collection_status():
    """Get next job collection time and last collection info."""
    next_time = get_next_collection_time()
    last_time = get_last_collection_time()
    
    # Default to 12 hours from now if scheduler not initialized
    if not next_time:
        from datetime import datetime, timedelta
        next_dt = datetime.now() + timedelta(hours=12)
        next_time = next_dt.isoformat()
        next_time_readable = next_dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        from datetime import datetime
        next_dt = datetime.fromisoformat(next_time)
        next_time_readable = next_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    last_time_readable = None
    if last_time:
        last_dt = datetime.fromisoformat(last_time)
        last_time_readable = last_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    return CollectionStatus(
        next_collection_timestamp=next_time,
        next_collection_time=next_time_readable,
        last_collection_timestamp=last_time,
        last_collection_time=last_time_readable
    )


# Schedule configuration endpoints

@router.get("/api/schedule-config", response_model=ScheduleConfigResponse)
async def get_schedule_config():
    """Get current schedule configuration."""
    interval_hours = load_schedule_config()
    return ScheduleConfigResponse(interval_hours=interval_hours)


@router.put("/api/schedule-config", response_model=ScheduleConfigResponse)
async def update_schedule_config(request: ScheduleConfigRequest):
    """Update schedule configuration."""
    interval_hours = request.interval_hours
    
    # Validate interval (1 hour to 1 week)
    if interval_hours < 1 or interval_hours > 168:
        raise HTTPException(
            status_code=400,
            detail="Interval must be between 1 and 168 hours (1 hour to 1 week)"
        )
    
    try:
        update_scheduler_interval(interval_hours)
        return ScheduleConfigResponse(interval_hours=interval_hours)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))