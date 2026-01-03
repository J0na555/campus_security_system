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
    from app.models.staff import StaffMember
    from sqlmodel import select
    
    visitors = VisitorService.list_passes(session)
    data = []
    for v in visitors:
        # Fetch host name directly from database to avoid relationship loading issues
        host_name = "Unknown"
        if v.host_staff_id:
            host = session.get(StaffMember, v.host_staff_id)
            if host:
                host_name = host.name
        
        data.append({
            "passId": v.id,
            "visitorName": v.name,
            "visitorEmail": v.email,
            "visitorPhoto": v.photo_url,
            "purpose": v.purpose,
            "hostName": host_name,
            "validFrom": v.valid_from.isoformat() + "Z",
            "validUntil": v.valid_until.isoformat() + "Z",
            "createdAt": v.created_at.isoformat() + "Z"
        })
    return {"status": "success", "data": {"visitors": data}}
