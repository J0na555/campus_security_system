from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import EmploymentStatusEnum

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.violation import Violation
    from app.models.fail_attempt import FailAttempt
    from app.models.visitor import Visitor

class StaffMember(SQLModel, table=True):
    __tablename__ = "staff_members"
    
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    photo_url: Optional[str] = None
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    position: Optional[str] = None
    employment_status: EmploymentStatusEnum = Field(default=EmploymentStatusEnum.ACTIVE)
    qr_code: str = Field(unique=True, index=True)
    hired_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    department: Optional["Department"] = Relationship(back_populates="staff_members")
    violations: list["Violation"] = Relationship(
        back_populates="staff_member",
        sa_relationship_kwargs={"foreign_keys": "Violation.staff_id"}
    )
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="staff_member")
    hosted_visitors: list["Visitor"] = Relationship(back_populates="host")
