from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.config import settings
from app.schemas.auth import LoginRequest, LoginResponse, UserInfo
from app.schemas.common import SuccessResponse
from app.models.security_staff import SecurityStaff
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=SuccessResponse)
async def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    user = AuthService.authenticate(session, login_data.employeeId, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail={"status": "error", "code": "INVALID_CREDENTIALS", "message": "Invalid ID or password"})
    
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = AuthService.create_token({"sub": user.id}, expires)
    
    user_info = UserInfo(id=user.id, employeeId=user.employee_id, name=user.name, email=user.email, role=user.role.value)
    return {"status": "success", "data": LoginResponse(token=token, expiresAt=datetime.utcnow() + expires, user=user_info).model_dump()}

@router.get("/me", response_model=SuccessResponse)
async def me(current_user: SecurityStaff = Depends(AuthService.get_current_user)):
    user_info = UserInfo(
        id=current_user.id, employeeId=current_user.employee_id, name=current_user.name, 
        email=current_user.email, role=current_user.role.value, department=current_user.department,
        createdAt=current_user.created_at, lastLoginAt=current_user.last_login_at
    )
    return {"status": "success", "data": user_info.model_dump()}
