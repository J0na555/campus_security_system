from sqlmodel import Session
from app.models.gate import Gate
from app.models.department import Department
from app.models.security_staff import SecurityStaff
from app.models.student import Student
from app.models.staff import StaffMember
from app.models.vehicle import Vehicle
from app.models.enums import (
    GateStatusEnum, UserRoleEnum, EnrollmentStatusEnum,
    EmploymentStatusEnum, OwnerTypeEnum, VehicleTypeEnum
)
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_gates(session: Session):
    gates = [
        Gate(id="gate_main_entrance", name="Main Entrance Gate", 
             location="Building A - North Side", status=GateStatusEnum.ONLINE),
        Gate(id="gate_library", name="Library Gate", 
             location="Library Building - East Entrance", status=GateStatusEnum.ONLINE),
        Gate(id="gate_hr_building", name="HR Building Gate", 
             location="HR Building - Main Entrance", status=GateStatusEnum.ONLINE),
        Gate(id="gate_engineering", name="Engineering Block Gate", 
             location="Engineering Building - West Wing", status=GateStatusEnum.ONLINE)
    ]
    for gate in gates:
        session.add(gate)
    return gates

def create_departments(session: Session):
    departments = [
        Department(name="Computer Science", code="CS"),
        Department(name="Engineering", code="ENG"),
        Department(name="Business Administration", code="BA"),
        Department(name="Human Resources", code="HR"),
        Department(name="Mathematics", code="MATH")
    ]
    for dept in departments:
        session.add(dept)
    return departments

def create_security_staff(session: Session):
    staff = [
        SecurityStaff(
            id="usr_abc123", employee_id="EMP-2024-001", name="John Smith",
            email="john.smith@campus.edu", password_hash=pwd_context.hash("password123"),
            role=UserRoleEnum.SECURITY_OFFICER, last_login_at=datetime.utcnow()
        ),
        SecurityStaff(
            id="usr_def456", employee_id="EMP-2024-002", name="Sarah Johnson",
            email="sarah.johnson@campus.edu", password_hash=pwd_context.hash("password123"),
            role=UserRoleEnum.SECURITY_SUPERVISOR
        ),
        SecurityStaff(
            id="usr_ghi789", employee_id="EMP-2024-003", name="Michael Chen",
            email="michael.chen@campus.edu", password_hash=pwd_context.hash("password123"),
            role=UserRoleEnum.ADMIN
        ),
        SecurityStaff(
            id="usr_admin001", employee_id="ADMIN-001", name="Admin User",
            email="admin@campus.edu", password_hash=pwd_context.hash("admin123"),
            role=UserRoleEnum.ADMIN, department="IT Administration"
        ),
        SecurityStaff(
            id="usr_admin002", employee_id="ADMIN-002", name="Super Admin",
            email="superadmin@campus.edu", password_hash=pwd_context.hash("admin123"),
            role=UserRoleEnum.ADMIN, department="System Administration"
        ),
        SecurityStaff(
            id="usr_super001", employee_id="SUPER-001", name="Supervisor One",
            email="supervisor1@campus.edu", password_hash=pwd_context.hash("super123"),
            role=UserRoleEnum.SECURITY_SUPERVISOR
        )
    ]
    for s in staff:
        session.add(s)
    return staff
