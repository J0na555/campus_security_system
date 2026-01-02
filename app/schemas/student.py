from typing import Optional
from pydantic import BaseModel

class SubjectStudent(BaseModel):
    id: str
    name: str
    photoUrl: Optional[str]
    department: Optional[str]
    enrollmentStatus: str
