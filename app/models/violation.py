from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import ViolationTypeEnum, SubjectTypeEnum

if TYPE_CHECKING:
    from app.models.gate import Gate
    from app.models.student import Student
    from app.models.staff import StaffMember
    from app.models.visitor import Visitor
    from app.models.security_staff import SecurityStaff
    from app.models.fail_attempt import FailAttempt

class Violation(SQLModel, table=True):
    __tablename__ = "violations"
    
    id: str = Field(primary_key=True)
    type: ViolationTypeEnum = Field(index=True)
    subject_type: Optional[SubjectTypeEnum] = Field(default=None, index=True)
    student_id: Optional[str] = Field(default=None, foreign_key="students.id")
    staff_id: Optional[str] = Field(default=None, foreign_key="staff_members.id")
    visitor_id: Optional[str] = Field(default=None, foreign_key="visitors.id")
    gate_id: str = Field(foreign_key="gates.id", index=True)
    occurred_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    details: Optional[str] = Field(default=None)
    scanned_qr_code: Optional[str] = None
    qr_hash: Optional[str] = Field(default=None)
    captured_image_url: Optional[str] = None
    captured_image_path: Optional[str] = Field(default=None)
    confidence_score: Optional[float] = None
    resolved: bool = Field(default=False, index=True)
    resolved_at: Optional[datetime] = None
    resolved_by_staff_id: Optional[str] = Field(default=None, foreign_key="security_staff.id")
    resolution_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    gate: "Gate" = Relationship(back_populates="violations")
    student: Optional["Student"] = Relationship(
        back_populates="violations",
        sa_relationship_kwargs={"foreign_keys": "Violation.student_id"}
    )
    staff_member: Optional["StaffMember"] = Relationship(
        back_populates="violations",
        sa_relationship_kwargs={"foreign_keys": "Violation.staff_id"}
    )
    visitor: Optional["Visitor"] = Relationship(
        back_populates="violations",
        sa_relationship_kwargs={"foreign_keys": "Violation.visitor_id"}
    )
    resolved_by: Optional["SecurityStaff"] = Relationship(back_populates="resolved_violations")
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="violation")
