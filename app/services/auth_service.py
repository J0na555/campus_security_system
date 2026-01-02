from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.core.config import settings
from app.core.database import get_session
from app.models.security_staff import SecurityStaff

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class AuthService:
    @staticmethod
    def verify_password(plain, hashed):
        return pwd_context.verify(plain, hashed)

    @staticmethod
    def create_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
        try:
            payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if not user_id: raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError: raise HTTPException(status_code=401, detail="Invalid token")
        
        user = session.exec(select(SecurityStaff).where(SecurityStaff.id == user_id)).first()
        if not user or not user.is_active: raise HTTPException(status_code=401, detail="User not found or inactive")
        return user

    @staticmethod
    def authenticate(session: Session, employee_id: str, password: str):
        user = session.exec(select(SecurityStaff).where(SecurityStaff.employee_id == employee_id)).first()
        if user and AuthService.verify_password(password, user.password_hash):
            user.last_login_at = datetime.utcnow()
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        return None
