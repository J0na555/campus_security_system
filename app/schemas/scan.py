from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class QRScanRequest(BaseModel):
    qrCode: str
    gateId: str
    scanTimestamp: datetime

class QRScanResponseValid(BaseModel):
    valid: bool = True
    subjectType: str
    subject: dict
    accessGranted: bool
    message: str
    requiresFaceVerification: bool

class QRScanResponseInvalid(BaseModel):
    valid: bool = False
    accessGranted: bool = False
    violationType: str
    message: str
    violationId: str
    subjectPersisted: bool
    subject: Optional[dict] = None

class FaceVerifyRequest(BaseModel):
    subjectId: str
    subjectType: str
    faceImage: str = Field(description="Base64 encoded face image")
    gateId: str
    scanTimestamp: datetime

class FaceVerifyResponseSuccess(BaseModel):
    verified: bool = True
    confidence: float
    accessGranted: bool = True
    message: str = "Face verification successful"

class FaceVerifyResponseFailed(BaseModel):
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
