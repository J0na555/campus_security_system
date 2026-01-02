from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.enums import VehicleAlertTypeEnum

if TYPE_CHECKING:
    from app.models.security_staff import SecurityStaff

class VehicleAlert(SQLModel, table=True):
    __tablename__ = "vehicle_alerts"
    
    id: int = Field(default=None, primary_key=True)
    license_plate: str = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    alert_type: VehicleAlertTypeEnum = Field(index=True)
    captured_image_path: Optional[str] = Field(default=None)
    details: Optional[str] = Field(default=None)
    resolved: bool = Field(default=False, index=True)
    resolved_at: Optional[datetime] = None
    resolved_by_staff_id: Optional[str] = Field(default=None, foreign_key="security_staff.id")
    resolution_notes: Optional[str] = None
    gate_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    resolved_by: Optional["SecurityStaff"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "VehicleAlert.resolved_by_staff_id"}
    )
