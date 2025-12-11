"""
SerpAPI Google Jobs Connector
Documentation: https://serpapi.com/google-jobs-api
"""
import os
import re
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
    
    @staticmethod
    def _extract_education(text: str) -> Optional[str]:
        """Extract education/diploma requirements from job description."""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Patterns for education requirements
        education_patterns = [
            (r"(phd|ph\.d\.|doctorate|doctoral)", "PhD/Doctorate"),
            (r"(master'?s?|msc|m\.s\.|graduate degree)", "Master's Degree"),
            (r"(bachelor'?s?|bs|b\.s\.|ba|b\.a\.|undergraduate degree|college degree)", "Bachelor's Degree"),
            (r"(associate'?s?|aa|a\.a\.|as|a\.s\.)", "Associate's Degree"),
            (r"(high school|secondary school|diploma|ged)", "High School Diploma"),
        ]
        
        for pattern, degree in education_patterns:
            if re.search(pattern, text_lower):
                return degree
        
        return None
    
    @staticmethod
    def _extract_experience(text: str) -> Optional[str]:
        """Extract years of experience requirements from job description."""
        if not text:
            return None
        
        # Patterns for experience requirements
        patterns = [
            r"(\d+)\+?\s*(?:to|\-|or)\s*(\d+)\+?\s*years?",  # "3-5 years" or "3 to 5 years"
            r"(\d+)\+?\s*years?",  # "3 years" or "3+ years"
            r"minimum\s+of\s+(\d+)\+?\s*years?",  # "minimum of 3 years"
            r"at least\s+(\d+)\+?\s*years?",  # "at least 3 years"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                groups = match.groups()
                if len(groups) == 2 and groups[1]:
                    # Range found
                    return f"{groups[0]}-{groups[1]} years"
                else:
                    # Single number found
                    return f"{groups[0]}+ years"
        
        return None
        
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
            # Try to parse posted_at string (format: "2024-01-15" or relative like "2 days ago")
            try:
                # Try ISO format first
                if 'T' in posted_at or len(posted_at) == 10:  # ISO format or YYYY-MM-DD
                    posted_date = datetime.fromisoformat(posted_at.split('T')[0]) if 'T' in posted_at else datetime.strptime(posted_at, '%Y-%m-%d')
                else:
                    # Try to parse relative dates like "2 days ago", "1 day ago", "Posted today", etc.
                    from datetime import timedelta
                    posted_lower = posted_at.lower()
                    now = datetime.now()
                    
                    if 'today' in posted_lower or 'just now' in posted_lower:
                        posted_date = now
                    elif 'yesterday' in posted_lower:
                        posted_date = now - timedelta(days=1)
                    elif 'day' in posted_lower:
                        # Extract number of days
                        match = re.search(r'(\d+)\s*day', posted_lower)
                        if match:
                            days = int(match.group(1))
                            posted_date = now - timedelta(days=days)
                    elif 'week' in posted_lower:
                        # Extract number of weeks
                        match = re.search(r'(\d+)\s*week', posted_lower)
                        if match:
                            weeks = int(match.group(1))
                            posted_date = now - timedelta(weeks=weeks)
                    elif 'month' in posted_lower:
                        # Extract number of months (approximate as 30 days)
                        match = re.search(r'(\d+)\s*month', posted_lower)
                        if match:
                            months = int(match.group(1))
                            posted_date = now - timedelta(days=months*30)
            except (ValueError, AttributeError):
                posted_date = None
        
        # If no posted_date, try to extract from job_date_posted field if available
        if not posted_date and 'job_date_posted' in job_data:
            try:
                posted_date = datetime.fromisoformat(job_data['job_date_posted'])
            except (ValueError, AttributeError):
                posted_date = None
        
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
        
        # Extract education and experience requirements
        full_text = f"{full_description} {job_data.get('title', '')} {' '.join([h.get('title', '') + ' ' + ' '.join(h.get('items', [])) for h in job_highlights])}"
        diploma = self._extract_education(full_text)
        experience = self._extract_experience(full_text)
        
        return JobPosting(
            title=job_data.get('title', 'N/A'),
            company=job_data.get('company_name', 'N/A'),
            location=location,
            description=full_description.strip(),
            url=job_url,
            source='Google Jobs (via SerpAPI)',
            posted_date=posted_date,
            salary=salary_str,
            diploma_required=diploma,
            years_experience=experience
        )
