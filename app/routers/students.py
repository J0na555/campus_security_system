from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.student import EnrollPhotoRequest, EnrollPhotoResponse
from app.schemas.common import SuccessResponse
from app.services.student_service import StudentService
from app.services.auth_service import AuthService
from app.models.security_staff import SecurityStaff

router = APIRouter(prefix="/students", tags=["Students"])

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
