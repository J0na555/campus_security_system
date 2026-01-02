from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.common import PaginationInfo
from app.schemas.vehicle import VehicleInfo

class VehicleEntryRequest(BaseModel):
    licensePlate: str = Field(description="License plate number")
    gateId: Optional[str] = None
    entryImagePath: Optional[str] = None
    timestamp: datetime

class VehicleExitRequest(BaseModel):
    licensePlate: str = Field(description="License plate number")
    gateId: Optional[str] = None
    exitImagePath: Optional[str] = None
    timestamp: datetime

class VehicleEntryResponse(BaseModel):
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
    entryId: int
    licensePlate: str
    entryTime: datetime
    exitTime: datetime
    duration: str
    status: str
    message: str

class VehicleEntryInfo(BaseModel):
    id: int
    licensePlate: str
    vehicleId: Optional[int]
    entryTime: datetime
    exitTime: Optional[datetime]
    status: str
    gateId: Optional[str]
    vehicle: Optional[VehicleInfo] = None

class VehicleEntryListResponse(BaseModel):
    entries: List[VehicleEntryInfo]
    pagination: PaginationInfo
