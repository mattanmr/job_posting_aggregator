from fastapi import APIRouter, Query, Request, HTTPException
from fastapi.responses import FileResponse
from .connectors.mock_connector import MockConnector
from .connectors.serpapi_connector import SerpAPIJobsConnector
from .schemas import JobOut, KeywordRequest, KeywordResponse, CsvFileInfo, CollectionStatus, ScheduleConfigRequest, ScheduleConfigResponse
from .storage import load_keywords, add_keyword, remove_keyword, list_csv_files, get_csv_file_path
from .scheduler import get_next_collection_time, get_last_collection_time, load_schedule_config, update_scheduler_interval, trigger_collection_now
from .collection_history import get_collection_history
from typing import List, Optional
from datetime import datetime
import os
import re
import csv
from pathlib import Path

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
    
    # Validate keyword: alphanumeric, spaces, hyphens, underscores only
    keyword = request.keyword.strip()
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', keyword):
        raise HTTPException(status_code=400, detail="Keyword can only contain letters, numbers, spaces, hyphens, and underscores")
    
    if len(keyword) > 100:
        raise HTTPException(status_code=400, detail="Keyword must be 100 characters or less")
    
    success = add_keyword(keyword)
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
    # Validate filename to prevent directory traversal and path injection
    if not filename or not re.match(r'^jobs_collection_\d{8}_\d{6}\.csv$', filename):
        raise HTTPException(status_code=400, detail="Invalid filename format")
    
    filepath = get_csv_file_path(filename)
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Additional security: verify resolved path is within data directory
    try:
        resolved_path = filepath.resolve()
        csv_dir = (Path(__file__).parent / "data" / "csv_files").resolve()
        if not str(resolved_path).startswith(str(csv_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="text/csv"
    )


@router.delete("/api/csv/{filename}")
async def delete_csv_file(filename: str):
    """Delete a specific CSV file."""
    # Validate filename to prevent directory traversal and path injection
    if not filename or not re.match(r'^jobs_collection_\d{8}_\d{6}\.csv$', filename):
        print(f"Invalid filename format: {filename}")
        raise HTTPException(status_code=400, detail="Invalid filename format")
    
    filepath = get_csv_file_path(filename)
    print(f"Getting path for filename: {filename}, result: {filepath}")
    if not filepath:
        print(f"File not found for filename: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    
    # Additional security: verify resolved path is within data directory
    try:
        resolved_path = filepath.resolve()
        csv_dir = (Path(__file__).parent / "data" / "csv_files").resolve()
        print(f"Resolved path: {resolved_path}, CSV dir: {csv_dir}")
        if not str(resolved_path).startswith(str(csv_dir)):
            print(f"Access denied: path not in CSV directory")
            raise HTTPException(status_code=403, detail="Access denied")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in path verification: {e}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete the file
    try:
        filepath_str = str(filepath)
        print(f"Attempting to delete file: {filepath_str}")
        print(f"File exists before delete: {os.path.exists(filepath_str)}")
        os.remove(filepath_str)
        print(f"Successfully deleted file: {filepath_str}")
        return {"message": f"File {filename} deleted successfully"}
    except FileNotFoundError:
        print(f"FileNotFoundError: {filename}")
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        print(f"Error deleting file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")


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


@router.post("/api/collect-now")
async def collect_now():
    """Trigger immediate job collection for all keywords."""
    try:
        result = trigger_collection_now()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Collection failed: {str(e)}"
        )


@router.get("/api/collection-history")
async def get_collection_history_endpoint(limit: int = Query(20, ge=1, le=100)):
    """Get collection history and statistics."""
    history = get_collection_history(limit=limit)
    return {"history": history}


@router.get("/api/csv-files/{filename}/preview")
async def preview_csv_file(filename: str, limit: int = Query(100, ge=1, le=1000)):
    """
    Preview CSV file content without downloading.
    
    Args:
        filename: CSV filename
        limit: Maximum number of rows to return (default 100, max 1000)
    
    Returns:
        JSON with headers, rows, and metadata
    """
    # Validate filename to prevent directory traversal
    if not filename or not re.match(r'^jobs_collection_\d{8}_\d{6}\.csv$', filename):
        raise HTTPException(status_code=400, detail="Invalid filename format")
    
    filepath = get_csv_file_path(filename)
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Security: verify resolved path is within data directory
    try:
        resolved_path = filepath.resolve()
        csv_dir = (Path(__file__).parent / "data" / "csv_files").resolve()
        if not str(resolved_path).startswith(str(csv_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Read and return CSV content
    try:
        rows = []
        headers = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            
            # Read up to limit rows
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                rows.append(row)
        
        return {
            "filename": filename,
            "headers": headers,
            "rows": rows,
            "total_rows": len(rows),
            "has_more": len(rows) == limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {str(e)}")
