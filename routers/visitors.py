"""
Visitor pass API endpoints
Dashboard endpoints - authentication required
"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from auth import get_current_user
from schemas import (
    CreateVisitorPassRequest, VisitorPassResponse,
    HostInfo, GateInfo, QRCodeInfo, CreatedByInfo, SuccessResponse
)
from models import SecurityStaff, Visitor, StaffMember, Gate
import uuid
import json

router = APIRouter(prefix="/visitors", tags=["Visitors"])


def generate_visitor_id() -> str:
    """Generate a unique visitor pass ID"""
    return f"vis_pass_{uuid.uuid4().hex[:10]}"


def generate_qr_code(visitor_id: str) -> str:
    """Generate QR code content for visitor pass"""
    # In production, this would be more sophisticated
    return f"QR-VIS-2026-{visitor_id.upper()}"


@router.post("/passes", response_model=SuccessResponse, status_code=201)
async def create_visitor_pass(
    pass_data: CreateVisitorPassRequest,
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    Create a new visitor pass with QR code
    
    Requires authentication
    """
    # Validation
    errors = []
    
    # Check time validity
    if pass_data.validUntil <= pass_data.validFrom:
        errors.append({
            "field": "validUntil",
            "message": "End time must be after start time"
        })
    
    # Check if validFrom is in the future or within last hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    if pass_data.validFrom < one_hour_ago:
        errors.append({
            "field": "validFrom",
            "message": "Start time must be in the future or within the last hour"
        })
    
    # Check maximum duration (24 hours)
    duration = pass_data.validUntil - pass_data.validFrom
    if duration > timedelta(hours=24):
        errors.append({
            "field": "validUntil",
            "message": "Maximum pass duration is 24 hours"
        })
    
    # Verify host employee exists and is active
    statement = select(StaffMember).where(StaffMember.id == pass_data.hostEmployeeId)
    host_staff = session.exec(statement).first()
    
    if not host_staff:
        errors.append({
            "field": "hostEmployeeId",
            "message": "Employee not found or inactive"
        })
    elif host_staff.employment_status.value != "active":
        errors.append({
            "field": "hostEmployeeId",
            "message": "Host employee is not active"
        })
    
    # Verify allowed gates exist
    if pass_data.allowedGates:
        for gate_id in pass_data.allowedGates:
            gate = session.get(Gate, gate_id)
            if not gate:
                errors.append({
                    "field": "allowedGates",
                    "message": f"Gate '{gate_id}' not found"
                })
                break
    
    # Return validation errors if any
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors
            }
        )
    
    # Generate visitor pass
    visitor_id = generate_visitor_id()
    qr_code_content = generate_qr_code(visitor_id)
    
    # In production, generate actual QR code image
    qr_code_image_url = f"https://cdn.campus-security.example.com/qrcodes/{visitor_id}.png"
    qr_code_base64 = "iVBORw0KGgoAAAANSUhEUgAA..."  # Placeholder
    
    # Store allowed gates as JSON if provided
    allowed_gates_json = None
    if pass_data.allowedGates:
        allowed_gates_json = json.dumps(pass_data.allowedGates)
    
    # Create visitor record
    visitor = Visitor(
        id=visitor_id,
        name=pass_data.visitorName,
        email=pass_data.visitorEmail,
        phone=pass_data.visitorPhone,
        purpose=pass_data.purpose,
        host_staff_id=pass_data.hostEmployeeId,
        qr_code=qr_code_content,
        qr_code_image_url=qr_code_image_url,
        valid_from=pass_data.validFrom,
        valid_until=pass_data.validUntil,
        allowed_gates=allowed_gates_json,
        notes=pass_data.notes,
        created_by_staff_id=current_user.id
    )
    
    session.add(visitor)
    session.commit()
    session.refresh(visitor)
    
    # Build response
    # Get host info
    host_info = HostInfo(
        employeeId=host_staff.id,
        name=host_staff.name,
        department=host_staff.department.name if host_staff.department else None,
        email=host_staff.email
    )
    
    # Get allowed gates info
    allowed_gates_list: List[GateInfo] = []
    if pass_data.allowedGates:
        for gate_id in pass_data.allowedGates:
            gate = session.get(Gate, gate_id)
            if gate:
                allowed_gates_list.append(GateInfo(id=gate.id, name=gate.name))
    else:
        # If no gates specified, return all gates
        all_gates = session.exec(select(Gate)).all()
        for gate in all_gates:
            allowed_gates_list.append(GateInfo(id=gate.id, name=gate.name))
    
    qr_code_info = QRCodeInfo(
        content=qr_code_content,
        imageUrl=qr_code_image_url,
        imageBase64=qr_code_base64
    )
    
    created_by_info = CreatedByInfo(
        id=current_user.id,
        name=current_user.name
    )
    
    response_data = VisitorPassResponse(
        passId=visitor_id,
        visitorName=visitor.name,
        visitorEmail=visitor.email,
        visitorPhone=visitor.phone,
        purpose=visitor.purpose,
        host=host_info,
        validFrom=visitor.valid_from,
        validUntil=visitor.valid_until,
        allowedGates=allowed_gates_list,
        qrCode=qr_code_info,
        createdAt=visitor.created_at,
        createdBy=created_by_info
    )
    
    # In production, send email notifications here
    
    return {
        "status": "success",
        "data": response_data.model_dump()
    }


@router.get("/passes", response_model=SuccessResponse)
async def list_visitor_passes(
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    List all visitor passes
    
    Requires authentication
    """
    statement = select(Visitor).order_by(Visitor.created_at.desc())
    visitors = session.exec(statement).all()
    
    visitor_list = []
    for visitor in visitors:
        visitor_list.append({
            "passId": visitor.id,
            "visitorName": visitor.name,
            "purpose": visitor.purpose,
            "hostName": visitor.host.name,
            "validFrom": visitor.valid_from.isoformat() + "Z",
            "validUntil": visitor.valid_until.isoformat() + "Z",
            "createdAt": visitor.created_at.isoformat() + "Z"
        })
    
    return {
        "status": "success",
        "data": {
            "visitors": visitor_list
        }
    }
