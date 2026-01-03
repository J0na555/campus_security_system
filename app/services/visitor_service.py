import json
from datetime import datetime, timedelta, timezone
from typing import List
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.visitor import Visitor
from app.models.staff import StaffMember
from app.models.gate import Gate
from app.models.security_staff import SecurityStaff
from app.schemas.visitor import CreateVisitorPassRequest, VisitorPassResponse, HostInfo, GateInfo, QRCodeInfo, CreatedByInfo
from app.utils.ids import generate_pass_id

class VisitorService:
    @staticmethod
    def create_pass(session: Session, pass_data: CreateVisitorPassRequest, user: SecurityStaff):
        VisitorService._validate_pass_data(session, pass_data)
        visitor_id = generate_pass_id()
        qr_code = f"QR-VIS-2026-{visitor_id.upper()}"
        
        visitor = Visitor(
            id=visitor_id, name=pass_data.visitorName, email=pass_data.visitorEmail,
            phone=pass_data.visitorPhone, purpose=pass_data.purpose,
            photo_url=pass_data.visitorPhoto,  # Save the visitor photo
            host_staff_id=pass_data.hostEmployeeId, qr_code=qr_code,
            valid_from=pass_data.validFrom, valid_until=pass_data.validUntil,
            allowed_gates=json.dumps(pass_data.allowedGates) if pass_data.allowedGates else None,
            notes=pass_data.notes, created_by_staff_id=user.id
        )
        session.add(visitor)
        session.commit()
        session.refresh(visitor)
        return VisitorService._build_pass_response(session, visitor, user, qr_code, pass_data.allowedGates)

    @staticmethod
    def _validate_pass_data(session: Session, data: CreateVisitorPassRequest):
        errors = []
        utc_now = datetime.now(timezone.utc)  # Use timezone-aware datetime

        if data.validUntil <= data.validFrom:
            errors.append({"field": "validUntil", "message": "End time must be after start time"})
        
        if data.validFrom < utc_now - timedelta(hours=1):
            errors.append({"field": "validFrom", "message": "Start time must be recent or future"})
        
        if data.validUntil - data.validFrom > timedelta(hours=24):
            errors.append({"field": "validUntil", "message": "Max duration 24h"})

        host = session.exec(select(StaffMember).where(StaffMember.id == data.hostEmployeeId)).first()

        if not host or host.employment_status.value != "active":
            errors.append({"field": "hostEmployeeId", "message": "Invalid or inactive host"})
        
        if errors:
            raise HTTPException(status_code=400, detail={"status": "error", "code": "VALIDATION_ERROR", "details": errors})

    @staticmethod
    def _build_pass_response(session: Session, visitor: Visitor, user: SecurityStaff, qr_code: str, allowed_gates):
        host = visitor.host
        host_info = HostInfo(
            employeeId=host.id, name=host.name, email=host.email,
            department=host.department.name if host.department else None
        )
        
        gates_info = []
        if allowed_gates:
            for g_id in allowed_gates:
                gate = session.get(Gate, g_id)
                if gate: gates_info.append(GateInfo(id=gate.id, name=gate.name))
        else:
            for gate in session.exec(select(Gate)).all():
                gates_info.append(GateInfo(id=gate.id, name=gate.name))

        return VisitorPassResponse(
            passId=visitor.id, visitorName=visitor.name, visitorEmail=visitor.email,
            visitorPhone=visitor.phone, visitorPhoto=visitor.photo_url, purpose=visitor.purpose, 
            host=host_info, validFrom=visitor.valid_from, validUntil=visitor.valid_until,
            allowedGates=gates_info, createdAt=visitor.created_at,
            qrCode=QRCodeInfo(content=qr_code, imageUrl="", imageBase64=""),
            createdBy=CreatedByInfo(id=user.id, name=user.name)
        )

    @staticmethod
    def list_passes(session: Session):
        # Simple query - relationships will be loaded lazily while session is active
        # The router accesses relationships immediately, so session should still be open
        return list(session.exec(select(Visitor).order_by(Visitor.created_at.desc())).all())
