from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.student import Student
    from app.models.staff import StaffMember

class Department(SQLModel, table=True):
    __tablename__ = "departments"
    
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    code: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    students: list["Student"] = Relationship(back_populates="department")
    staff_members: list["StaffMember"] = Relationship(back_populates="department")
