from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

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

class CreateStudentRequest(BaseModel):
    name: str = Field(..., description="Full name of the student")
    email: EmailStr = Field(..., description="Student's email address")
    departmentId: Optional[int] = Field(None, description="Department ID")
    qrCode: Optional[str] = Field(None, description="QR code (auto-generated if not provided)")
    photo: Optional[str] = Field(None, description="Base64 encoded image (optional)")

class UpdateStudentRequest(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the student")
    email: Optional[EmailStr] = Field(None, description="Student's email address")
    departmentId: Optional[int] = Field(None, description="Department ID")
    qrCode: Optional[str] = Field(None, description="QR code")
    enrollmentStatus: Optional[str] = Field(None, description="Enrollment status (active/suspended/graduated)")

class StudentResponse(BaseModel):
    id: str
    name: str
    email: str
    photoUrl: Optional[str]
    departmentId: Optional[int]
    department: Optional[str]
    enrollmentStatus: str
    qrCode: str
    enrolledAt: datetime
    createdAt: datetime
    updatedAt: datetime
