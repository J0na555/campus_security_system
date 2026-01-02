from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

class SubjectVisitor(BaseModel):
    id: str
    name: str
    photoUrl: Optional[str]
    purpose: str
    hostName: str
    hostDepartment: Optional[str]
    validFrom: datetime
    validUntil: datetime

class CreateVisitorPassRequest(BaseModel):
    visitorName: str
    visitorEmail: Optional[EmailStr] = None
    visitorPhone: Optional[str] = None
    purpose: str
    hostEmployeeId: str
    validFrom: datetime
    validUntil: datetime
    allowedGates: Optional[List[str]] = None
    notes: Optional[str] = None

class GateInfo(BaseModel):
    id: str
    name: str

class HostInfo(BaseModel):
    employeeId: str
    name: str
    department: Optional[str]
    email: str

class QRCodeInfo(BaseModel):
    content: str
    imageUrl: str
    imageBase64: str

class CreatedByInfo(BaseModel):
    id: str
    name: str

class VisitorPassResponse(BaseModel):
    passId: str
    visitorName: str
    visitorEmail: Optional[str]
    visitorPhone: Optional[str]
    purpose: str
    host: HostInfo
    validFrom: datetime
    validUntil: datetime
    allowedGates: List[GateInfo]
    qrCode: QRCodeInfo
    createdAt: datetime
    createdBy: CreatedByInfo
