"""Background scheduler for periodic job collection."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from .storage import load_keywords, save_jobs_to_csv, initialize_storage
from .connectors.mock_connector import MockConnector
from .connectors.serpapi_connector import SerpAPIJobsConnector
import os
import json
from pathlib import Path

# Global scheduler instance
scheduler = BackgroundScheduler()

# Store last collection time
METADATA_FILE = Path(__file__).parent / "data" / "collection_metadata.json"


def get_last_collection_time():
    """Get the timestamp of the last collection."""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r') as f:
                data = json.load(f)
                return data.get('last_collection')
        except:
            pass
    return None


def save_collection_time(timestamp: str):
    """Save the collection timestamp."""
    METADATA_FILE.parent.mkdir(exist_ok=True)
    data = {}
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r') as f:
                data = json.load(f)
        except:
            pass
    
    data['last_collection'] = timestamp
    with open(METADATA_FILE, 'w') as f:
        json.dump(data, f)


def get_next_collection_time():
    """Calculate next collection time based on scheduler."""
    if not scheduler.running:
        return None
    
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.name == 'collect_jobs':
            # Get next run time
            next_run = job.next_run_time
            if next_run:
                return next_run.isoformat()
    return None


def collect_jobs_task():
    """
    Background task to collect jobs for all keywords.
    Runs every 12 hours.
    """
    print(f"[{datetime.now().isoformat()}] Starting scheduled job collection...")
    
    keywords = load_keywords()
    if not keywords:
        print("No keywords configured. Skipping job collection.")
        return
    
    # Initialize connectors
    mock = MockConnector()
    try:
        serpapi = SerpAPIJobsConnector()
    except ValueError:
        serpapi = None
        print("SerpAPI not configured, using mock data only")
    
    collected_count = 0
    
    for keyword in keywords:
        print(f"  Collecting jobs for keyword: '{keyword}'")
        
        jobs = []
        
        # Try SerpAPI first if available
        if serpapi:
            try:
                jobs = serpapi.search(query=keyword)
                print(f"    Found {len(jobs)} jobs from SerpAPI")
            except Exception as e:
                print(f"    Error with SerpAPI: {e}")
        
        # Fallback to mock data if needed
        if not jobs:
            jobs = mock.search(keyword)
            print(f"    Using mock data: {len(jobs)} jobs")
        
        # Save to CSV
        if jobs:
            filename = save_jobs_to_csv(jobs, keyword)
            print(f"    Saved {len(jobs)} jobs to {filename}")
            collected_count += len(jobs)
        else:
            print(f"    No jobs found for '{keyword}'")
    
    # Update last collection time
    save_collection_time(datetime.now().isoformat())
    print(f"[{datetime.now().isoformat()}] Job collection completed. Total jobs: {collected_count}")


def init_scheduler():
    """Initialize and start the background scheduler."""
    initialize_storage()
    
    # Remove any existing jobs to avoid duplicates
    scheduler.remove_all_jobs()
    
    # Schedule job collection every 12 hours
    scheduler.add_job(
        func=collect_jobs_task,
        trigger=IntervalTrigger(hours=12),
        id='collect_jobs',
        name='collect_jobs',
        replace_existing=True
    )
    
    # Start scheduler if not already running
    if not scheduler.running:
        scheduler.start()


def shutdown_scheduler():
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
