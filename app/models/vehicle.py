from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import OwnerTypeEnum, VehicleTypeEnum

if TYPE_CHECKING:
    from app.models.vehicle_entry import VehicleEntry

class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicles"
    
    id: int = Field(default=None, primary_key=True)
    license_plate: str = Field(unique=True, index=True)
    owner_type: OwnerTypeEnum = Field(index=True)
    owner_id: Optional[str] = Field(default=None)
    owner_name: str
    vehicle_type: VehicleTypeEnum = Field(default=VehicleTypeEnum.CAR)
    color: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    vehicle_entries: list["VehicleEntry"] = Relationship(back_populates="vehicle")
