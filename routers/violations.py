"""
Violations API endpoints
Dashboard endpoints - authentication required
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, or_
from database import get_session
from auth import get_current_user
from schemas import SuccessResponse, ViolationsListResponse, ViolationItem, ViolationSubject, ViolationResolvedBy, PaginationInfo
from models import SecurityStaff, Violation, Gate, Student, StaffMember, Visitor, ViolationTypeEnum, SubjectTypeEnum
import json
import math

router = APIRouter(prefix="/violations", tags=["Violations"])


@router.get("", response_model=SuccessResponse)
async def list_violations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by violation type"),
    subjectType: Optional[str] = Query(None, description="Filter by subject type"),
    gateId: Optional[str] = Query(None, description="Filter by gate ID"),
    startDate: Optional[datetime] = Query(None, description="Filter from this date"),
    endDate: Optional[datetime] = Query(None, description="Filter until this date"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    List violation history with optional filters
    
    Requires authentication
    """
    # Build query
    query = select(Violation)
    
    # Apply filters
    if type:
        try:
            violation_type = ViolationTypeEnum(type)
            query = query.where(Violation.type == violation_type)
        except ValueError:
            pass
    
    if subjectType:
        try:
            subject_type_enum = SubjectTypeEnum(subjectType)
            query = query.where(Violation.subject_type == subject_type_enum)
        except ValueError:
            pass
    
    if gateId:
        query = query.where(Violation.gate_id == gateId)
    
    if startDate:
        query = query.where(Violation.occurred_at >= startDate)
    
    if endDate:
        query = query.where(Violation.occurred_at <= endDate)
    
    if resolved is not None:
        query = query.where(Violation.resolved == resolved)
    
    # Order by most recent first
    query = query.order_by(Violation.occurred_at.desc())
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total_items = session.exec(count_query).one()
    
    # Calculate pagination
    total_pages = math.ceil(total_items / limit)
    offset = (page - 1) * limit
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    violations = session.exec(query).all()
    
    # Build response
    violation_items = []
    for violation in violations:
        # Get gate info
        gate = session.get(Gate, violation.gate_id)
        gate_name = gate.name if gate else "Unknown Gate"
        
        # Get subject info
        subject_data = None
        if violation.subject_type and violation.subject_type != "":
            if violation.subject_type == SubjectTypeEnum.STUDENT and violation.student_id:
                student = session.get(Student, violation.student_id)
                if student:
                    subject_data = ViolationSubject(
                        id=student.id,
                        name=student.name,
                        photoUrl=student.photo_url
                    )
            elif violation.subject_type == SubjectTypeEnum.STAFF and violation.staff_id:
                staff = session.get(StaffMember, violation.staff_id)
                if staff:
                    subject_data = ViolationSubject(
                        id=staff.id,
                        name=staff.name,
                        photoUrl=staff.photo_url
                    )
            elif violation.subject_type == SubjectTypeEnum.VISITOR and violation.visitor_id:
                visitor = session.get(Visitor, violation.visitor_id)
                if visitor:
                    subject_data = ViolationSubject(
                        id=visitor.id,
                        name=visitor.name,
                        photoUrl=visitor.photo_url
                    )
        
        # Parse details JSON
        details_dict = {}
        if violation.details:
            try:
                details_dict = json.loads(violation.details)
            except json.JSONDecodeError:
                pass
        
        # Add additional detail fields
        if violation.scanned_qr_code:
            details_dict["scannedQrCode"] = violation.scanned_qr_code
        if violation.captured_image_url:
            details_dict["capturedImageUrl"] = violation.captured_image_url
        if violation.confidence_score is not None:
            details_dict["confidence"] = violation.confidence_score
        
        # Get resolved by info
        resolved_by_data = None
        if violation.resolved_by_staff_id:
            resolved_by_staff = session.get(SecurityStaff, violation.resolved_by_staff_id)
            if resolved_by_staff:
                resolved_by_data = ViolationResolvedBy(
                    id=resolved_by_staff.id,
                    name=resolved_by_staff.name
                )
        
        violation_item = ViolationItem(
            id=violation.id,
            type=violation.type.value,
            subjectType=violation.subject_type.value if violation.subject_type else None,
            subject=subject_data,
            gateId=violation.gate_id,
            gateName=gate_name,
            occurredAt=violation.occurred_at,
            details=details_dict,
            resolved=violation.resolved,
            resolvedAt=violation.resolved_at,
            resolvedBy=resolved_by_data,
            notes=violation.resolution_notes
        )
        violation_items.append(violation_item)
    
    # Build pagination info
    pagination = PaginationInfo(
        currentPage=page,
        totalPages=total_pages,
        totalItems=total_items,
        itemsPerPage=limit,
        hasNextPage=page < total_pages,
        hasPreviousPage=page > 1
    )
    
    response_data = ViolationsListResponse(
        violations=violation_items,
        pagination=pagination
    )
    
    return {
        "status": "success",
        "data": response_data.model_dump()
    }


@router.patch("/{violation_id}/resolve", response_model=SuccessResponse)
async def resolve_violation(
    violation_id: str,
    notes: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    Mark a violation as resolved
    
    Requires authentication
    """
    violation = session.get(Violation, violation_id)
    
    if not violation:
        return {
            "status": "error",
            "code": "NOT_FOUND",
            "message": "Violation not found"
        }
    
    if violation.resolved:
        return {
            "status": "error",
            "code": "ALREADY_RESOLVED",
            "message": "Violation is already resolved"
        }
    
    # Mark as resolved
    violation.resolved = True
    violation.resolved_at = datetime.utcnow()
    violation.resolved_by_staff_id = current_user.id
    violation.resolution_notes = notes
    
    session.add(violation)
    session.commit()
    session.refresh(violation)
    
    return {
        "status": "success",
        "data": {
            "violationId": violation_id,
            "resolved": True,
            "resolvedAt": violation.resolved_at.isoformat() + "Z",
            "resolvedBy": {
                "id": current_user.id,
                "name": current_user.name
            },
            "notes": notes
        }
    }
