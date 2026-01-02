"""
Pydantic schemas for request/response models
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from models import ViolationTypeEnum, SubjectTypeEnum, UserRoleEnum, VehicleTypeEnum, VehicleEntryStatusEnum, VehicleAlertTypeEnum, OwnerTypeEnum


# ============================================================================
# COMMON RESPONSE SCHEMAS
# ============================================================================

class SuccessResponse(BaseModel):
    """Standard success response wrapper"""
    status: str = "success"
    data: dict


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = "error"
    code: str
    message: str
    details: Optional[List[dict]] = None


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================

class LoginRequest(BaseModel):
    """Login request payload"""
    employeeId: str
    password: str


class UserInfo(BaseModel):
    """User information in responses"""
    id: str
    employeeId: str
    name: str
    email: str
    role: str
    department: Optional[str] = None
    createdAt: Optional[datetime] = None
    lastLoginAt: Optional[datetime] = None


class LoginResponse(BaseModel):
    """Login success response data"""
    token: str
    expiresAt: datetime
    user: UserInfo


# ============================================================================
# SUBJECT SCHEMAS
# ============================================================================

class SubjectStudent(BaseModel):
    """Student subject information"""
    id: str
    name: str
    photoUrl: Optional[str]
    department: Optional[str]
    enrollmentStatus: str


class SubjectStaff(BaseModel):
    """Staff subject information"""
    id: str
    name: str
    photoUrl: Optional[str]
    department: Optional[str]
    position: Optional[str]
    employmentStatus: str


class SubjectVisitor(BaseModel):
    """Visitor subject information"""
    id: str
    name: str
    photoUrl: Optional[str]
    purpose: str
    hostName: str
    hostDepartment: Optional[str]
    validFrom: datetime
    validUntil: datetime


# ============================================================================
# QR SCAN SCHEMAS
# ============================================================================

class QRScanRequest(BaseModel):
    """QR code scan request"""
    qrCode: str
    gateId: str
    scanTimestamp: datetime


class QRScanResponseValid(BaseModel):
    """QR scan response for valid codes"""
    valid: bool = True
    subjectType: str
    subject: dict
    accessGranted: bool
    message: str
    requiresFaceVerification: bool


class QRScanResponseInvalid(BaseModel):
    """QR scan response for invalid codes"""
    valid: bool = False
    accessGranted: bool = False
    violationType: str
    message: str
    violationId: str
    subjectPersisted: bool
    subject: Optional[dict] = None


# ============================================================================
# FACE VERIFICATION SCHEMAS
# ============================================================================

class FaceVerifyRequest(BaseModel):
    """Face verification request"""
    subjectId: str
    subjectType: str
    faceImage: str = Field(description="Base64 encoded face image")
    gateId: str
    scanTimestamp: datetime


class FaceVerifyResponseSuccess(BaseModel):
    """Face verification success response"""
    verified: bool = True
    confidence: float
    accessGranted: bool = True
    message: str = "Face verification successful"


class FaceVerifyResponseFailed(BaseModel):
    """Face verification failed response"""
    verified: bool = False
    confidence: Optional[float] = None
    accessGranted: bool = False
    violationType: str
    message: str
    violationId: str
    subjectPersisted: bool = True
    capturedImagePersisted: bool = True
    subject: dict
    lockoutUntil: Optional[datetime] = None
    failedAttemptCount: Optional[int] = None


# ============================================================================
# VIOLATION SCHEMAS
# ============================================================================

class ViolationSubject(BaseModel):
    """Subject information in violation response"""
    id: str
    name: str
    photoUrl: Optional[str]


class ViolationResolvedBy(BaseModel):
    """Resolver information"""
    id: str
    name: str


class ViolationItem(BaseModel):
    """Single violation item in list"""
    id: str
    type: str
    subjectType: Optional[str]
    subject: Optional[ViolationSubject]
    gateId: str
    gateName: str
    occurredAt: datetime
    details: dict
    resolved: bool
    resolvedAt: Optional[datetime]
    resolvedBy: Optional[ViolationResolvedBy]
    notes: Optional[str]


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    currentPage: int
    totalPages: int
    totalItems: int
    itemsPerPage: int
    hasNextPage: bool
    hasPreviousPage: bool


class ViolationsListResponse(BaseModel):
    """Violations list response data"""
    violations: List[ViolationItem]
    pagination: PaginationInfo


# ============================================================================
# VISITOR PASS SCHEMAS
# ============================================================================

class CreateVisitorPassRequest(BaseModel):
    """Create visitor pass request"""
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
    """Gate information"""
    id: str
    name: str


class HostInfo(BaseModel):
    """Host employee information"""
    employeeId: str
    name: str
    department: Optional[str]
    email: str


class QRCodeInfo(BaseModel):
    """QR code information"""
    content: str
    imageUrl: str
    imageBase64: str


class CreatedByInfo(BaseModel):
    """Created by information"""
    id: str
    name: str


class VisitorPassResponse(BaseModel):
    """Visitor pass creation response data"""
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


# ============================================================================
# VEHICLE SCHEMAS
# ============================================================================

class VehicleEntryRequest(BaseModel):
    """Vehicle entry request"""
    licensePlate: str = Field(description="License plate number")
    gateId: Optional[str] = None
    entryImagePath: Optional[str] = None
    timestamp: datetime


class VehicleExitRequest(BaseModel):
    """Vehicle exit request"""
    licensePlate: str = Field(description="License plate number")
    gateId: Optional[str] = None
    exitImagePath: Optional[str] = None
    timestamp: datetime


class VehicleEntryResponse(BaseModel):
    """Vehicle entry response"""
    entryId: int
    licensePlate: str
    vehicleId: Optional[int]
    registered: bool
    entryTime: datetime
    status: str
    alertCreated: bool = False
    alertId: Optional[int] = None
    message: str


class VehicleExitResponse(BaseModel):
    """Vehicle exit response"""
    entryId: int
    licensePlate: str
    entryTime: datetime
    exitTime: datetime
    duration: str
    status: str
    message: str


class RegisterVehicleRequest(BaseModel):
    """Register new vehicle request"""
    licensePlate: str
    ownerType: str
    ownerId: Optional[str] = None
    ownerName: str
    vehicleType: str = "car"
    color: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None


class VehicleInfo(BaseModel):
    """Vehicle information"""
    id: int
    licensePlate: str
    ownerType: str
    ownerId: Optional[str]
    ownerName: str
    vehicleType: str
    color: Optional[str]
    make: Optional[str]
    model: Optional[str]
    registeredAt: datetime


class VehicleEntryInfo(BaseModel):
    """Vehicle entry information"""
    id: int
    licensePlate: str
    vehicleId: Optional[int]
    entryTime: datetime
    exitTime: Optional[datetime]
    status: str
    gateId: Optional[str]
    vehicle: Optional[VehicleInfo] = None


class VehicleAlertInfo(BaseModel):
    """Vehicle alert information"""
    id: int
    licensePlate: str
    timestamp: datetime
    alertType: str
    gateId: Optional[str]
    resolved: bool
    resolvedAt: Optional[datetime]
    resolvedBy: Optional[ViolationResolvedBy]
    notes: Optional[str]


class VehicleListResponse(BaseModel):
    """List of vehicles response"""
    vehicles: List[VehicleInfo]
    total: int


class VehicleEntryListResponse(BaseModel):
    """List of vehicle entries response"""
    entries: List[VehicleEntryInfo]
    pagination: PaginationInfo


class VehicleAlertListResponse(BaseModel):
    """List of vehicle alerts response"""
    alerts: List[VehicleAlertInfo]
    pagination: PaginationInfo
