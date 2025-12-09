from typing import List
from .base import JobConnector, JobPosting


class MockConnector(JobConnector):
    """Mock connector with sample job data for testing."""
    
    def __init__(self):
        # Sample job data for demonstration
        self.jobs = [
            {
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "description": "We are looking for an experienced Python developer to join our team. Requirements: 5+ years of experience with Python, FastAPI, and cloud technologies.",
                "url": "https://example.com/job/1",
            },
            {
                "title": "Frontend React Engineer",
                "company": "StartUp Inc",
                "location": "New York, NY",
                "description": "Seeking a talented React developer for our innovative web platform. Experience with TypeScript and Vite is a plus.",
                "url": "https://example.com/job/2",
            },
            {
                "title": "Full Stack Developer",
                "company": "Enterprise Solutions",
                "location": "Remote",
                "description": "Join our team as a Full Stack Developer. Work with Python backend and React frontend. Must have 3+ years of experience.",
                "url": "https://example.com/job/3",
            },
            {
                "title": "DevOps Engineer",
                "company": "Cloud Systems Ltd",
                "location": "Austin, TX",
                "description": "Looking for a DevOps Engineer experienced with Docker, Kubernetes, and CI/CD pipelines.",
                "url": "https://example.com/job/4",
            },
            {
                "title": "Junior Python Developer",
                "company": "Learning Labs",
                "location": "Boston, MA",
                "description": "Great opportunity for junior developers to grow. We provide mentorship and training in Python web development.",
                "url": "https://example.com/job/5",
            },
        ]
    
    def search(self, q: str, page: int = 1) -> List[JobPosting]:
        """Search jobs by keyword in title, description, or company."""
        ql = q.lower()
        results = []
        
        for j in self.jobs:
            if (ql in j.get("title", "").lower() or 
                ql in j.get("description", "").lower() or 
                ql in j.get("company", "").lower()):
                results.append(JobPosting(
                    title=j["title"],
                    company=j["company"],
                    location=j["location"],
                    description=j["description"],
                    url=j["url"],
                    source="Mock Data",
                ))
        
        return results
