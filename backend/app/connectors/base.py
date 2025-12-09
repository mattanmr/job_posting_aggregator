from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class JobPosting:
    """Data class for a job posting."""
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    posted_date: Optional[datetime] = None
    salary: Optional[str] = None
    diploma_required: Optional[str] = None
    years_experience: Optional[str] = None


class JobConnector:
    """Base class for job source connectors."""
    
    def search(self, q: str, page: int = 1) -> List[JobPosting]:
        """Search for jobs. Must be implemented by subclasses."""
        raise NotImplementedError


# Keep BaseConnector for backwards compatibility
class BaseConnector(JobConnector):
    """Base class for job source connectors. Deprecated, use JobConnector instead."""
    
    def search(self, q: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for jobs. Must be implemented by subclasses."""
        raise NotImplementedError
