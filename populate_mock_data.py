#!/usr/bin/env python3
"""
Standalone script to populate database with comprehensive mock data for frontend testing.

Usage:
    python populate_mock_data.py

This script will:
- Add admin users (login credentials below)
- Add students, staff, visitors
- Add violations for dashboard testing
- Add vehicle entries and alerts

Admin Login Credentials:admin123
- Employee ID: ADMIN-001, Password: admin123
- Employee ID: ADMIN-002, Password: admin123
- Employee ID: EMP-2024-003, Password: password123
- Employee ID: SUPER-001, Password: super123
"""

from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
# Import all models to ensure relationships are properly configured
from app.models.gate import Gate
from app.models.department import Department
from app.models.security_staff import SecurityStaff
from app.models.student import Student
from app.models.staff import StaffMember
from app.models.vehicle import Vehicle
from app.models.visitor import Visitor
from app.models.violation import Violation
from app.models.vehicle_entry import VehicleEntry
from app.models.vehicle_alert import VehicleAlert
from app.models.fail_attempt import FailAttempt
from app.utils.sample_data import (
    create_gates, create_departments, create_security_staff
)
from app.utils.sample_data_subjects import (
    create_students, create_staff_members, create_vehicles
)
from app.utils.mock_data import populate_mock_data


def main():
    print("=" * 60)
    print("Campus Security System - Mock Data Population")
    print("=" * 60)
    
    with Session(engine) as session:
        # Check if database needs initialization
        try:
            existing_gate = session.exec(select(Gate)).first()
            existing_dept = session.exec(select(Department)).first()
            existing_staff = session.exec(select(SecurityStaff)).first()
            
            if not existing_gate or not existing_dept or not existing_staff:
                print("\nInitializing database with base data...")
                create_db_and_tables()
                
                gates = create_gates(session)
                departments = create_departments(session)
                session.commit()
                
                staff = create_security_staff(session)
                students = create_students(session, departments)
                staff_members = create_staff_members(session, departments)
                vehicles = create_vehicles(session, students, staff_members)
                session.commit()
                
                print("Base data created successfully!")
            else:
                print("\nDatabase already initialized. Fetching existing data...")
                gates = list(session.exec(select(Gate)).all())
                departments = list(session.exec(select(Department)).all())
                staff = list(session.exec(select(SecurityStaff)).all())
                students = list(session.exec(select(Student)).all())
                staff_members = list(session.exec(select(StaffMember)).all())
                vehicles = list(session.exec(select(Vehicle)).all())
                
                print(f"Found: {len(gates)} gates, {len(departments)} departments, "
                      f"{len(staff)} security staff, {len(students)} students, "
                      f"{len(staff_members)} staff members, {len(vehicles)} vehicles")
                
                # Check if we need to add more admin users
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                from app.models.enums import UserRoleEnum
                
                existing_employee_ids = {s.employee_id for s in staff}
                new_admins = []
                
                if "ADMIN-001" not in existing_employee_ids:
                    new_admins.append(SecurityStaff(
                        id="usr_admin001", employee_id="ADMIN-001", name="Admin User",
                        email="admin@campus.edu", password_hash=pwd_context.hash("admin123"),
                        role=UserRoleEnum.ADMIN, department="IT Administration"
                    ))
                if "ADMIN-002" not in existing_employee_ids:
                    new_admins.append(SecurityStaff(
                        id="usr_admin002", employee_id="ADMIN-002", name="Super Admin",
                        email="superadmin@campus.edu", password_hash=pwd_context.hash("admin123"),
                        role=UserRoleEnum.ADMIN, department="System Administration"
                    ))
                if "SUPER-001" not in existing_employee_ids:
                    new_admins.append(SecurityStaff(
                        id="usr_super001", employee_id="SUPER-001", name="Supervisor One",
                        email="supervisor1@campus.edu", password_hash=pwd_context.hash("super123"),
                        role=UserRoleEnum.SECURITY_SUPERVISOR
                    ))
                
                if new_admins:
                    print(f"\nAdding {len(new_admins)} new admin/supervisor users...")
                    for admin in new_admins:
                        session.add(admin)
                    session.commit()
                    staff.extend(new_admins)
        
        except Exception as e:
            print(f"\nError checking database: {e}")
            print("Initializing fresh database...")
            create_db_and_tables()
            
            gates = create_gates(session)
            departments = create_departments(session)
            session.commit()
            
            staff = create_security_staff(session)
            students = create_students(session, departments)
            staff_members = create_staff_members(session, departments)
            vehicles = create_vehicles(session, students, staff_members)
            session.commit()
        
        # Check if mock data already exists
        existing_visitors = session.exec(select(Visitor).where(Visitor.qr_code.like("QR-VIS-2026-MOCK%"))).all()
        
        if existing_visitors:
            print("\nMock data already exists. Skipping population.")
            print(f"Found {len(existing_visitors)} existing mock visitors.")
        else:
            # Populate comprehensive mock data
            print("\n" + "=" * 60)
            print("Populating comprehensive mock data...")
            print("=" * 60)
            
            populate_mock_data(session, students, staff_members, vehicles, gates, staff)
        
        print("\n" + "=" * 60)
        print("Mock Data Population Complete!")
        print("=" * 60)
        print("\nAdmin Login Credentials:")
        print("  Employee ID: ADMIN-001, Password: admin123")
        print("  Employee ID: ADMIN-002, Password: admin123")
        print("  Employee ID: EMP-2024-003, Password: password123")
        print("  Employee ID: SUPER-001, Password: super123")
        print("\nOther Users:")
        print("  Employee ID: EMP-2024-001, Password: password123 (Security Officer)")
        print("  Employee ID: EMP-2024-002, Password: password123 (Supervisor)")
        print("\nTest QR Codes:")
        print("  Student: QR-STU-2024-ABC123XYZ")
        print("  Staff: QR-STF-2024-XYZ789ABC")
        print("  Visitor: QR-VIS-2026-MOCK001")
        print("=" * 60)


if __name__ == "__main__":
    main()
