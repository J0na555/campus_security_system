import json
from datetime import datetime
from sqlmodel import Session, select
from app.models.visitor import Visitor
from app.models.violation import Violation
from app.models.enums import ViolationTypeEnum, SubjectTypeEnum
from app.utils.ids import generate_violation_id

class VisitorQRService:
    @staticmethod
    def check_visitor(session: Session, qr_code: str, gate_id: str, scan_timestamp: datetime):
        statement = select(Visitor).where(Visitor.qr_code == qr_code)
        visitor = session.exec(statement).first()
        if not visitor: return None
        
        current_time = datetime.utcnow()
        if current_time > visitor.valid_until:
            return VisitorQRService._handle_expired_visitor(session, visitor, gate_id, scan_timestamp)
        
        if current_time < visitor.valid_from:
            return {"valid": False, "accessGranted": False, "subjectType": "visitor",
                    "message": f"Visitor pass not valid until {visitor.valid_from.isoformat()}Z"}
        
        if visitor.allowed_gates:
            allowed = json.loads(visitor.allowed_gates)
            if gate_id not in allowed:
                return {"valid": False, "accessGranted": False, "subjectType": "visitor",
                        "message": "Gate not allowed"}
        
        return {
            "valid": True, "subjectType": "visitor", "accessGranted": True,
            "message": "Visitor pass valid", "requiresFaceVerification": False,
            "subject": {
                "id": visitor.id, "name": visitor.name, "photoUrl": visitor.photo_url,
                "purpose": visitor.purpose, "hostName": visitor.host.name,
                "hostDepartment": visitor.host.department.name if visitor.host.department else None,
                "validFrom": visitor.valid_from.isoformat() + "Z",
                "validUntil": visitor.valid_until.isoformat() + "Z"
            }
        }

    @staticmethod
    def _handle_expired_visitor(session: Session, visitor: Visitor, gate_id: str, scan_timestamp: datetime):
        violation_id = generate_violation_id()
        violation = Violation(
            id=violation_id, type=ViolationTypeEnum.EXPIRED_VISITOR_QR_CODE,
            subject_type=SubjectTypeEnum.VISITOR, visitor_id=visitor.id,
            gate_id=gate_id, occurred_at=scan_timestamp,
            details=json.dumps({"validUntil": visitor.valid_until.isoformat(), 
                                "scannedAt": scan_timestamp.isoformat()})
        )
        session.add(violation)
        session.commit()
        return {
            "valid": False, "accessGranted": False, "violationType": "expired_visitor_qr_code",
            "message": "Visitor pass has expired", "violationId": violation_id,
            "subjectPersisted": True, "subject": {"id": visitor.id, "name": visitor.name}
        }
