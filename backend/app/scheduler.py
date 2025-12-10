"""Background scheduler for periodic job collection."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from .storage import load_keywords, save_jobs_to_csv, initialize_storage, cleanup_old_csv_files
from .collection_history import log_collection
from .connectors.mock_connector import MockConnector
from .connectors.serpapi_connector import SerpAPIJobsConnector
import os
import json
from pathlib import Path

# Global scheduler instance
scheduler = BackgroundScheduler()

# Store last collection time and schedule config
METADATA_FILE = Path(__file__).parent / "data" / "collection_metadata.json"
CONFIG_FILE = Path(__file__).parent / "data" / "scheduler_config.json"

# Default schedule: 12 hours
DEFAULT_INTERVAL_HOURS = 12


def load_schedule_config():
    """Load scheduling configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get('interval_hours', DEFAULT_INTERVAL_HOURS)
        except:
            pass
    return DEFAULT_INTERVAL_HOURS


def save_schedule_config(interval_hours: int):
    """Save scheduling configuration to file."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    data = {'interval_hours': interval_hours}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)


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
    Saves all collected jobs to a single CSV file per collection cycle.
    Runs every 12 hours.
    """
    print(f"[{datetime.now().isoformat()}] Starting scheduled job collection...")
    
    keywords = load_keywords()
    if not keywords:
        print("No keywords configured. Skipping job collection.")
        log_collection(
            status="skipped",
            total_jobs=0,
            keywords=[],
            error="No keywords configured"
        )
        return
    
    # Initialize connectors
    mock = MockConnector()
    try:
        serpapi = SerpAPIJobsConnector()
    except ValueError:
        serpapi = None
        print("SerpAPI not configured, using mock data only")
    
    all_jobs = []
    job_keywords = {}  # Track which keyword each job came from
    
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
        
        job_keywords[keyword] = jobs  # Store jobs per keyword
        all_jobs.extend(jobs)
    
    # Save all jobs to a single CSV file with keyword tracking
    filename = None
    if all_jobs:
        filename = save_jobs_to_csv(all_jobs, job_keywords)
        print(f"[{datetime.now().isoformat()}] Job collection completed. Total jobs: {len(all_jobs)}")
        print(f"    Saved to {filename}")
        log_collection(
            status="success",
            total_jobs=len(all_jobs),
            keywords=keywords,
            filename=filename
        )
    else:
        print(f"[{datetime.now().isoformat()}] No jobs found for any keyword")
        log_collection(
            status="warning",
            total_jobs=0,
            keywords=keywords,
            error="No jobs found for any keyword"
        )
    
    # Update last collection time
    save_collection_time(datetime.now().isoformat())
    
    # Clean up old CSV files based on retention policy
    cleanup_old_csv_files()


def init_scheduler():
    """Initialize and start the background scheduler."""
    initialize_storage()
    
    # Remove any existing jobs to avoid duplicates
    scheduler.remove_all_jobs()
    
    # Load configured interval
    interval_hours = load_schedule_config()
    
    # Schedule job collection every N hours (configurable)
    scheduler.add_job(
        func=collect_jobs_task,
        trigger=IntervalTrigger(hours=interval_hours),
        id='collect_jobs',
        name='collect_jobs',
        replace_existing=True
    )
    
    # Start scheduler if not already running
    if not scheduler.running:
        scheduler.start()
        print(f"[{datetime.now().isoformat()}] Scheduler started with interval: {interval_hours} hours")


def update_scheduler_interval(interval_hours: int):
    """Update the scheduler interval and reschedule the job."""
    if interval_hours < 1 or interval_hours > 168:  # 1 hour to 1 week
        raise ValueError("Interval must be between 1 and 168 hours")
    
    # Save new configuration
    save_schedule_config(interval_hours)
    
    # Reschedule the job with new interval
    if scheduler.running:
        scheduler.remove_job('collect_jobs')
        scheduler.add_job(
            func=collect_jobs_task,
            trigger=IntervalTrigger(hours=interval_hours),
            id='collect_jobs',
            name='collect_jobs',
            replace_existing=True
        )
        print(f"[{datetime.now().isoformat()}] Scheduler interval updated to {interval_hours} hours")


def shutdown_scheduler():
    """Shutdown the scheduler."""
    if scheduler.running:
        scheduler.shutdown()


def trigger_collection_now() -> dict:
    """
    Trigger job collection immediately for all keywords.
    Saves all collected jobs to a single CSV file.
    Returns collection statistics.
    """
    print(f"[{datetime.now().isoformat()}] Manual collection triggered...")
    
    keywords = load_keywords()
    if not keywords:
        return {
            "status": "skipped",
            "message": "No keywords configured",
            "total_jobs": 0
        }
    
    # Initialize connectors
    mock = MockConnector()
    try:
        serpapi = SerpAPIJobsConnector()
    except ValueError:
        serpapi = None
    
    all_jobs = []
    keywords_collected = []
    
    for keyword in keywords:
        jobs = []
        
        # Try SerpAPI first if available
        if serpapi:
            try:
                jobs = serpapi.search(query=keyword)
            except Exception as e:
                print(f"    Error with SerpAPI: {e}")
        
        # Fallback to mock data if needed
        if not jobs:
            jobs = mock.search(keyword)
        
        if jobs:
            all_jobs.extend(jobs)
            keywords_collected.append({
                "keyword": keyword,
                "job_count": len(jobs)
            })
    
    # Save all jobs to a single CSV file
    filename = None
    if all_jobs:
        filename = save_jobs_to_csv(all_jobs)
        log_collection(
            status="success",
            total_jobs=len(all_jobs),
            keywords=keywords,
            filename=filename
        )
    else:
        log_collection(
            status="warning",
            total_jobs=0,
            keywords=keywords,
            error="No jobs found for any keyword"
        )
    
    # Update last collection time
    save_collection_time(datetime.now().isoformat())
    
    return {
        "status": "success",
        "message": f"Collected {len(all_jobs)} jobs for {len(keywords_collected)} keyword(s)",
        "total_jobs": len(all_jobs),
        "keywords": keywords_collected,
        "filename": filename,
        "timestamp": datetime.now().isoformat()
    }
