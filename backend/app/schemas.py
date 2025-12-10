from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class JobOut(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    post_date: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    diploma_required: Optional[str] = None
    years_experience: Optional[str] = None
    raw: Optional[Any] = None


class KeywordRequest(BaseModel):
    keyword: str


class KeywordResponse(BaseModel):
    keywords: list[str]


class CsvFileInfo(BaseModel):
    filename: str
    timestamp: str
    size: int
    job_count: int


class CollectionStatus(BaseModel):
    next_collection_timestamp: str
    next_collection_time: str
    last_collection_timestamp: Optional[str] = None
    last_collection_time: Optional[str] = None


class ScheduleConfigRequest(BaseModel):
    interval_hours: int


class ScheduleConfigResponse(BaseModel):
    interval_hours: int
    min_interval: int = 1
    max_interval: int = 168