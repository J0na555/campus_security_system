from typing import Optional
from pydantic import BaseModel

class SubjectStaff(BaseModel):
    id: str
    name: str
    photoUrl: Optional[str]
    department: Optional[str]
    position: Optional[str]
    employmentStatus: str
