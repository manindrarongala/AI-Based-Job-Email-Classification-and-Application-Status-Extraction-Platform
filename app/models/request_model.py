"""Data models"""

from pydantic import BaseModel
from typing import Optional, List


class ScanEmailsRequest(BaseModel):
    """Request model for scanning emails"""
    email: str
    app_password: str


class JobEmailResult(BaseModel):
    """Step 13: Final result for a job-related email"""
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    subject: str
    body: Optional[str] = None


class ScanEmailsResponse(BaseModel):
    """Response model for email scanning (Step 13)"""
    total_emails: int
    job_related_count: int
    job_emails: List[JobEmailResult] = []


class ClassifiedEmail(BaseModel):
    """Single classified email"""
    subject: str
    body: str
    is_job_related: bool
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None


class EmailRequest(BaseModel):
    subject: str
    body: str


class ClassificationResponse(BaseModel):
    is_job_related: bool
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
