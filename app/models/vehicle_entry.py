from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import VehicleEntryStatusEnum

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle

class VehicleEntry(SQLModel, table=True):
    __tablename__ = "vehicle_entries"
    
    id: int = Field(default=None, primary_key=True)
    license_plate: str = Field(index=True)
    vehicle_id: Optional[int] = Field(default=None, foreign_key="vehicles.id")
    entry_time: datetime = Field(default_factory=datetime.utcnow, index=True)
    exit_time: Optional[datetime] = Field(default=None, index=True)
    entry_image_path: Optional[str] = Field(default=None)
    exit_image_path: Optional[str] = Field(default=None)
    status: VehicleEntryStatusEnum = Field(default=VehicleEntryStatusEnum.ENTERED, index=True)
    gate_id: Optional[str] = Field(default=None)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    vehicle: Optional["Vehicle"] = Relationship(back_populates="vehicle_entries")
