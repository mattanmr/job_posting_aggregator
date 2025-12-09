from typing import Dict, Any

def normalize_job(raw: Dict[str, Any], source: str) -> Dict[str, Any]:
    """Normalize job data to consistent format."""
    normalized = {
        "id": raw.get("id") or raw.get("url") or f"{source}:{raw.get('title','')}",
        "title": raw.get("title"),
        "company": raw.get("company"),
        "location": raw.get("location"),
        "post_date": raw.get("post_date"),
        "description": raw.get("description"),
        "url": raw.get("url"),
        "source": source,
        "raw": raw
    }
    return normalized
