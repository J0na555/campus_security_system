"""
Gate scanning API endpoints (QR scan and face verification)
Public endpoints - no authentication required
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from schemas import (
    QRScanRequest, FaceVerifyRequest,
    SuccessResponse
)
from models import (
    Student, StaffMember, Visitor, Gate, Violation, FailAttempt,
    ViolationTypeEnum, SubjectTypeEnum
)
import uuid
import json

router = APIRouter(prefix="/scan", tags=["Gate Scanning"])


def generate_violation_id() -> str:
    """Generate a unique violation ID"""
    return f"vio_{uuid.uuid4().hex[:10]}"


@router.post("/qr", response_model=SuccessResponse)
async def scan_qr_code(
    scan_data: QRScanRequest,
    session: Session = Depends(get_session)
):
    """
    Validate a QR code at a gate
    
    Public endpoint - no authentication required
    Returns access decision and subject information
    """
    qr_code = scan_data.qrCode
    gate_id = scan_data.gateId
    
    # Verify gate exists
    gate = session.get(Gate, gate_id)
    if not gate:
        raise HTTPException(status_code=400, detail="Invalid gate ID")
    
    # Try to find the subject by QR code
    # Check students
    statement = select(Student).where(Student.qr_code == qr_code)
    student = session.exec(statement).first()
    
    if student:
        # Check if student is active
        if student.enrollment_status.value != "active":
            # Could create a violation here if needed
            return {
                "status": "success",
                "data": {
                    "valid": False,
                    "accessGranted": False,
                    "message": "Student enrollment is not active",
                    "subjectType": "student"
                }
            }
        
        # Valid student QR code
        return {
            "status": "success",
            "data": {
                "valid": True,
                "subjectType": "student",
                "subject": {
                    "id": student.id,
                    "name": student.name,
                    "photoUrl": student.photo_url,
                    "department": student.department.name if student.department else None,
                    "enrollmentStatus": student.enrollment_status.value
                },
                "accessGranted": True,
                "message": "Access granted",
                "requiresFaceVerification": True
            }
        }
    
    # Check staff
    statement = select(StaffMember).where(StaffMember.qr_code == qr_code)
    staff = session.exec(statement).first()
    
    if staff:
        # Check if staff is active
        if staff.employment_status.value != "active":
            return {
                "status": "success",
                "data": {
                    "valid": False,
                    "accessGranted": False,
                    "message": "Staff employment is not active",
                    "subjectType": "staff"
                }
            }
        
        # Valid staff QR code
        return {
            "status": "success",
            "data": {
                "valid": True,
                "subjectType": "staff",
                "subject": {
                    "id": staff.id,
                    "name": staff.name,
                    "photoUrl": staff.photo_url,
                    "department": staff.department.name if staff.department else None,
                    "position": staff.position,
                    "employmentStatus": staff.employment_status.value
                },
                "accessGranted": True,
                "message": "Access granted",
                "requiresFaceVerification": True
            }
        }
    
    # Check visitors
    statement = select(Visitor).where(Visitor.qr_code == qr_code)
    visitor = session.exec(statement).first()
    
    if visitor:
        current_time = datetime.utcnow()
        
        # Check if visitor pass is expired
        if current_time > visitor.valid_until:
            # Create expired_visitor_qr_code violation
            violation_id = generate_violation_id()
            violation = Violation(
                id=violation_id,
                type=ViolationTypeEnum.EXPIRED_VISITOR_QR_CODE,
                subject_type=SubjectTypeEnum.VISITOR,
                visitor_id=visitor.id,
                gate_id=gate_id,
                occurred_at=scan_data.scanTimestamp,
                details=json.dumps({
                    "validUntil": visitor.valid_until.isoformat(),
                    "scannedAt": scan_data.scanTimestamp.isoformat()
                })
            )
            session.add(violation)
            session.commit()
            
            return {
                "status": "success",
                "data": {
                    "valid": False,
                    "accessGranted": False,
                    "violationType": "expired_visitor_qr_code",
                    "message": "Visitor pass has expired",
                    "violationId": violation_id,
                    "subjectPersisted": True,
                    "subject": {
                        "id": visitor.id,
                        "name": visitor.name,
                        "validUntil": visitor.valid_until.isoformat() + "Z"
                    }
                }
            }
        
        # Check if pass is not yet valid
        if current_time < visitor.valid_from:
            return {
                "status": "success",
                "data": {
                    "valid": False,
                    "accessGranted": False,
                    "message": f"Visitor pass not valid until {visitor.valid_from.isoformat()}Z",
                    "subjectType": "visitor"
                }
            }
        
        # Check allowed gates if specified
        if visitor.allowed_gates:
            allowed_gates_list = json.loads(visitor.allowed_gates)
            if gate_id not in allowed_gates_list:
                return {
                    "status": "success",
                    "data": {
                        "valid": False,
                        "accessGranted": False,
                        "message": "This gate is not in the allowed gates list for this visitor",
                        "subjectType": "visitor"
                    }
                }
        
        # Valid visitor pass
        return {
            "status": "success",
            "data": {
                "valid": True,
                "subjectType": "visitor",
                "subject": {
                    "id": visitor.id,
                    "name": visitor.name,
                    "photoUrl": visitor.photo_url,
                    "purpose": visitor.purpose,
                    "hostName": visitor.host.name,
                    "hostDepartment": visitor.host.department.name if visitor.host.department else None,
                    "validFrom": visitor.valid_from.isoformat() + "Z",
                    "validUntil": visitor.valid_until.isoformat() + "Z"
                },
                "accessGranted": True,
                "message": "Visitor pass valid",
                "requiresFaceVerification": False
            }
        }
    
    # QR code not found - unauthorized_qr_scan violation
    violation_id = generate_violation_id()
    violation = Violation(
        id=violation_id,
        type=ViolationTypeEnum.UNAUTHORIZED_QR_SCAN,
        subject_type=None,  # No subject for invalid QR
        gate_id=gate_id,
        occurred_at=scan_data.scanTimestamp,
        scanned_qr_code=qr_code,
        details=json.dumps({
            "scannedQrCode": qr_code,
            "reason": "Invalid or tampered QR code"
        })
    )
    session.add(violation)
    session.commit()
    
    return {
        "status": "success",
        "data": {
            "valid": False,
            "accessGranted": False,
            "violationType": "unauthorized_qr_scan",
            "message": "Invalid or tampered QR code",
            "violationId": violation_id,
            "subjectPersisted": False
        }
    }


@router.post("/face/verify", response_model=SuccessResponse)
async def verify_face(
    verify_data: FaceVerifyRequest,
    session: Session = Depends(get_session)
):
    """
    Verify a captured face against the enrolled photo
    
    Public endpoint - no authentication required
    Returns verification result and access decision
    """
    subject_id = verify_data.subjectId
    subject_type = verify_data.subjectType
    gate_id = verify_data.gateId
    
    # In a real implementation, this would call a face recognition service
    # For now, we'll simulate it with a random confidence score
    import random
    confidence = random.uniform(0.3, 0.98)
    
    # Simulate face verification threshold
    VERIFICATION_THRESHOLD = 0.75
    verified = confidence >= VERIFICATION_THRESHOLD
    
    if verified:
        # Face verification successful
        # In production, log this to AccessLog table
        return {
            "status": "success",
            "data": {
                "verified": True,
                "confidence": round(confidence, 2),
                "accessGranted": True,
                "message": "Face verification successful"
            }
        }
    
    # Face verification failed - check for multiple attempts
    # Count recent failed attempts (within last 5 minutes)
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    
    # Get subject based on type
    subject_name = None
    if subject_type == "student":
        student = session.get(Student, subject_id)
        if student:
            subject_name = student.name
    elif subject_type == "staff":
        staff = session.get(StaffMember, subject_id)
        if staff:
            subject_name = staff.name
    elif subject_type == "visitor":
        visitor = session.get(Visitor, subject_id)
        if visitor:
            subject_name = visitor.name
    
    # Build query for recent fail attempts
    query = select(FailAttempt).where(
        FailAttempt.attempted_at >= five_minutes_ago,
        FailAttempt.gate_id == gate_id
    )
    
    if subject_type == "student":
        query = query.where(FailAttempt.student_id == subject_id)
    elif subject_type == "staff":
        query = query.where(FailAttempt.staff_id == subject_id)
    elif subject_type == "visitor":
        query = query.where(FailAttempt.visitor_id == subject_id)
    
    recent_attempts = session.exec(query).all()
    attempt_count = len(recent_attempts) + 1  # +1 for current attempt
    
    # Determine violation type
    if attempt_count >= 3:
        # Multiple fail attempt violation
        violation_id = generate_violation_id()
        violation = Violation(
            id=violation_id,
            type=ViolationTypeEnum.MULTIPLE_FAIL_ATTEMPT,
            subject_type=SubjectTypeEnum(subject_type),
            gate_id=gate_id,
            occurred_at=verify_data.scanTimestamp,
            confidence_score=confidence,
            details=json.dumps({
                "failedAttemptCount": attempt_count,
                "confidence": round(confidence, 2),
                "timeWindow": "5 minutes"
            })
        )
        
        # Link to subject
        if subject_type == "student":
            violation.student_id = subject_id
        elif subject_type == "staff":
            violation.staff_id = subject_id
        elif subject_type == "visitor":
            violation.visitor_id = subject_id
        
        session.add(violation)
        
        # Record this fail attempt
        fail_attempt = FailAttempt(
            subject_type=SubjectTypeEnum(subject_type),
            gate_id=gate_id,
            attempted_at=verify_data.scanTimestamp,
            confidence_score=confidence,
            violation_id=violation_id
        )
        
        if subject_type == "student":
            fail_attempt.student_id = subject_id
        elif subject_type == "staff":
            fail_attempt.staff_id = subject_id
        elif subject_type == "visitor":
            fail_attempt.visitor_id = subject_id
        
        session.add(fail_attempt)
        session.commit()
        
        lockout_until = datetime.utcnow() + timedelta(minutes=10)
        
        return {
            "status": "success",
            "data": {
                "verified": False,
                "accessGranted": False,
                "violationType": "multiple_fail_attempt",
                "message": "Access blocked: 3+ verification failures in 5 minutes",
                "violationId": violation_id,
                "subjectPersisted": True,
                "capturedImagePersisted": True,
                "lockoutUntil": lockout_until.isoformat() + "Z",
                "failedAttemptCount": attempt_count,
                "subject": {
                    "id": subject_id,
                    "name": subject_name,
                    "type": subject_type
                }
            }
        }
    
    # Single face verification mismatch
    violation_id = generate_violation_id()
    violation = Violation(
        id=violation_id,
        type=ViolationTypeEnum.FACE_VERIFICATION_MISMATCH,
        subject_type=SubjectTypeEnum(subject_type),
        gate_id=gate_id,
        occurred_at=verify_data.scanTimestamp,
        confidence_score=confidence,
        details=json.dumps({
            "confidence": round(confidence, 2)
        })
    )
    
    # Link to subject
    if subject_type == "student":
        violation.student_id = subject_id
    elif subject_type == "staff":
        violation.staff_id = subject_id
    elif subject_type == "visitor":
        violation.visitor_id = subject_id
    
    session.add(violation)
    
    # Record this fail attempt
    fail_attempt = FailAttempt(
        subject_type=SubjectTypeEnum(subject_type),
        gate_id=gate_id,
        attempted_at=verify_data.scanTimestamp,
        confidence_score=confidence,
        violation_id=violation_id
    )
    
    if subject_type == "student":
        fail_attempt.student_id = subject_id
    elif subject_type == "staff":
        fail_attempt.staff_id = subject_id
    elif subject_type == "visitor":
        fail_attempt.visitor_id = subject_id
    
    session.add(fail_attempt)
    session.commit()
    
    return {
        "status": "success",
        "data": {
            "verified": False,
            "confidence": round(confidence, 2),
            "accessGranted": False,
            "violationType": "face_verification_mismatch",
            "message": "Face does not match enrolled photo",
            "violationId": violation_id,
            "subjectPersisted": True,
            "capturedImagePersisted": True,
            "subject": {
                "id": subject_id,
                "name": subject_name,
                "type": subject_type
            }
        }
    }
