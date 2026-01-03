import json
from datetime import datetime
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.student import Student
from app.models.staff import StaffMember
from app.models.gate import Gate
from app.models.violation import Violation
from app.models.enums import ViolationTypeEnum
from app.utils.ids import generate_violation_id
from app.services.visitor_qr_service import VisitorQRService
from app.services.alert_service import alert_service

class QRService:
    @staticmethod
    def validate_gate(session: Session, gate_id: str):
        gate = session.get(Gate, gate_id)
        if not gate:
            raise HTTPException(status_code=400, detail="Invalid gate ID")
        return gate

    @staticmethod
    def check_student(session: Session, qr_code: str):
        statement = select(Student).where(Student.qr_code == qr_code)
        student = session.exec(statement).first()
        if student and student.enrollment_status.value == "active":
            return {
                "valid": True, "subjectType": "student", "accessGranted": True,
                "message": "Access granted", "requiresFaceVerification": True,
                "subject": {
                    "id": student.id, "name": student.name, "photoUrl": student.photo_url,
                    "department": student.department.name if student.department else None,
                    "enrollmentStatus": student.enrollment_status.value
                }
            }
        return None

    @staticmethod
    def check_staff(session: Session, qr_code: str):
        statement = select(StaffMember).where(StaffMember.qr_code == qr_code)
        staff = session.exec(statement).first()
        if staff and staff.employment_status.value == "active":
            return {
                "valid": True, "subjectType": "staff", "accessGranted": True,
                "message": "Access granted", "requiresFaceVerification": True,
                "subject": {
                    "id": staff.id, "name": staff.name, "photoUrl": staff.photo_url,
                    "department": staff.department.name if staff.department else None,
                    "position": staff.position, "employmentStatus": staff.employment_status.value
                }
            }
        return None

    @staticmethod
    async def handle_unauthorized_qr(session: Session, qr_code: str, gate_id: str, scan_timestamp: datetime):
        violation_id = generate_violation_id()
        violation = Violation(
            id=violation_id, type=ViolationTypeEnum.UNAUTHORIZED_QR_SCAN,
            gate_id=gate_id, occurred_at=scan_timestamp, scanned_qr_code=qr_code,
            details=json.dumps({"scannedQrCode": qr_code, "reason": "Invalid or tampered QR code"})
        )
        session.add(violation)
        session.commit()
        
        await alert_service.broadcast_violation({
            "id": violation_id,
            "type": "unauthorized_qr_scan",
            "gateId": gate_id,
            "scannedQrCode": qr_code
        })
        
        return {"valid": False, "accessGranted": False, "violationType": "unauthorized_qr_scan",
                "message": "Invalid or tampered QR code", "violationId": violation_id, "subjectPersisted": False}
