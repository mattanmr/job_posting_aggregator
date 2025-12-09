from typing import List, Dict, Any

class BaseConnector:
    """Base class for job source connectors."""
    
    def search(self, q: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search for jobs. Must be implemented by subclasses."""
        raise NotImplementedError
