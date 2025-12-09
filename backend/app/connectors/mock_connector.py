from typing import List, Dict, Any
from ..utils import normalize_job
from .base import BaseConnector

class MockConnector(BaseConnector):
    """Mock connector with sample job data for testing."""
    
    def __init__(self):
        # Sample job data for demonstration
        self.jobs = [
            {
                "id": "mock-1",
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "description": "We are looking for an experienced Python developer to join our team. Requirements: 5+ years of experience with Python, FastAPI, and cloud technologies.",
                "url": "https://example.com/job/1",
                "post_date": "2025-12-06"
            },
            {
                "id": "mock-2",
                "title": "Frontend React Engineer",
                "company": "StartUp Inc",
                "location": "New York, NY",
                "description": "Seeking a talented React developer for our innovative web platform. Experience with TypeScript and Vite is a plus.",
                "url": "https://example.com/job/2",
                "post_date": "2025-12-05"
            },
            {
                "id": "mock-3",
                "title": "Full Stack Developer",
                "company": "Enterprise Solutions",
                "location": "Remote",
                "description": "Join our team as a Full Stack Developer. Work with Python backend and React frontend. Must have 3+ years of experience.",
                "url": "https://example.com/job/3",
                "post_date": "2025-12-04"
            },
            {
                "id": "mock-4",
                "title": "DevOps Engineer",
                "company": "Cloud Systems Ltd",
                "location": "Austin, TX",
                "description": "Looking for a DevOps Engineer experienced with Docker, Kubernetes, and CI/CD pipelines.",
                "url": "https://example.com/job/4",
                "post_date": "2025-12-03"
            },
            {
                "id": "mock-5",
                "title": "Junior Python Developer",
                "company": "Learning Labs",
                "location": "Boston, MA",
                "description": "Great opportunity for junior developers to grow. We provide mentorship and training in Python web development.",
                "url": "https://example.com/job/5",
                "post_date": "2025-12-02"
            },
        ]
    
    def search(self, q: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search jobs by keyword in title, description, or company."""
        ql = q.lower()
        results = []
        
        for j in self.jobs:
            if (ql in j.get("title", "").lower() or 
                ql in j.get("description", "").lower() or 
                ql in j.get("company", "").lower()):
                results.append(normalize_job(j, source="mock"))
        
        return results
