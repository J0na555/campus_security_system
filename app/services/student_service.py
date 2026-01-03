import os
import base64
import secrets
from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.student import Student
from app.models.department import Department
from app.models.enums import EnrollmentStatusEnum

class StudentService:
    PHOTO_DIR = "student_photos"
    
    @staticmethod
    def _ensure_photo_directory():
        if not os.path.exists(StudentService.PHOTO_DIR):
            os.makedirs(StudentService.PHOTO_DIR)
    
    @staticmethod
    def _generate_student_id() -> str:
        return f"stu_{secrets.token_hex(4)}"
    
    @staticmethod
    def _generate_qr_code(student_id: str) -> str:
        unique_part = secrets.token_hex(6).upper()
        return f"QR-STU-{datetime.utcnow().year}-{unique_part}"
    
    @staticmethod
    def _decode_base64_image(base64_string: str) -> tuple:
        try:
            if base64_string.startswith('data:'):
                header, encoded = base64_string.split(',', 1)
                image_type = header.split(';')[0].split('/')[1]
                extension = image_type if image_type in ['jpg', 'jpeg', 'png', 'gif'] else 'jpg'
            else:
                encoded = base64_string
                extension = 'jpg'
            image_bytes = base64.b64decode(encoded)
            return image_bytes, extension
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image format: {str(e)}")
    
    @staticmethod
    def _save_image_file(image_bytes: bytes, student_id: str, extension: str) -> str:
        StudentService._ensure_photo_directory()
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{student_id}_{timestamp}.{extension}"
        filepath = os.path.join(StudentService.PHOTO_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        photo_url = f"https://cdn.campus-security.example.com/photos/{filename}"
        return photo_url
    
    @staticmethod
    def create_student(session: Session, data: dict) -> dict:
        existing = session.exec(select(Student).where(Student.email == data.get('email'))).first()
        if existing:
            raise HTTPException(status_code=400, detail={"status": "error", "code": "EMAIL_EXISTS", "message": "A student with this email already exists"})
        
        department = None
        if data.get('departmentId'):
            department = session.exec(select(Department).where(Department.id == data['departmentId'])).first()
            if not department:
                raise HTTPException(status_code=404, detail={"status": "error", "code": "DEPARTMENT_NOT_FOUND", "message": "Department not found"})
        
        student_id = StudentService._generate_student_id()
        qr_code = data.get('qrCode') or StudentService._generate_qr_code(student_id)
        
        existing_qr = session.exec(select(Student).where(Student.qr_code == qr_code)).first()
        if existing_qr:
            raise HTTPException(status_code=400, detail={"status": "error", "code": "QR_CODE_EXISTS", "message": "This QR code is already in use"})
        
        photo_url = None
        if data.get('photo'):
            image_bytes, extension = StudentService._decode_base64_image(data['photo'])
            photo_url = StudentService._save_image_file(image_bytes, student_id, extension)
        
        student = Student(
            id=student_id,
            name=data['name'],
            email=data['email'],
            photo_url=photo_url,
            department_id=data.get('departmentId'),
            qr_code=qr_code,
            enrollment_status=EnrollmentStatusEnum.ACTIVE
        )
        
        session.add(student)
        session.commit()
        session.refresh(student)
        
        return StudentService._format_student_response(student, department)
    
    @staticmethod
    def get_students(session: Session, page: int = 1, limit: int = 20) -> dict:
        offset = (page - 1) * limit
        total_query = select(Student)
        total_count = len(session.exec(total_query).all())
        query = select(Student).offset(offset).limit(limit)
        students = session.exec(query).all()
        
        students_data = []
        for student in students:
            department = None
            if student.department_id:
                department = session.exec(select(Department).where(Department.id == student.department_id)).first()
            students_data.append(StudentService._format_student_response(student, department))
        
        return {
            "students": students_data,
            "pagination": {
                "currentPage": page,
                "totalPages": (total_count + limit - 1) // limit,
                "totalItems": total_count,
                "itemsPerPage": limit,
                "hasNextPage": offset + limit < total_count,
                "hasPreviousPage": page > 1
            }
        }
    
    @staticmethod
    def get_student(session: Session, student_id: str) -> dict:
        student = session.exec(select(Student).where(Student.id == student_id)).first()
        if not student:
            raise HTTPException(status_code=404, detail={"status": "error", "code": "STUDENT_NOT_FOUND", "message": f"Student with ID '{student_id}' not found"})
        
        department = None
        if student.department_id:
            department = session.exec(select(Department).where(Department.id == student.department_id)).first()
        
        return StudentService._format_student_response(student, department)
    
    @staticmethod
    def update_student(session: Session, student_id: str, data: dict) -> dict:
        student = session.exec(select(Student).where(Student.id == student_id)).first()
        if not student:
            raise HTTPException(status_code=404, detail={"status": "error", "code": "STUDENT_NOT_FOUND", "message": f"Student with ID '{student_id}' not found"})
        
        if data.get('name'):
            student.name = data['name']
        
        if data.get('email'):
            existing = session.exec(select(Student).where(Student.email == data['email'], Student.id != student_id)).first()
            if existing:
                raise HTTPException(status_code=400, detail={"status": "error", "code": "EMAIL_EXISTS", "message": "A student with this email already exists"})
            student.email = data['email']
        
        if data.get('departmentId') is not None:
            if data['departmentId']:
                department = session.exec(select(Department).where(Department.id == data['departmentId'])).first()
                if not department:
                    raise HTTPException(status_code=404, detail={"status": "error", "code": "DEPARTMENT_NOT_FOUND", "message": "Department not found"})
            student.department_id = data['departmentId']
        
        if data.get('qrCode'):
            existing_qr = session.exec(select(Student).where(Student.qr_code == data['qrCode'], Student.id != student_id)).first()
            if existing_qr:
                raise HTTPException(status_code=400, detail={"status": "error", "code": "QR_CODE_EXISTS", "message": "This QR code is already in use"})
            student.qr_code = data['qrCode']
        
        if data.get('enrollmentStatus'):
            try:
                student.enrollment_status = EnrollmentStatusEnum(data['enrollmentStatus'])
            except ValueError:
                raise HTTPException(status_code=400, detail={"status": "error", "code": "INVALID_STATUS", "message": "Invalid enrollment status"})
        
        student.updated_at = datetime.utcnow()
        session.add(student)
        session.commit()
        session.refresh(student)
        
        department = None
        if student.department_id:
            department = session.exec(select(Department).where(Department.id == student.department_id)).first()
        
        return StudentService._format_student_response(student, department)
    
    @staticmethod
    def enroll_photo(session: Session, student_id: str, photo_base64: str) -> dict:
        student = session.exec(select(Student).where(Student.id == student_id)).first()
        if not student:
            raise HTTPException(status_code=404, detail={"status": "error", "code": "STUDENT_NOT_FOUND", "message": f"Student with ID '{student_id}' not found"})
        
        image_bytes, extension = StudentService._decode_base64_image(photo_base64)
        photo_url = StudentService._save_image_file(image_bytes, student_id, extension)
        
        student.photo_url = photo_url
        student.updated_at = datetime.utcnow()
        session.add(student)
        session.commit()
        session.refresh(student)
        
        return {
            "studentId": student.id,
            "photoUrl": student.photo_url
        }
    
    @staticmethod
    def _format_student_response(student: Student, department: Optional[Department] = None) -> dict:
        return {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "photoUrl": student.photo_url,
            "departmentId": student.department_id,
            "department": department.name if department else None,
            "enrollmentStatus": student.enrollment_status.value,
            "qrCode": student.qr_code,
            "enrolledAt": student.enrolled_at,
            "createdAt": student.created_at,
            "updatedAt": student.updated_at
        }
