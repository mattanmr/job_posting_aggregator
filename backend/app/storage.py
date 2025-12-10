"""Storage module for managing keywords and CSV files."""
import os
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from app.connectors.base import JobPosting


# Define paths
DATA_DIR = Path(__file__).parent / "data"
CSV_DIR = DATA_DIR / "csv_files"
KEYWORDS_FILE = DATA_DIR / "keywords.json"

# CSV retention policy: keep last N files or files newer than X days
CSV_MAX_FILES = 30  # Keep maximum 30 CSV files
CSV_RETENTION_DAYS = 90  # Delete files older than 90 days


def initialize_storage():
    """Initialize storage directories and files."""
    DATA_DIR.mkdir(exist_ok=True)
    CSV_DIR.mkdir(exist_ok=True)
    
    if not KEYWORDS_FILE.exists():
        save_keywords([])
    
    # Apply retention policy on startup
    cleanup_old_csv_files()


def load_keywords() -> List[str]:
    """Load keywords from JSON file."""
    if not KEYWORDS_FILE.exists():
        return []
    
    try:
        with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_keywords(keywords: List[str]):
    """Save keywords to JSON file."""
    with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(keywords, f, indent=2)


def add_keyword(keyword: str) -> bool:
    """Add a keyword if it doesn't already exist."""
    keywords = load_keywords()
    keyword = keyword.strip().lower()
    
    if keyword and keyword not in keywords:
        keywords.append(keyword)
        save_keywords(keywords)
        return True
    return False


def remove_keyword(keyword: str) -> bool:
    """Remove a keyword if it exists."""
    keywords = load_keywords()
    keyword = keyword.strip().lower()
    
    if keyword in keywords:
        keywords.remove(keyword)
        save_keywords(keywords)
        return True
    return False


def save_jobs_to_csv(jobs: List[JobPosting]) -> str:
    """
    Save job postings to a single CSV file for the collection cycle.
    
    Args:
        jobs: List of JobPosting objects from all keywords
    
    Returns:
        Filename of the created CSV file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"jobs_collection_{timestamp}.csv"
    filepath = CSV_DIR / filename
    
    fieldnames = [
        'title',
        'company',
        'location',
        'diploma_required',
        'years_experience',
        'url',
        'posted_date',
        'description'
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for job in jobs:
            writer.writerow({
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'diploma_required': job.diploma_required or 'Not specified',
                'years_experience': job.years_experience or 'Not specified',
                'url': job.url,
                'posted_date': job.posted_date.isoformat() if job.posted_date else 'Not specified',
                'description': job.description[:500] if job.description else ''  # Truncate description
            })
    
    return filename


def list_csv_files() -> List[Dict[str, any]]:
    """
    List all CSV files with metadata.
    
    Returns:
        List of dicts with filename, timestamp, and file size
    """
    if not CSV_DIR.exists():
        return []
    
    files = []
    for filepath in CSV_DIR.glob("jobs_collection_*.csv"):
        stat = filepath.stat()
        
        # Parse filename: jobs_collection_{timestamp}.csv
        name_parts = filepath.stem.split('_')  # ['jobs', 'collection', YYYYMMDD, HHMMSS]
        timestamp_str = '_'.join(name_parts[-2:]) if len(name_parts) >= 4 else ''
        
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
        except ValueError:
            timestamp = datetime.fromtimestamp(stat.st_mtime)
        
        # Count jobs in file
        job_count = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                job_count = sum(1 for _ in csv.DictReader(f))
        except:
            job_count = 0
        
        files.append({
            'filename': filepath.name,
            'timestamp': timestamp.isoformat(),
            'size': stat.st_size,
            'job_count': job_count
        })
    
    # Sort by timestamp, newest first
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    return files


def get_csv_file_path(filename: str) -> Optional[Path]:
    """
    Get the full path to a CSV file if it exists.
    
    Returns:
        Path object if file exists, None otherwise
    """
    filepath = CSV_DIR / filename
    if filepath.exists() and filepath.is_file():
        return filepath
    return None


def cleanup_old_csv_files():
    """
    Clean up old CSV files based on retention policy.
    Keeps maximum CSV_MAX_FILES files and deletes files older than CSV_RETENTION_DAYS.
    """
    if not CSV_DIR.exists():
        return
    
    files = []
    for filepath in CSV_DIR.glob("jobs_collection_*.csv"):
        stat = filepath.stat()
        files.append((filepath, stat.st_mtime))
    
    if not files:
        return
    
    # Sort by modification time (newest first)
    files.sort(key=lambda x: x[1], reverse=True)
    
    # Delete files exceeding max file count
    if len(files) > CSV_MAX_FILES:
        for filepath, _ in files[CSV_MAX_FILES:]:
            try:
                filepath.unlink()
                print(f"Deleted old CSV file: {filepath.name}")
            except Exception as e:
                print(f"Error deleting CSV file {filepath.name}: {e}")
    
    # Delete files older than retention period
    cutoff_time = (datetime.now() - timedelta(days=CSV_RETENTION_DAYS)).timestamp()
    for filepath, mtime in files:
        if mtime < cutoff_time:
            try:
                filepath.unlink()
                print(f"Deleted expired CSV file: {filepath.name}")
            except Exception as e:
                print(f"Error deleting CSV file {filepath.name}: {e}")
