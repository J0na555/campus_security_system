from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.student import (
    EnrollPhotoRequest, EnrollPhotoResponse, 
    CreateStudentRequest, UpdateStudentRequest, StudentResponse
)
from app.schemas.common import SuccessResponse
from app.services.student_service import StudentService
from app.services.auth_service import AuthService
from app.models.security_staff import SecurityStaff

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("", response_model=SuccessResponse, status_code=201)
async def create_student(
    request: CreateStudentRequest,
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(AuthService.get_current_user)
):
    """
    Create a new student with optional photo and QR code.
    
    If qrCode is not provided, it will be auto-generated.
    If photo is provided, it will be saved and linked to the student.
    
    Returns:
        201 Created with student data including generated QR code
    """
    result = StudentService.create_student(
        session=session,
        data=request.model_dump(exclude_none=True)
    )
    
    return {
        "status": "success",
        "data": result
    }

@router.get("", response_model=SuccessResponse)
async def list_students(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(AuthService.get_current_user)
):
    """Get list of students with pagination."""
    result = StudentService.get_students(session=session, page=page, limit=limit)
    
    return {
        "status": "success",
        "data": result
    }

@router.get("/{student_id}", response_model=SuccessResponse)
async def get_student(
    student_id: str,
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(AuthService.get_current_user)
):
    """Get a single student by ID."""
    result = StudentService.get_student(session=session, student_id=student_id)
    
    return {
        "status": "success",
        "data": result
    }

@router.patch("/{student_id}", response_model=SuccessResponse)
async def update_student(
    student_id: str,
    request: UpdateStudentRequest,
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(AuthService.get_current_user)
):
    """Update a student's information (including QR code)."""
    result = StudentService.update_student(
        session=session,
        student_id=student_id,
        data=request.model_dump(exclude_none=True)
    )
    
    return {
        "status": "success",
        "data": result
    }

@router.post("/enroll-photo", response_model=SuccessResponse)
async def enroll_student_photo(
    request: EnrollPhotoRequest,
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(AuthService.get_current_user)
):
    """
    Enroll or update a student's base photo for face verification.
    
    This endpoint allows authenticated security staff to add or update the photo
    that will be used as the reference for face verification at gates.
    
    Args:
        request: Contains studentId and base64 encoded photo
        session: Database session
        current_user: Authenticated security staff user
        
    Returns:
        SuccessResponse with studentId and photoUrl
        
    Raises:
        404: Student not found
        400: Invalid image format
        401: Unauthorized (no valid token)
    """
    result = StudentService.enroll_photo(
        session=session,
        student_id=request.studentId,
        photo_base64=request.photo
    )
    
    return {
        "status": "success",
        "data": result
    }
