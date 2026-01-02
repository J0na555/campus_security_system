import random
import json
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.models.violation import Violation
from app.models.fail_attempt import FailAttempt
from app.models.enums import ViolationTypeEnum, SubjectTypeEnum
from app.utils.ids import generate_violation_id
from app.utils.subjects import get_subject_name, link_subject

class FaceMatchService:
    THRESHOLD = 0.75

    @staticmethod
    def verify(session: Session, subject_id: str, subject_type: str, gate_id: str, scan_timestamp: datetime):
        confidence = random.uniform(0.3, 0.98)
        if confidence >= FaceMatchService.THRESHOLD:
            return {"verified": True, "confidence": round(confidence, 2), 
                    "accessGranted": True, "message": "Face verification successful"}
        
        return FaceMatchService._handle_failure(session, subject_id, subject_type, gate_id, scan_timestamp, confidence)

    @staticmethod
    def _handle_failure(session: Session, subject_id: str, subject_type: str, gate_id: str, scan_timestamp: datetime, confidence: float):
        five_mins_ago = datetime.utcnow() - timedelta(minutes=5)
        name = get_subject_name(session, subject_id, subject_type)
        recent = FaceMatchService._get_recent_fails(session, subject_id, subject_type, gate_id, five_mins_ago)
        count = len(recent) + 1
        
        v_type = ViolationTypeEnum.MULTIPLE_FAIL_ATTEMPT if count >= 3 else ViolationTypeEnum.FACE_VERIFICATION_MISMATCH
        v_id = generate_violation_id()
        
        v = Violation(id=v_id, type=v_type, subject_type=SubjectTypeEnum(subject_type), gate_id=gate_id, occurred_at=scan_timestamp, confidence_score=confidence, details=json.dumps({"failedAttemptCount": count, "confidence": round(confidence, 2)}))
        link_subject(v, subject_id, subject_type)
        session.add(v)
        
        f = FailAttempt(subject_type=SubjectTypeEnum(subject_type), gate_id=gate_id, attempted_at=scan_timestamp, confidence_score=confidence, violation_id=v_id)
        link_subject(f, subject_id, subject_type)
        session.add(f)
        session.commit()
        
        res = {"verified": False, "accessGranted": False, "violationType": v_type.value, "message": "Verification failure", "violationId": v_id, "subjectPersisted": True, "subject": {"id": subject_id, "name": name, "type": subject_type}}
        if count >= 3:
            res["lockoutUntil"] = (datetime.utcnow() + timedelta(minutes=10)).isoformat() + "Z"
            res["failedAttemptCount"] = count
        return res

    @staticmethod
    def _get_recent_fails(session: Session, subject_id: str, subject_type: str, gate_id: str, since: datetime):
        q = select(FailAttempt).where(FailAttempt.attempted_at >= since, FailAttempt.gate_id == gate_id)
        if subject_type == "student": q = q.where(FailAttempt.student_id == subject_id)
        elif subject_type == "staff": q = q.where(FailAttempt.staff_id == subject_id)
        elif subject_type == "visitor": q = q.where(FailAttempt.visitor_id == subject_id)
        return session.exec(q).all()
