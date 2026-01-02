"""
Database configuration and utilities
"""
from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./campus_security.db")

# Create engine
# For SQLite, we need check_same_thread=False to allow FastAPI to use it
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting database sessions"""
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize database with sample data (for development)"""
    from models import (
        Gate, Department, SecurityStaff, Student, StaffMember, Vehicle,
        GateStatusEnum, EnrollmentStatusEnum, EmploymentStatusEnum, UserRoleEnum,
        VehicleTypeEnum, OwnerTypeEnum
    )
    from passlib.context import CryptContext
    from datetime import datetime
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    with Session(engine) as session:
        # Check if data already exists
        existing_gates = session.query(Gate).first()
        if existing_gates:
            print("Database already initialized")
            return
        
        print("Initializing database with sample data...")
        
        # Create Gates
        gates = [
            Gate(
                id="gate_main_entrance",
                name="Main Entrance Gate",
                location="Building A - North Side",
                status=GateStatusEnum.ONLINE
            ),
            Gate(
                id="gate_library",
                name="Library Gate",
                location="Library Building - East Entrance",
                status=GateStatusEnum.ONLINE
            ),
            Gate(
                id="gate_hr_building",
                name="HR Building Gate",
                location="HR Building - Main Entrance",
                status=GateStatusEnum.ONLINE
            ),
            Gate(
                id="gate_engineering",
                name="Engineering Block Gate",
                location="Engineering Building - West Wing",
                status=GateStatusEnum.ONLINE
            )
        ]
        for gate in gates:
            session.add(gate)
        
        # Create Departments
        departments = [
            Department(name="Computer Science", code="CS"),
            Department(name="Engineering", code="ENG"),
            Department(name="Business Administration", code="BA"),
            Department(name="Human Resources", code="HR"),
            Department(name="Mathematics", code="MATH")
        ]
        for dept in departments:
            session.add(dept)
        
        session.commit()
        session.refresh(departments[0])  # Refresh to get IDs
        
        # Create Security Staff (Dashboard Users)
        security_staff = [
            SecurityStaff(
                id="usr_abc123",
                employee_id="EMP-2024-001",
                name="John Smith",
                email="john.smith@campus.edu",
                password_hash=pwd_context.hash("password123"),  # In production, use strong passwords
                role=UserRoleEnum.SECURITY_OFFICER,
                department="Campus Security",
                last_login_at=datetime.utcnow()
            ),
            SecurityStaff(
                id="usr_def456",
                employee_id="EMP-2024-002",
                name="Sarah Johnson",
                email="sarah.johnson@campus.edu",
                password_hash=pwd_context.hash("password123"),
                role=UserRoleEnum.SECURITY_SUPERVISOR,
                department="Campus Security"
            ),
            SecurityStaff(
                id="usr_ghi789",
                employee_id="EMP-2024-003",
                name="Michael Chen",
                email="michael.chen@campus.edu",
                password_hash=pwd_context.hash("password123"),
                role=UserRoleEnum.ADMIN,
                department="Campus Security"
            )
        ]
        for staff in security_staff:
            session.add(staff)
        
        # Create Sample Students
        students = [
            Student(
                id="stu_789xyz",
                name="Alice Johnson",
                email="alice.johnson@student.campus.edu",
                photo_url="https://cdn.campus-security.example.com/photos/stu_789xyz.jpg",
                department_id=departments[0].id,  # Computer Science
                enrollment_status=EnrollmentStatusEnum.ACTIVE,
                qr_code="QR-STU-2024-ABC123XYZ"
            ),
            Student(
                id="stu_456abc",
                name="Bob Williams",
                email="bob.williams@student.campus.edu",
                photo_url="https://cdn.campus-security.example.com/photos/stu_456abc.jpg",
                department_id=departments[1].id,  # Engineering
                enrollment_status=EnrollmentStatusEnum.ACTIVE,
                qr_code="QR-STU-2024-DEF456ABC"
            )
        ]
        for student in students:
            session.add(student)
        
        # Create Sample Staff Members
        staff_members = [
            StaffMember(
                id="stf_456abc",
                name="Dr. Robert Chen",
                email="robert.chen@campus.edu",
                photo_url="https://cdn.campus-security.example.com/photos/stf_456abc.jpg",
                department_id=departments[1].id,  # Engineering
                position="Professor",
                employment_status=EmploymentStatusEnum.ACTIVE,
                qr_code="QR-STF-2024-XYZ789ABC"
            ),
            StaffMember(
                id="stf_789xyz",
                name="Jane Doe",
                email="jane.doe@campus.edu",
                photo_url="https://cdn.campus-security.example.com/photos/stf_789xyz.jpg",
                department_id=departments[3].id,  # Human Resources
                position="HR Manager",
                employment_status=EmploymentStatusEnum.ACTIVE,
                qr_code="QR-STF-2024-JKL012DEF"
            )
        ]
        for staff_member in staff_members:
            session.add(staff_member)
        
        # Create Sample Vehicles
        vehicles = [
            Vehicle(
                license_plate="ABC-123",
                owner_type=OwnerTypeEnum.STUDENT,
                owner_id=students[0].id,
                owner_name=students[0].name,
                vehicle_type=VehicleTypeEnum.CAR,
                color="Blue",
                make="Toyota",
                model="Camry"
            ),
            Vehicle(
                license_plate="XYZ-789",
                owner_type=OwnerTypeEnum.STAFF,
                owner_id=staff_members[0].id,
                owner_name=staff_members[0].name,
                vehicle_type=VehicleTypeEnum.CAR,
                color="Black",
                make="Honda",
                model="Accord"
            ),
            Vehicle(
                license_plate="MOT-456",
                owner_type=OwnerTypeEnum.STUDENT,
                owner_id=students[1].id,
                owner_name=students[1].name,
                vehicle_type=VehicleTypeEnum.MOTORCYCLE,
                color="Red",
                make="Yamaha",
                model="R15"
            )
        ]
        for vehicle in vehicles:
            session.add(vehicle)
        
        session.commit()
        print("Database initialized successfully!")
        print("\nSample Security Staff Credentials:")
        print("  Email: john.smith@campus.edu")
        print("  Password: password123")
        print("  Role: Security Officer")
        print("\nSample Registered Vehicles:")
        print("  ABC-123 (Blue Toyota Camry - Student)")
        print("  XYZ-789 (Black Honda Accord - Staff)")
        print("  MOT-456 (Red Yamaha R15 - Student)")