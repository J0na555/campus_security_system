from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import GateStatusEnum

if TYPE_CHECKING:
    from app.models.violation import Violation
    from app.models.fail_attempt import FailAttempt

class Gate(SQLModel, table=True):
    __tablename__ = "gates"
    
    id: str = Field(primary_key=True)
    name: str = Field(index=True)
    location: str
    status: GateStatusEnum = Field(default=GateStatusEnum.ONLINE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    violations: list["Violation"] = Relationship(back_populates="gate")
    fail_attempts: list["FailAttempt"] = Relationship(back_populates="gate")
