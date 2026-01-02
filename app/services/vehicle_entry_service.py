import json
from datetime import datetime
from sqlmodel import Session, select
from app.models.vehicle import Vehicle
from app.models.vehicle_entry import VehicleEntry
from app.models.vehicle_alert import VehicleAlert
from app.models.enums import VehicleEntryStatusEnum, VehicleAlertTypeEnum
from app.schemas.vehicle_entry import VehicleEntryRequest, VehicleExitRequest
from app.services.alert_service import alert_service

class VehicleEntryService:
    @staticmethod
    async def log_entry(session: Session, data: VehicleEntryRequest):
        plate = data.licensePlate.upper().strip()
        vehicle = session.exec(select(Vehicle).where(Vehicle.license_plate == plate)).first()
        
        entry = VehicleEntry(
            license_plate=plate, vehicle_id=vehicle.id if vehicle else None,
            entry_time=data.timestamp, entry_image_path=data.entryImagePath,
            status=VehicleEntryStatusEnum.ENTERED, gate_id=data.gateId
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        
        alert_data = await VehicleEntryService._check_and_create_alert(session, vehicle, plate, data, entry.id)
        return entry, vehicle, alert_data

    @staticmethod
    async def _check_and_create_alert(session: Session, vehicle, plate, data, entry_id):
        if vehicle: return {"created": False, "id": None, "message": "Entry logged"}
        
        alert = VehicleAlert(
            license_plate=plate, timestamp=data.timestamp,
            alert_type=VehicleAlertTypeEnum.UNKNOWN_VEHICLE,
            captured_image_path=data.entryImagePath, gate_id=data.gateId,
            details=json.dumps({"reason": "Unregistered", "entryId": entry_id})
        )
        session.add(alert)
        session.commit()
        session.refresh(alert)
        await alert_service.broadcast_vehicle_alert({"id": alert.id, "plate": plate, "type": "unknown"})
        return {"created": True, "id": alert.id, "message": "Unknown vehicle - alert created"}

    @staticmethod
    async def log_exit(session: Session, data: VehicleExitRequest):
        plate = data.licensePlate.upper().strip()
        entry = session.exec(
            select(VehicleEntry).where(VehicleEntry.license_plate == plate, VehicleEntry.exit_time.is_(None))
            .order_by(VehicleEntry.entry_time.desc())
        ).first()
        
        if not entry:
            alert = VehicleAlert(
                license_plate=plate, timestamp=data.timestamp,
                alert_type=VehicleAlertTypeEnum.VEHICLE_MISMATCH,
                captured_image_path=data.exitImagePath, gate_id=data.gateId,
                details=json.dumps({"reason": "Exit without entry"})
            )
            session.add(alert)
            session.commit()
            await alert_service.broadcast_vehicle_alert({"id": alert.id, "plate": plate, "type": "mismatch"})
            return None
        
        entry.exit_time, entry.exit_image_path, entry.status = data.timestamp, data.exitImagePath, VehicleEntryStatusEnum.EXITED
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry
