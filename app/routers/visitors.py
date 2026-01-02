from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.services.auth_service import AuthService
from app.services.visitor_service import VisitorService
from app.schemas.visitor import CreateVisitorPassRequest
from app.schemas.common import SuccessResponse
from app.models.security_staff import SecurityStaff

router = APIRouter(prefix="/visitors", tags=["Visitors"])

@router.post("/passes", response_model=SuccessResponse, status_code=201)
async def create_pass(pass_data: CreateVisitorPassRequest, session: Session = Depends(get_session), user: SecurityStaff = Depends(AuthService.get_current_user)):
    res = VisitorService.create_pass(session, pass_data, user)
    return {"status": "success", "data": res.model_dump()}

@router.get("/passes", response_model=SuccessResponse)
async def list_passes(session: Session = Depends(get_session), user: SecurityStaff = Depends(AuthService.get_current_user)):
    visitors = VisitorService.list_passes(session)
    data = [{"passId": v.id, "visitorName": v.name, "purpose": v.purpose, "hostName": v.host.name, "validFrom": v.valid_from.isoformat() + "Z", "validUntil": v.valid_until.isoformat() + "Z", "createdAt": v.created_at.isoformat() + "Z"} for v in visitors]
    return {"status": "success", "data": {"visitors": data}}
