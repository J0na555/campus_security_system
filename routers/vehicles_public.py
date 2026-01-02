"""
Vehicle tracking API endpoints
Public endpoints for gate cameras - no authentication required
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database import get_session
from schemas import (
    VehicleEntryRequest, VehicleExitRequest,
    VehicleEntryResponse, VehicleExitResponse,
    SuccessResponse
)
from models import Vehicle, VehicleEntry, VehicleAlert, VehicleEntryStatusEnum, VehicleAlertTypeEnum
import json

router = APIRouter(prefix="/vehicle", tags=["Vehicle Tracking"])


@router.post("/entry", response_model=SuccessResponse)
async def log_vehicle_entry(
    entry_data: VehicleEntryRequest,
    session: Session = Depends(get_session)
):
    """
    Log vehicle entry via license plate scan
    
    Public endpoint - no authentication required
    ALL vehicle entries are logged (unlike pedestrian entries)
    Creates alert if vehicle is not registered
    """
    license_plate = entry_data.licensePlate.upper().strip()
    
    # Check if vehicle is registered
    statement = select(Vehicle).where(Vehicle.license_plate == license_plate)
    vehicle = session.exec(statement).first()
    
    # Create vehicle entry record (logged for ALL vehicles)
    vehicle_entry = VehicleEntry(
        license_plate=license_plate,
        vehicle_id=vehicle.id if vehicle else None,
        entry_time=entry_data.timestamp,
        entry_image_path=entry_data.entryImagePath,
        status=VehicleEntryStatusEnum.ENTERED,
        gate_id=entry_data.gateId
    )
    session.add(vehicle_entry)
    session.commit()
    session.refresh(vehicle_entry)
    
    # Create alert if vehicle is not registered
    alert_created = False
    alert_id = None
    message = "Vehicle entry logged successfully"
    
    if not vehicle:
        # Unknown vehicle - create alert
        alert = VehicleAlert(
            license_plate=license_plate,
            timestamp=entry_data.timestamp,
            alert_type=VehicleAlertTypeEnum.UNKNOWN_VEHICLE,
            captured_image_path=entry_data.entryImagePath,
            gate_id=entry_data.gateId,
            details=json.dumps({
                "reason": "Vehicle not registered in system",
                "entryId": vehicle_entry.id
            })
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)
        
        alert_created = True
        alert_id = alert.id
        message = "Unknown vehicle - alert created"
        
        # TODO: Broadcast to WebSocket
    
    response_data = VehicleEntryResponse(
        entryId=vehicle_entry.id,
        licensePlate=license_plate,
        vehicleId=vehicle.id if vehicle else None,
        registered=vehicle is not None,
        entryTime=vehicle_entry.entry_time,
        status=vehicle_entry.status.value,
        alertCreated=alert_created,
        alertId=alert_id,
        message=message
    )
    
    return {
        "status": "success",
        "data": response_data.model_dump()
    }


@router.post("/exit", response_model=SuccessResponse)
async def log_vehicle_exit(
    exit_data: VehicleExitRequest,
    session: Session = Depends(get_session)
):
    """
    Log vehicle exit
    
    Public endpoint - no authentication required
    Updates the most recent entry record with exit time
    Creates alert if no matching entry found
    """
    license_plate = exit_data.licensePlate.upper().strip()
    
    # Find the most recent entry without an exit time
    statement = (
        select(VehicleEntry)
        .where(VehicleEntry.license_plate == license_plate)
        .where(VehicleEntry.exit_time.is_(None))
        .order_by(VehicleEntry.entry_time.desc())
    )
    vehicle_entry = session.exec(statement).first()
    
    if not vehicle_entry:
        # No matching entry found - create alert
        alert = VehicleAlert(
            license_plate=license_plate,
            timestamp=exit_data.timestamp,
            alert_type=VehicleAlertTypeEnum.VEHICLE_MISMATCH,
            captured_image_path=exit_data.exitImagePath,
            gate_id=exit_data.gateId,
            details=json.dumps({
                "reason": "Exit without entry - no matching entry record found"
            })
        )
        session.add(alert)
        session.commit()
        
        # TODO: Broadcast to WebSocket
        
        return {
            "status": "error",
            "code": "NO_ENTRY_FOUND",
            "message": f"No entry record found for license plate {license_plate}"
        }
    
    # Update entry with exit time
    vehicle_entry.exit_time = exit_data.timestamp
    vehicle_entry.exit_image_path = exit_data.exitImagePath
    vehicle_entry.status = VehicleEntryStatusEnum.EXITED
    vehicle_entry.updated_at = datetime.utcnow()
    
    session.add(vehicle_entry)
    session.commit()
    session.refresh(vehicle_entry)
    
    # Calculate duration
    duration = vehicle_entry.exit_time - vehicle_entry.entry_time
    hours = int(duration.total_seconds() // 3600)
    minutes = int((duration.total_seconds() % 3600) // 60)
    duration_str = f"{hours}h {minutes}m"
    
    response_data = VehicleExitResponse(
        entryId=vehicle_entry.id,
        licensePlate=license_plate,
        entryTime=vehicle_entry.entry_time,
        exitTime=vehicle_entry.exit_time,
        duration=duration_str,
        status=vehicle_entry.status.value,
        message="Vehicle exit logged successfully"
    )
    
    return {
        "status": "success",
        "data": response_data.model_dump()
    }
