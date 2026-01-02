from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.common import PaginationInfo
from app.schemas.violation import ViolationResolvedBy

class RegisterVehicleRequest(BaseModel):
    licensePlate: str
    ownerType: str
    ownerId: Optional[str] = None
    ownerName: str
    vehicleType: str = "car"
    color: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None

class VehicleInfo(BaseModel):
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

class VehicleAlertInfo(BaseModel):
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
    vehicles: List[VehicleInfo]
    total: int

class VehicleAlertListResponse(BaseModel):
    alerts: List[VehicleAlertInfo]
    pagination: PaginationInfo
