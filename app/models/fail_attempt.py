from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import SubjectTypeEnum

if TYPE_CHECKING:
    from app.models.gate import Gate
    from app.models.student import Student
    from app.models.staff import StaffMember
    from app.models.visitor import Visitor
    from app.models.violation import Violation

class FailAttempt(SQLModel, table=True):
    __tablename__ = "fail_attempts"
    
    id: int = Field(default=None, primary_key=True)
    subject_type: SubjectTypeEnum = Field(index=True)
    student_id: Optional[str] = Field(default=None, foreign_key="students.id")
    staff_id: Optional[str] = Field(default=None, foreign_key="staff_members.id")
    visitor_id: Optional[str] = Field(default=None, foreign_key="visitors.id")
    gate_id: str = Field(foreign_key="gates.id", index=True)
    attempted_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    captured_image_url: Optional[str] = None
    confidence_score: Optional[float] = None
    violation_id: Optional[str] = Field(default=None, foreign_key="violations.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    gate: "Gate" = Relationship(back_populates="fail_attempts")
    student: Optional["Student"] = Relationship(back_populates="fail_attempts")
    staff_member: Optional["StaffMember"] = Relationship(back_populates="fail_attempts")
    visitor: Optional["Visitor"] = Relationship(back_populates="fail_attempts")
    violation: Optional["Violation"] = Relationship(back_populates="fail_attempts")
