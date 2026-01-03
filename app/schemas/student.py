from typing import Optional
from pydantic import BaseModel, Field

class SubjectStudent(BaseModel):
    id: str
    name: str
    photoUrl: Optional[str]
    department: Optional[str]
    enrollmentStatus: str

class EnrollPhotoRequest(BaseModel):
    studentId: str = Field(..., description="Student ID")
    photo: str = Field(..., description="Base64 encoded image string (data:image/jpeg;base64,...)")

class EnrollPhotoResponse(BaseModel):
    studentId: str
    photoUrl: str
