import os
import base64
import hashlib
from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.student import Student
from app.core.config import settings

class StudentService:
    # Directory to store student photos
    PHOTO_DIR = "student_photos"
    
    @staticmethod
    def _ensure_photo_directory():
        """Ensure the photo storage directory exists"""
        if not os.path.exists(StudentService.PHOTO_DIR):
            os.makedirs(StudentService.PHOTO_DIR)
    
    @staticmethod
    def _decode_base64_image(base64_string: str) -> tuple[bytes, str]:
        """
        Decode base64 image string and return image bytes and extension
        
        Args:
            base64_string: Base64 encoded image (with or without data URI prefix)
            
        Returns:
            tuple: (image_bytes, file_extension)
        """
        try:
            # Remove data URI prefix if present (e.g., "data:image/jpeg;base64,")
            if base64_string.startswith('data:'):
                # Extract the image type and base64 data
                header, encoded = base64_string.split(',', 1)
                # Extract image format from header (e.g., "image/jpeg" -> "jpeg")
                image_type = header.split(';')[0].split('/')[1]
                extension = image_type if image_type in ['jpg', 'jpeg', 'png', 'gif'] else 'jpg'
            else:
                encoded = base64_string
                extension = 'jpg'  # default extension
            
            # Decode base64 string
            image_bytes = base64.b64decode(encoded)
            return image_bytes, extension
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image format: {str(e)}")
    
    @staticmethod
    def _save_image_file(image_bytes: bytes, student_id: str, extension: str) -> str:
        """
        Save image bytes to file and return the file path/URL
        
        Args:
            image_bytes: Raw image bytes
            student_id: Student ID for naming the file
            extension: File extension (jpg, png, etc.)
            
        Returns:
            str: Photo URL/path
        """
        StudentService._ensure_photo_directory()
        
        # Generate a unique filename using student_id and timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{student_id}_{timestamp}.{extension}"
        filepath = os.path.join(StudentService.PHOTO_DIR, filename)
        
        # Write image bytes to file
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # In production, this would be a CDN URL
        # For now, return a relative path that could be served by the backend
        photo_url = f"https://cdn.campus-security.example.com/photos/{filename}"
        
        return photo_url
    
    @staticmethod
    def enroll_photo(session: Session, student_id: str, photo_base64: str) -> dict:
        """
        Enroll or update a student's photo for face verification
        
        Args:
            session: Database session
            student_id: Student ID
            photo_base64: Base64 encoded photo string
            
        Returns:
            dict: Response data with studentId and photoUrl
            
        Raises:
            HTTPException: If student not found or invalid image
        """
        # Verify student exists
        student = session.exec(select(Student).where(Student.id == student_id)).first()
        if not student:
            raise HTTPException(
                status_code=404, 
                detail={"status": "error", "code": "STUDENT_NOT_FOUND", "message": f"Student with ID '{student_id}' not found"}
            )
        
        # Decode and validate base64 image
        image_bytes, extension = StudentService._decode_base64_image(photo_base64)
        
        # Save image file and get URL
        photo_url = StudentService._save_image_file(image_bytes, student_id, extension)
        
        # Update student record with new photo URL
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
    def get_student_photo(session: Session, student_id: str) -> Optional[str]:
        """
        Get the enrolled photo URL for a student
        
        Args:
            session: Database session
            student_id: Student ID
            
        Returns:
            Optional[str]: Photo URL if exists, None otherwise
        """
        student = session.exec(select(Student).where(Student.id == student_id)).first()
        if student:
            return student.photo_url
        return None
