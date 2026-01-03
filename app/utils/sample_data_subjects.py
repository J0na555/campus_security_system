from sqlmodel import Session
from app.models.student import Student
from app.models.staff import StaffMember
from app.models.vehicle import Vehicle
from app.models.enums import (
    EnrollmentStatusEnum, EmploymentStatusEnum, 
    OwnerTypeEnum, VehicleTypeEnum
)

def create_students(session: Session, departments):
    students = [
        Student(id="stu_789xyz", name="Alice Johnson", 
                email="alice.johnson@student.campus.edu",
                department_id=departments[0].id, qr_code="QR-STU-2024-ABC123XYZ"),
        Student(id="stu_456abc", name="Bob Williams", 
                email="bob.williams@student.campus.edu",
                department_id=departments[1].id, qr_code="QR-STU-2024-DEF456ABC"),
        Student(id="stu_111aaa", name="Charlie Davis", 
                email="charlie.davis@student.campus.edu",
                department_id=departments[0].id, qr_code="QR-STU-2024-GHI789XYZ"),
        Student(id="stu_222bbb", name="Diana Martinez", 
                email="diana.martinez@student.campus.edu",
                department_id=departments[2].id, qr_code="QR-STU-2024-JKL012ABC"),
        Student(id="stu_333ccc", name="Ethan Wilson", 
                email="ethan.wilson@student.campus.edu",
                department_id=departments[1].id, qr_code="QR-STU-2024-MNO345DEF")
    ]
    for student in students:
        session.add(student)
    return students

def create_staff_members(session: Session, departments):
    staff_members = [
        StaffMember(id="stf_456abc", name="Dr. Robert Chen", 
                    email="robert.chen@campus.edu", department_id=departments[1].id,
                    position="Professor", qr_code="QR-STF-2024-XYZ789ABC"),
        StaffMember(id="stf_789xyz", name="Jane Doe", 
                    email="jane.doe@campus.edu", department_id=departments[3].id,
                    position="HR Manager", qr_code="QR-STF-2024-JKL012DEF"),
        StaffMember(id="stf_111aaa", name="Dr. Sarah Thompson", 
                    email="sarah.thompson@campus.edu", department_id=departments[0].id,
                    position="Associate Professor", qr_code="QR-STF-2024-PQR678GHI"),
        StaffMember(id="stf_222bbb", name="Mark Johnson", 
                    email="mark.johnson@campus.edu", department_id=departments[2].id,
                    position="Department Head", qr_code="QR-STF-2024-STU901JKL")
    ]
    for staff in staff_members:
        session.add(staff)
    return staff_members

def create_vehicles(session: Session, students, staff_members):
    vehicles = [
        Vehicle(license_plate="ABC-123", owner_type=OwnerTypeEnum.STUDENT,
                owner_id=students[0].id, owner_name=students[0].name,
                vehicle_type=VehicleTypeEnum.CAR, make="Toyota", model="Camry"),
        Vehicle(license_plate="XYZ-789", owner_type=OwnerTypeEnum.STAFF,
                owner_id=staff_members[0].id, owner_name=staff_members[0].name,
                vehicle_type=VehicleTypeEnum.CAR, make="Honda", model="Accord"),
        Vehicle(license_plate="MOT-456", owner_type=OwnerTypeEnum.STUDENT,
                owner_id=students[1].id, owner_name=students[1].name,
                vehicle_type=VehicleTypeEnum.MOTORCYCLE, make="Yamaha", model="R15")
    ]
    for vehicle in vehicles:
        session.add(vehicle)
    return vehicles
