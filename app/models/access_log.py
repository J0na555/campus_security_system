from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.enums import SubjectTypeEnum

class AccessLog(SQLModel, table=True):
    __tablename__ = "access_logs"
    
    id: int = Field(default=None, primary_key=True)
    subject_type: SubjectTypeEnum = Field(index=True)
    subject_id: str = Field(index=True)
    gate_id: str = Field(index=True)
    accessed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    qr_code_used: str
    face_verified: bool = Field(default=False)
    face_confidence: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
