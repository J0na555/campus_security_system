from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    employeeId: str
    password: str

class UserInfo(BaseModel):
    id: str
    employeeId: str
    name: str
    email: str
    role: str
    department: Optional[str] = None
    createdAt: Optional[datetime] = None
    lastLoginAt: Optional[datetime] = None

class LoginResponse(BaseModel):
    token: str
    expiresAt: datetime
    user: UserInfo
