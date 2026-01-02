"""
Authentication API endpoints
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from database import get_session
from auth import authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas import LoginRequest, LoginResponse, UserInfo, SuccessResponse, ErrorResponse
from models import SecurityStaff

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=SuccessResponse)
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login with employee credentials
    
    Returns JWT token and user information
    """
    user = authenticate_user(session, login_data.employeeId, login_data.password)
    
    if not user:
        # Check if account is locked
        from sqlmodel import select
        statement = select(SecurityStaff).where(SecurityStaff.employee_id == login_data.employeeId)
        check_user = session.exec(statement).first()
        
        if check_user and check_user.locked_until and check_user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail={
                    "status": "error",
                    "code": "ACCOUNT_LOCKED",
                    "message": "Account locked due to multiple failed attempts. Try again in 15 minutes."
                }
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid employee ID or password"
            }
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": "error",
                "code": "ACCOUNT_INACTIVE",
                "message": "Account is inactive"
            }
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.utcnow() + access_token_expires
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    # Prepare response
    user_info = UserInfo(
        id=user.id,
        employeeId=user.employee_id,
        name=user.name,
        email=user.email,
        role=user.role.value
    )
    
    response_data = LoginResponse(
        token=access_token,
        expiresAt=expires_at,
        user=user_info
    )
    
    return {
        "status": "success",
        "data": response_data.model_dump()
    }


@router.get("/me", response_model=SuccessResponse)
async def get_current_user_info(
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    Get current authenticated user information
    
    Requires valid JWT token in Authorization header
    """
    user_info = UserInfo(
        id=current_user.id,
        employeeId=current_user.employee_id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        department=current_user.department,
        createdAt=current_user.created_at,
        lastLoginAt=current_user.last_login_at
    )
    
    return {
        "status": "success",
        "data": user_info.model_dump()
    }
