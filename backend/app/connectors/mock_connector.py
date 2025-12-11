from typing import List
from datetime import datetime, timedelta
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
                "description": "We are looking for an experienced Python developer to join our team. Requirements: Bachelor's degree in Computer Science and 5+ years of experience with Python, FastAPI, and cloud technologies.",
                "url": "https://example.com/job/1",
                "diploma": "Bachelor's Degree",
                "experience": "5+ years",
                "posted_date": datetime.now() - timedelta(days=2)
            },
            {
                "title": "Frontend React Engineer",
                "company": "StartUp Inc",
                "location": "New York, NY",
                "description": "Seeking a talented React developer for our innovative web platform. Experience with TypeScript and Vite is a plus. 3+ years required.",
                "url": "https://example.com/job/2",
                "diploma": "Bachelor's Degree",
                "experience": "3+ years",
                "posted_date": datetime.now() - timedelta(days=5)
            },
            {
                "title": "Full Stack Developer",
                "company": "Enterprise Solutions",
                "location": "Remote",
                "description": "Join our team as a Full Stack Developer. Work with Python backend and React frontend. Must have 3+ years of experience and a degree in related field.",
                "url": "https://example.com/job/3",
                "diploma": "Bachelor's Degree",
                "experience": "3+ years",
                "posted_date": datetime.now() - timedelta(days=1)
            },
            {
                "title": "DevOps Engineer",
                "company": "Cloud Systems Ltd",
                "location": "Austin, TX",
                "description": "Looking for a DevOps Engineer experienced with Docker, Kubernetes, and CI/CD pipelines. Master's degree preferred, minimum 4 years experience.",
                "url": "https://example.com/job/4",
                "diploma": "Master's Degree",
                "experience": "4+ years",
                "posted_date": datetime.now() - timedelta(days=3)
            },
            {
                "title": "Junior Python Developer",
                "company": "Learning Labs",
                "location": "Boston, MA",
                "description": "Great opportunity for junior developers to grow. We provide mentorship and training in Python web development. High school diploma required, 1-2 years experience preferred.",
                "url": "https://example.com/job/5",
                "diploma": "High School Diploma",
                "experience": "1-2 years",
                "posted_date": datetime.now() - timedelta(days=7)
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
                    posted_date=j.get("posted_date"),
                    diploma_required=j.get("diploma"),
                    years_experience=j.get("experience")
                ))
        
        return results
