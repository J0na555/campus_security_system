"""
Comprehensive mock data for frontend testing
Includes violations, visitors, vehicle entries, and alerts
"""
import json
from datetime import datetime, timedelta
from sqlmodel import Session
from app.models.visitor import Visitor
from app.models.violation import Violation
from app.models.vehicle_entry import VehicleEntry
from app.models.vehicle_alert import VehicleAlert
from app.models.enums import (
    ViolationTypeEnum, SubjectTypeEnum, VehicleEntryStatusEnum,
    VehicleAlertTypeEnum
)
from app.utils.ids import generate_violation_id, generate_pass_id


def create_mock_visitors(session: Session, staff_members, security_staff, gates):
    """Create mock visitor passes for testing"""
    now = datetime.utcnow()
    
    visitors = [
        Visitor(
            id=generate_pass_id(),
            name="Bob Williams",
            email="bob.williams@email.com",
            phone="+1-555-123-4567",
            purpose="Interview at HR Department",
            host_staff_id=staff_members[1].id,  # Jane Doe (HR Manager)
            qr_code="QR-VIS-2026-MOCK001",
            valid_from=now - timedelta(hours=2),
            valid_until=now + timedelta(hours=6),
            allowed_gates=json.dumps([gates[0].id, gates[2].id]),
            created_by_staff_id=security_staff[0].id  # John Smith
        ),
        Visitor(
            id=generate_pass_id(),
            name="Alice Cooper",
            email="alice.cooper@email.com",
            phone="+1-555-234-5678",
            purpose="Guest Lecture - Engineering",
            host_staff_id=staff_members[0].id,  # Dr. Robert Chen
            qr_code="QR-VIS-2026-MOCK002",
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(hours=2),
            allowed_gates=json.dumps([gates[0].id, gates[3].id]),
            created_by_staff_id=security_staff[2].id  # Michael Chen (Admin)
        ),
        Visitor(
            id=generate_pass_id(),
            name="Charlie Brown",
            email="charlie.brown@email.com",
            purpose="Campus Tour",
            host_staff_id=staff_members[0].id,
            qr_code="QR-VIS-2026-MOCK003",
            valid_from=now - timedelta(days=2),
            valid_until=now - timedelta(hours=1),  # Expired
            allowed_gates=json.dumps([gates[0].id]),
            created_by_staff_id=security_staff[1].id  # Sarah Johnson
        ),
        Visitor(
            id=generate_pass_id(),
            name="Diana Prince",
            email="diana.prince@email.com",
            phone="+1-555-345-6789",
            purpose="Research Collaboration Meeting",
            host_staff_id=staff_members[0].id,
            qr_code="QR-VIS-2026-MOCK004",
            valid_from=now + timedelta(hours=1),
            valid_until=now + timedelta(days=1),
            allowed_gates=None,  # All gates allowed
            created_by_staff_id=security_staff[0].id
        )
    ]
    
    for visitor in visitors:
        session.add(visitor)
    return visitors


def create_mock_violations(session: Session, students, staff_members, visitors, gates, security_staff):
    """Create mock violations for dashboard testing"""
    now = datetime.utcnow()
    
    violations = [
        # Face verification mismatch
        Violation(
            id=generate_violation_id(),
            type=ViolationTypeEnum.FACE_VERIFICATION_MISMATCH,
            subject_type=SubjectTypeEnum.STUDENT,
            student_id=students[0].id,
            gate_id=gates[0].id,
            occurred_at=now - timedelta(hours=2),
            details=json.dumps({"confidence": 0.32, "threshold": 0.75}),
            confidence_score=0.32,
            captured_image_url="https://cdn.campus-security.example.com/captures/vio_face001.jpg",
            resolved=False
        ),
        # Unauthorized QR scan
        Violation(
            id=generate_violation_id(),
            type=ViolationTypeEnum.UNAUTHORIZED_QR_SCAN,
            subject_type=None,
            gate_id=gates[1].id,
            occurred_at=now - timedelta(hours=5),
            scanned_qr_code="INVALID_QR_DATA_xyz123",
            details=json.dumps({"scannedQrCode": "INVALID_QR_DATA_xyz123"}),
            captured_image_url="https://cdn.campus-security.example.com/captures/vio_qr001.jpg",
            resolved=True,
            resolved_at=now - timedelta(hours=4),
            resolved_by_staff_id=security_staff[0].id,
            resolution_notes="Investigated - student using old expired ID card"
        ),
        # Expired visitor QR code
        Violation(
            id=generate_violation_id(),
            type=ViolationTypeEnum.EXPIRED_VISITOR_QR_CODE,
            subject_type=SubjectTypeEnum.VISITOR,
            visitor_id=visitors[2].id,  # Charlie Brown (expired)
            gate_id=gates[0].id,
            occurred_at=now - timedelta(minutes=30),
            details=json.dumps({
                "validUntil": visitors[2].valid_until.isoformat(),
                "scannedAt": (now - timedelta(minutes=30)).isoformat()
            }),
            captured_image_url="https://cdn.campus-security.example.com/captures/vio_exp001.jpg",
            resolved=False
        ),
        # Multiple fail attempt
        Violation(
            id=generate_violation_id(),
            type=ViolationTypeEnum.MULTIPLE_FAIL_ATTEMPT,
            subject_type=SubjectTypeEnum.STAFF,
            staff_id=staff_members[0].id,
            gate_id=gates[3].id,
            occurred_at=now - timedelta(hours=1),
            details=json.dumps({
                "failedAttemptCount": 3,
                "lockoutUntil": (now + timedelta(minutes=15)).isoformat()
            }),
            confidence_score=0.25,
            captured_image_url="https://cdn.campus-security.example.com/captures/vio_multi001.jpg",
            resolved=False
        ),
        # Another face verification mismatch (resolved)
        Violation(
            id=generate_violation_id(),
            type=ViolationTypeEnum.FACE_VERIFICATION_MISMATCH,
            subject_type=SubjectTypeEnum.STUDENT,
            student_id=students[1].id,
            gate_id=gates[2].id,
            occurred_at=now - timedelta(days=1),
            details=json.dumps({"confidence": 0.28}),
            confidence_score=0.28,
            captured_image_url="https://cdn.campus-security.example.com/captures/vio_face002.jpg",
            resolved=True,
            resolved_at=now - timedelta(hours=20),
            resolved_by_staff_id=security_staff[1].id,
            resolution_notes="False alarm - lighting issue"
        ),
        # Recent unauthorized QR scan
        Violation(
            id=generate_violation_id(),
            type=ViolationTypeEnum.UNAUTHORIZED_QR_SCAN,
            subject_type=None,
            gate_id=gates[0].id,
            occurred_at=now - timedelta(minutes=15),
            scanned_qr_code="TAMPERED_QR_789",
            details=json.dumps({"scannedQrCode": "TAMPERED_QR_789"}),
            captured_image_url="https://cdn.campus-security.example.com/captures/vio_qr002.jpg",
            resolved=False
        )
    ]
    
    for violation in violations:
        session.add(violation)
    return violations


def create_mock_vehicle_entries(session: Session, vehicles, gates):
    """Create mock vehicle entries for testing"""
    now = datetime.utcnow()
    
    entries = [
        VehicleEntry(
            license_plate="ABC-123",
            vehicle_id=vehicles[0].id if vehicles else None,
            entry_time=now - timedelta(hours=3),
            exit_time=now - timedelta(hours=1),
            status=VehicleEntryStatusEnum.EXITED,
            gate_id=gates[0].id
        ),
        VehicleEntry(
            license_plate="XYZ-789",
            vehicle_id=vehicles[1].id if len(vehicles) > 1 else None,
            entry_time=now - timedelta(hours=2),
            status=VehicleEntryStatusEnum.ENTERED,
            gate_id=gates[0].id
        ),
        VehicleEntry(
            license_plate="UNKNOWN-999",
            vehicle_id=None,  # Unknown vehicle
            entry_time=now - timedelta(minutes=30),
            status=VehicleEntryStatusEnum.FLAGGED,
            gate_id=gates[1].id
        ),
        VehicleEntry(
            license_plate="MOT-456",
            vehicle_id=vehicles[2].id if len(vehicles) > 2 else None,
            entry_time=now - timedelta(hours=4),
            exit_time=now - timedelta(hours=2),
            status=VehicleEntryStatusEnum.EXITED,
            gate_id=gates[3].id
        )
    ]
    
    for entry in entries:
        session.add(entry)
    return entries


def create_mock_vehicle_alerts(session: Session, gates, security_staff):
    """Create mock vehicle alerts for testing"""
    now = datetime.utcnow()
    
    alerts = [
        VehicleAlert(
            license_plate="UNKNOWN-999",
            timestamp=now - timedelta(minutes=30),
            alert_type=VehicleAlertTypeEnum.UNKNOWN_VEHICLE,
            gate_id=gates[1].id,
            resolved=False
        ),
        VehicleAlert(
            license_plate="SUSPECT-123",
            timestamp=now - timedelta(hours=2),
            alert_type=VehicleAlertTypeEnum.UNKNOWN_VEHICLE,
            gate_id=gates[0].id,
            resolved=True,
            resolved_at=now - timedelta(hours=1),
            resolved_by_staff_id=security_staff[0].id,
            resolution_notes="Vehicle registered after alert"
        ),
        VehicleAlert(
            license_plate="MISMATCH-456",
            timestamp=now - timedelta(hours=1),
            alert_type=VehicleAlertTypeEnum.VEHICLE_MISMATCH,
            gate_id=gates[2].id,
            resolved=False
        )
    ]
    
    for alert in alerts:
        session.add(alert)
    return alerts


def populate_mock_data(session: Session, students, staff_members, vehicles, gates, security_staff):
    """Populate all mock data for frontend testing"""
    print("Creating mock visitors...")
    visitors = create_mock_visitors(session, staff_members, security_staff, gates)
    session.commit()
    
    print("Creating mock violations...")
    violations = create_mock_violations(session, students, staff_members, visitors, gates, security_staff)
    session.commit()
    
    print("Creating mock vehicle entries...")
    vehicle_entries = create_mock_vehicle_entries(session, vehicles, gates)
    session.commit()
    
    print("Creating mock vehicle alerts...")
    vehicle_alerts = create_mock_vehicle_alerts(session, gates, security_staff)
    session.commit()
    
    print(f"Mock data created:")
    print(f"  - {len(visitors)} visitors")
    print(f"  - {len(violations)} violations")
    print(f"  - {len(vehicle_entries)} vehicle entries")
    print(f"  - {len(vehicle_alerts)} vehicle alerts")
    
    return {
        "visitors": visitors,
        "violations": violations,
        "vehicle_entries": vehicle_entries,
        "vehicle_alerts": vehicle_alerts
    }
