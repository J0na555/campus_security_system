from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.schemas.scan import QRScanRequest, FaceVerifyRequest
from app.schemas.common import SuccessResponse
from app.services.qr_service import QRService
from app.services.visitor_qr_service import VisitorQRService
from app.services.face_match_service import FaceMatchService

router = APIRouter(prefix="/scan", tags=["Gate Scanning"])

@router.post("/qr", response_model=SuccessResponse)
async def scan_qr(scan_data: QRScanRequest, session: Session = Depends(get_session)):
    QRService.validate_gate(session, scan_data.gateId)
    
    res = QRService.check_student(session, scan_data.qrCode)
    if res: return {"status": "success", "data": res}
    
    res = QRService.check_staff(session, scan_data.qrCode)
    if res: return {"status": "success", "data": res}
    
    res = VisitorQRService.check_visitor(session, scan_data.qrCode, scan_data.gateId, scan_data.scanTimestamp)
    if res: return {"status": "success", "data": res}
    
    res = await QRService.handle_unauthorized_qr(session, scan_data.qrCode, scan_data.gateId, scan_data.scanTimestamp)
    return {"status": "success", "data": res}

@router.post("/face/verify", response_model=SuccessResponse)
async def verify_face(verify_data: FaceVerifyRequest, session: Session = Depends(get_session)):
    res = FaceMatchService.verify(session, verify_data.subjectId, verify_data.subjectType, verify_data.gateId, verify_data.scanTimestamp)
    return {"status": "success", "data": res}
