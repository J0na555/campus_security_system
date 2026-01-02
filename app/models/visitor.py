from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.staff import StaffMember
    from app.models.security_staff import SecurityStaff
    from app.models.violation import Violation
    from app.models.fail_attempt import FailAttempt

class Visitor(SQLModel, table=True):
    __tablename__ = "visitors"
    
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    email: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    purpose: str
    host_staff_id: str = Field(foreign_key="staff_members.id")
    qr_code: str = Field(unique=True, index=True)
    qr_code_image_url: Optional[str] = None
    valid_from: datetime
    valid_until: datetime
    allowed_gates: Optional[str] = Field(default=None)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_staff_id: str = Field(foreign_key="security_staff.id")
    
    host: "StaffMember" = Relationship(back_populates="hosted_visitors")
    created_by: "SecurityStaff" = Relationship(back_populates="created_visitors")
    violations: list["Violation"] = Relationship(
        back_populates="visitor",
        sa_relationship_kwargs={"foreign_keys": "Violation.visitor_id"}
    )
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="visitor")
