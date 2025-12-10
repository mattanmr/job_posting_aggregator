"""Collection history tracking for monitoring and debugging."""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

HISTORY_FILE = Path(__file__).parent / "data" / "collection_history.json"


def log_collection(
    status: str,
    total_jobs: int,
    keywords: List[str],
    error: Optional[str] = None,
    filename: Optional[str] = None,
) -> None:
    """
    Log a collection event to history.
    
    Args:
        status: "success" or "error"
        total_jobs: Number of jobs collected
        keywords: List of keywords that were collected
        error: Error message if collection failed
        filename: CSV filename if collection succeeded
    """
    HISTORY_FILE.parent.mkdir(exist_ok=True)

    history = []
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            history = []

    entry = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "total_jobs": total_jobs,
        "keywords_count": len(keywords),
        "keywords": keywords,
        "filename": filename,
        "error": error,
    }

    history.append(entry)

    # Keep only last 100 entries
    history = history[-100:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def get_collection_history(limit: int = 20) -> List[Dict]:
    """Get recent collection history entries."""
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
            return history[-limit:] if history else []
    except:
        return []
