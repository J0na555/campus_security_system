from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
import uuid

from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import EnrollmentStatusEnum

if TYPE_CHECKING:
    from app.models.department import Department
    from app.models.violation import Violation
    from app.models.fail_attempt import FailAttempt


def utc_now():
    return datetime.now(timezone.utc)


class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)

    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)

    photo_url: Optional[str] = None

    department_id: Optional[int] = Field(default=None, foreign_key="departments.id")

    enrollment_status: EnrollmentStatusEnum = Field(
        default=EnrollmentStatusEnum.ACTIVE
    )

    qr_code: str = Field(unique=True, index=True)

    enrolled_at: datetime = Field(default_factory=utc_now)
    created_at: datetime = Field(default_factory=utc_now)

    updated_at: datetime = Field(default_factory=utc_now)

    department: Optional["Department"] = Relationship(back_populates="students")

    violations: list["Violation"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"foreign_keys": "Violation.student_id"}
    )

    fail_attempts: list["FailAttempt"] = Relationship(back_populates="student")