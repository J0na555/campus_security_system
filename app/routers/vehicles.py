from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.core.database import get_session
from app.services.auth_service import AuthService
from app.services.vehicle_service import VehicleService
from app.services.vehicle_entry_service import VehicleEntryService
from app.services.vehicle_alert_service import VehicleAlertService
from app.schemas.vehicle import RegisterVehicleRequest, VehicleListResponse, VehicleAlertListResponse
from app.schemas.vehicle_entry import VehicleEntryRequest, VehicleExitRequest, VehicleEntryResponse, VehicleExitResponse, VehicleEntryListResponse
from app.schemas.common import SuccessResponse
from app.models.security_staff import SecurityStaff

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.post("/entry", response_model=SuccessResponse)
async def entry(data: VehicleEntryRequest, session: Session = Depends(get_session)):
    entry, vehicle, alert = await VehicleEntryService.log_entry(session, data)
    res = VehicleEntryResponse(entryId=entry.id, licensePlate=entry.license_plate, vehicleId=entry.vehicle_id, registered=vehicle is not None, entryTime=entry.entry_time, status=entry.status.value, alertCreated=alert["created"], alertId=alert["id"], message=alert["message"])
    return {"status": "success", "data": res.model_dump()}

@router.post("/exit", response_model=SuccessResponse)
async def exit(data: VehicleExitRequest, session: Session = Depends(get_session)):
    entry = await VehicleEntryService.log_exit(session, data)
    if not entry: return {"status": "error", "code": "NO_ENTRY_FOUND", "message": "No entry found"}
    duration = f"{int((entry.exit_time - entry.entry_time).total_seconds() // 3600)}h {int(((entry.exit_time - entry.entry_time).total_seconds() % 3600) // 60)}m"
    res = VehicleExitResponse(entryId=entry.id, licensePlate=entry.license_plate, entryTime=entry.entry_time, exitTime=entry.exit_time, duration=duration, status=entry.status.value, message="Exit logged")
    return {"status": "success", "data": res.model_dump()}

@router.post("", response_model=SuccessResponse, status_code=201)
async def register(data: RegisterVehicleRequest, session: Session = Depends(get_session), user: SecurityStaff = Depends(AuthService.get_current_user)):
    v = VehicleService.register(session, data)
    return {"status": "success", "data": VehicleService.get_vehicle_info(v).model_dump()}

@router.get("", response_model=SuccessResponse)
async def list_vehicles(session: Session = Depends(get_session), user: SecurityStaff = Depends(AuthService.get_current_user)):
    vehicles = VehicleService.list_vehicles(session)
    data = [VehicleService.get_vehicle_info(v).model_dump() for v in vehicles]
    return {"status": "success", "data": {"vehicles": data, "total": len(data)}}

@router.get("/alerts", response_model=SuccessResponse)
async def list_alerts(page: int = 1, limit: int = 20, alertType: str = None, resolved: bool = None, session: Session = Depends(get_session), user: SecurityStaff = Depends(AuthService.get_current_user)):
    alerts, pagination = VehicleAlertService.list_alerts(session, page, limit, alertType, resolved)
    data = []
    for a in alerts:
        data.append({
            "id": a.id,
            "licensePlate": a.license_plate,
            "timestamp": a.timestamp,
            "alertType": a.alert_type.value if hasattr(a.alert_type, 'value') else a.alert_type,
            "gateId": a.gate_id,
            "resolved": a.resolved,
            "resolvedAt": a.resolved_at,
            "notes": a.resolution_notes
        })
    return {"status": "success", "data": {"alerts": data, "pagination": pagination.model_dump()}}
