from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.common import PaginationInfo

class ViolationSubject(BaseModel):
    id: str
    name: str
    photoUrl: Optional[str]

class ViolationResolvedBy(BaseModel):
    id: str
    name: str

class ViolationItem(BaseModel):
    id: str
    type: str
    subjectType: Optional[str]
    subject: Optional[ViolationSubject]
    gateId: str
    gateName: str
    occurredAt: datetime
    details: dict
    resolved: bool
    resolvedAt: Optional[datetime]
    resolvedBy: Optional[ViolationResolvedBy]
    notes: Optional[str]

class ViolationsListResponse(BaseModel):
    violations: List[ViolationItem]
    pagination: PaginationInfo
