import pytest
import json
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from datetime import datetime, timedelta

from app.main import app
from app.core.database import get_session
from app.utils.sample_data import (
    create_gates, create_departments, create_security_staff
)
from app.utils.sample_data_subjects import (
    create_students, create_staff_members, create_vehicles
)
from app.models.enums import UserRoleEnum, SubjectTypeEnum

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        gates = create_gates(session)
        depts = create_departments(session)
        session.commit()
        
        staff = create_security_staff(session)
        students = create_students(session, depts)
        staff_members = create_staff_members(session, depts)
        create_vehicles(session, students, staff_members)
        session.commit()
        
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session):
    return TestClient(app)

@pytest.fixture(name="auth_token")
def auth_token_fixture(client):
    # Use Michael Chen (Admin) for testing protected endpoints
    response = client.post(
        "/api/v1/auth/login",
        json={"employeeId": "EMP-2024-003", "password": "password123"}
    )
    return response.json()["data"]["token"]

def test_root_and_health(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_auth_login(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"employeeId": "EMP-2024-003", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "token" in response.json()["data"]

def test_auth_me(client, auth_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["employeeId"] == "EMP-2024-003"

def test_scan_qr_student(client):
    response = client.post(
        "/api/v1/scan/qr",
        json={
            "qrCode": "QR-STU-2024-ABC123XYZ",
            "gateId": "gate_main_entrance",
            "scanTimestamp": datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["data"]["subjectType"] == "student"

def test_scan_qr_invalid(client):
    response = client.post(
        "/api/v1/scan/qr",
        json={
            "qrCode": "INVALID-QR",
            "gateId": "gate_main_entrance",
            "scanTimestamp": datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == 200
    # The app returns 200 even for unauthorized scans but with violation info
    assert response.json()["data"]["valid"] == False
    assert "violationId" in response.json()["data"]

def test_visitor_pass_lifecycle(client, auth_token):
    # 1. Create a pass
    pass_data = {
        "visitorName": "John Test Visitor",
        "visitorEmail": "test@visitor.com",
        "purpose": "Test Purpose",
        "hostEmployeeId": "stf_456abc",
        "validFrom": datetime.utcnow().isoformat(),
        "validUntil": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        "allowedGates": ["gate_main_entrance"]
    }
    response = client.post(
        "/api/v1/visitors/passes",
        json=pass_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    qr_code = response.json()["data"]["qrCode"]["content"]
    
    # 2. List passes
    response = client.get(
        "/api/v1/visitors/passes",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert any(p["visitorName"] == "John Test Visitor" for p in response.json()["data"]["visitors"])

    # 3. Scan the visitor QR
    response = client.post(
        "/api/v1/scan/qr",
        json={
            "qrCode": qr_code,
            "gateId": "gate_main_entrance",
            "scanTimestamp": datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == 200
    assert response.json()["data"]["subjectType"] == "visitor"

def test_vehicle_endpoints(client, auth_token):
    # 1. Vehicle Entry (Registered)
    response = client.post(
        "/api/v1/vehicles/entry",
        json={
            "licensePlate": "ABC-123",
            "gateId": "gate_main_entrance",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    assert response.status_code == 200
    assert response.json()["data"]["registered"] == True
    
    # 2. Vehicle Exit
    response = client.post(
        "/api/v1/vehicles/exit",
        json={
            "licensePlate": "ABC-123",
            "gateId": "gate_main_entrance",
            "timestamp": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        }
    )
    assert response.status_code == 200
    assert "Exit logged" in response.json()["data"]["message"]

    # 3. Register New Vehicle
    response = client.post(
        "/api/v1/vehicles",
        json={
            "licensePlate": "NEW-777",
            "ownerType": "student",
            "ownerId": "stu_789xyz",
            "ownerName": "Alice Johnson",
            "vehicleType": "car",
            "make": "Tesla",
            "model": "Model 3"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    
    # 4. List Vehicles
    response = client.get(
        "/api/v1/vehicles",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert any(v["licensePlate"] == "NEW-777" for v in response.json()["data"]["vehicles"])

def test_vehicle_alerts(client, auth_token):
    # 1. Trigger a vehicle alert by logging an entry for an unregistered vehicle
    client.post(
        "/api/v1/vehicles/entry",
        json={
            "licensePlate": "UNREG-123",
            "gateId": "gate_main_entrance",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    # 2. List vehicle alerts
    response = client.get(
        "/api/v1/vehicles/alerts",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()["data"]["alerts"]) > 0
    assert response.json()["data"]["alerts"][0]["licensePlate"] == "UNREG-123"

def test_violations_and_resolution(client, auth_token):
    # 1. Generate a violation via invalid QR scan
    client.post(
        "/api/v1/scan/qr",
        json={
            "qrCode": "BAD-CODE",
            "gateId": "gate_main_entrance",
            "scanTimestamp": datetime.utcnow().isoformat()
        }
    )
    
    # 2. List violations
    response = client.get(
        "/api/v1/violations",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    violations = response.json()["data"]["violations"]
    assert len(violations) > 0
    violation_id = violations[0]["id"]
    
    # 3. Resolve violation
    response = client.patch(
        f"/api/v1/violations/{violation_id}/resolve",
        params={"notes": "Test resolution"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["resolved"] == True

def test_websocket_violation_broadcast(client):
    with client.websocket_connect("/ws/alerts") as websocket:
        # Trigger an unauthorized QR scan violation
        response = client.post(
            "/api/v1/scan/qr",
            json={
                "qrCode": "INVALID-QR-CODE-BROADCAST",
                "gateId": "gate_main_entrance",
                "scanTimestamp": datetime.utcnow().isoformat()
            }
        )
        assert response.status_code == 200
        
        # Check if we received the broadcast
        data = websocket.receive_text()
        message = json.loads(data)
        
        assert message["type"] == "violation_alert"
        assert message["data"]["scannedQrCode"] == "INVALID-QR-CODE-BROADCAST"
        assert message["data"]["type"] == "unauthorized_qr_scan"

def test_websocket_vehicle_alert_broadcast(client):
    with client.websocket_connect("/ws/alerts") as websocket:
        # Trigger an unregistered vehicle entry alert
        response = client.post(
            "/api/v1/vehicles/entry",
            json={
                "licensePlate": "UNREG-BROADCAST",
                "gateId": "gate_main_entrance",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        assert response.status_code == 200
        
        # Check if we received the broadcast
        data = websocket.receive_text()
        message = json.loads(data)
        
        assert message["type"] == "vehicle_alert"
        assert message["data"]["plate"] == "UNREG-BROADCAST"

def test_websocket_expired_visitor_broadcast(client, session):
    # 1. Manually insert an expired visitor into the DB bypassing service validation
    from app.models.visitor import Visitor
    from app.models.staff import StaffMember
    from app.models.security_staff import SecurityStaff
    
    staff = session.exec(select(StaffMember)).first()
    sec_staff = session.exec(select(SecurityStaff)).first()
    
    visitor = Visitor(
        id="test-expired-visitor",
        name="Expired Visitor",
        email="expired@visitor.com",
        purpose="Test Expired",
        host_staff_id=staff.id,
        qr_code="QR-EXP-123456",
        valid_from=datetime.utcnow() - timedelta(days=2),
        valid_until=datetime.utcnow() - timedelta(minutes=5),
        allowed_gates=json.dumps(["gate_main_entrance"]),
        created_by_staff_id=sec_staff.id
    )
    session.add(visitor)
    session.commit()
    
    with client.websocket_connect("/ws/alerts") as websocket:
        # 2. Scan the expired visitor QR
        response = client.post(
            "/api/v1/scan/qr",
            json={
                "qrCode": "QR-EXP-123456",
                "gateId": "gate_main_entrance",
                "scanTimestamp": datetime.utcnow().isoformat()
            }
        )
        assert response.status_code == 200
        assert response.json()["data"]["violationType"] == "expired_visitor_qr_code"
        
        # 3. Check broadcast
        data = websocket.receive_text()
        message = json.loads(data)
        assert message["type"] == "violation_alert"
        assert message["data"]["type"] == "expired_visitor_qr_code"
        assert message["data"]["visitorName"] == "Expired Visitor"
