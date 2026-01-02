from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import UserRoleEnum

if TYPE_CHECKING:
    from app.models.visitor import Visitor
    from app.models.violation import Violation

class SecurityStaff(SQLModel, table=True):
    __tablename__ = "security_staff"
    
    id: str = Field(primary_key=True)
    employee_id: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: UserRoleEnum = Field(default=UserRoleEnum.SECURITY_OFFICER)
    department: str = Field(default="Campus Security")
    is_active: bool = Field(default=True)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    created_visitors: list["Visitor"] = Relationship(back_populates="created_by")
    resolved_violations: list["Violation"] = Relationship(back_populates="resolved_by")
