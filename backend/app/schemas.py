from pydantic import BaseModel
from typing import Optional, Any

class JobOut(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    post_date: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    raw: Optional[Any] = None
