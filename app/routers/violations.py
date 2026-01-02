from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.core.database import get_session
from app.services.auth_service import AuthService
from app.services.violation_service import ViolationService
from app.schemas.common import SuccessResponse
from app.models.security_staff import SecurityStaff

router = APIRouter(prefix="/violations", tags=["Violations"])

@router.get("", response_model=SuccessResponse)
async def list_violations(
    page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = None, subjectType: Optional[str] = None,
    gateId: Optional[str] = None, startDate: Optional[datetime] = None,
    endDate: Optional[datetime] = None, resolved: Optional[bool] = None,
    session: Session = Depends(get_session),
    user: SecurityStaff = Depends(AuthService.get_current_user)
):
    filters = {"type": type, "subjectType": subjectType, "gateId": gateId, "startDate": startDate, "endDate": endDate, "resolved": resolved}
    items, pagination = ViolationService.list_violations(session, page, limit, filters)
    return {"status": "success", "data": {"violations": [i.model_dump() for i in items], "pagination": pagination.model_dump()}}

@router.patch("/{violation_id}/resolve", response_model=SuccessResponse)
async def resolve(violation_id: str, notes: Optional[str] = None, session: Session = Depends(get_session), user: SecurityStaff = Depends(AuthService.get_current_user)):
    v = ViolationService.resolve(session, violation_id, notes, user)
    if not v: return {"status": "error", "code": "NOT_FOUND", "message": "Violation not found or already resolved"}
    return {"status": "success", "data": {"violationId": violation_id, "resolved": True}}
