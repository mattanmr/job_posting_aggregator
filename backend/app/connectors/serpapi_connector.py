"""
SerpAPI Google Jobs Connector
Documentation: https://serpapi.com/google-jobs-api
"""
import os
import requests
from typing import List, Optional
from datetime import datetime
from .base import JobConnector, JobPosting


class SerpAPIJobsConnector(JobConnector):
    """Connector for SerpAPI Google Jobs API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SerpAPI connector
        
        Args:
            api_key: SerpAPI API key. If not provided, will try to get from environment variable SERPAPI_KEY
        """
        self.api_key = api_key or os.getenv('SERPAPI_KEY')
        self.base_url = 'https://serpapi.com/search.json'
        
    def search(
        self, 
        query: str, 
        location: Optional[str] = None,
        google_domain: str = 'google.com',
        gl: str = 'us',
        hl: str = 'en',
        lrad: Optional[int] = None,
        chips: Optional[str] = None,
        **kwargs
    ) -> List[JobPosting]:
        """
        Search for jobs using SerpAPI Google Jobs
        
        Args:
            query: Search keywords (required)
            location: Geographic location for the search
            google_domain: Google domain to use (default: google.com)
            gl: Country code (e.g., 'us', 'uk', 'il')
            hl: Language code (e.g., 'en', 'es', 'he')
            lrad: Search radius in kilometers
            chips: Additional query conditions (e.g., city, job type filters)
            **kwargs: Additional parameters supported by SerpAPI
            
        Returns:
            List of JobPosting objects
        """
        if not self.api_key:
            raise ValueError("SerpAPI key is required. Set SERPAPI_KEY environment variable or pass api_key parameter.")
        
        # Build request parameters
        params = {
            'engine': 'google_jobs',
            'q': query,
            'api_key': self.api_key,
            'google_domain': google_domain,
            'gl': gl,
            'hl': hl,
        }
        
        # Add optional parameters
        if location:
            params['location'] = location
        if lrad:
            params['lrad'] = lrad
        if chips:
            params['chips'] = chips
            
        # Add any additional kwargs
        params.update(kwargs)
        
        try:
            # Make API request
            response = requests.get(
                url=self.base_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for errors
            if 'error' in data:
                print(f"SerpAPI error: {data['error']}")
                return []
            
            # Parse job results
            jobs_results = data.get('jobs_results', [])
            return [self._parse_job(job) for job in jobs_results]
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching jobs from SerpAPI: {e}")
            return []
    
    def _parse_job(self, job_data: dict) -> JobPosting:
        """Convert SerpAPI job data to JobPosting object"""
        
        # Extract salary from extensions if available
        salary_str = None
        detected_extensions = job_data.get('detected_extensions', {})
        
        # Try to build salary string from extensions
        schedule_type = detected_extensions.get('schedule_type', '')
        if schedule_type:
            salary_str = schedule_type
        
        # Get description (truncate if too long)
        description = job_data.get('description', '')
        if len(description) > 500:
            description = description[:500] + '...'
        
        # Parse posted date from extensions
        posted_date = None
        posted_at = detected_extensions.get('posted_at')
        if posted_at:
            # posted_at is usually a string like "2 days ago", "1 week ago", etc.
            # We'll keep it as string in the description for now
            pass
        
        # Get location
        location = job_data.get('location', 'N/A')
        
        # Build a more complete description with job highlights
        full_description = description
        job_highlights = job_data.get('job_highlights', [])
        if job_highlights:
            full_description += '\n\n'
            for highlight in job_highlights[:2]:  # Limit to first 2 sections
                title = highlight.get('title', '')
                items = highlight.get('items', [])
                if items:
                    full_description += f"\n{title}:\n"
                    for item in items[:3]:  # Limit to 3 items per section
                        full_description += f"• {item}\n"
        
        # Get the actual job posting URL from apply_options (first one is usually the primary source)
        job_url = ''
        apply_options = job_data.get('apply_options', [])
        if apply_options and len(apply_options) > 0:
            job_url = apply_options[0].get('link', '')
        
        # Fallback to share_link if no apply options (though this is a Google Jobs link)
        if not job_url:
            job_url = job_data.get('share_link', '')
        
        return JobPosting(
            title=job_data.get('title', 'N/A'),
            company=job_data.get('company_name', 'N/A'),
            location=location,
            description=full_description.strip(),
            url=job_url,
            source='Google Jobs (via SerpAPI)',
            posted_date=posted_date,
            salary=salary_str
        )
