import json
import math
from datetime import datetime
from typing import Optional, List
from sqlmodel import Session, select, func
from app.models.violation import Violation
from app.models.gate import Gate
from app.models.student import Student
from app.models.staff import StaffMember
from app.models.visitor import Visitor
from app.models.security_staff import SecurityStaff
from app.models.enums import ViolationTypeEnum, SubjectTypeEnum
from app.schemas.violation import ViolationItem, ViolationSubject, ViolationResolvedBy, PaginationInfo

class ViolationService:
    @staticmethod
    def list_violations(session: Session, page: int, limit: int, filters: dict):
        query = ViolationService._build_query(filters)
        total_items = session.exec(select(func.count()).select_from(query.subquery())).one()
        total_pages = math.ceil(total_items / limit)
        violations = session.exec(query.offset((page - 1) * limit).limit(limit)).all()
        
        items = [ViolationService._build_item(session, v) for v in violations]
        pagination = PaginationInfo(
            currentPage=page, totalPages=total_pages, totalItems=total_items,
            itemsPerPage=limit, hasNextPage=page < total_pages, hasPreviousPage=page > 1
        )
        return items, pagination

    @staticmethod
    def _build_query(filters: dict):
        query = select(Violation).order_by(Violation.occurred_at.desc())
        if filters.get("type"): query = query.where(Violation.type == ViolationTypeEnum(filters["type"]))
        if filters.get("subjectType"): query = query.where(Violation.subject_type == SubjectTypeEnum(filters["subjectType"]))
        if filters.get("gateId"): query = query.where(Violation.gate_id == filters["gateId"])
        if filters.get("startDate"): query = query.where(Violation.occurred_at >= filters["startDate"])
        if filters.get("endDate"): query = query.where(Violation.occurred_at <= filters["endDate"])
        if filters.get("resolved") is not None: query = query.where(Violation.resolved == filters["resolved"])
        return query

    @staticmethod
    def _build_item(session: Session, v: Violation):
        gate = session.get(Gate, v.gate_id)
        subject = ViolationService._get_subject(session, v)
        resolved_by = None
        if v.resolved_by_staff_id:
            staff = session.get(SecurityStaff, v.resolved_by_staff_id)
            if staff: resolved_by = ViolationResolvedBy(id=staff.id, name=staff.name)
        
        details = json.loads(v.details) if v.details else {}
        if v.scanned_qr_code: details["scannedQrCode"] = v.scanned_qr_code
        if v.confidence_score is not None: details["confidence"] = v.confidence_score

        return ViolationItem(
            id=v.id, type=v.type.value, subjectType=v.subject_type.value if v.subject_type else None,
            subject=subject, gateId=v.gate_id, gateName=gate.name if gate else "Unknown",
            occurredAt=v.occurred_at, details=details, resolved=v.resolved,
            resolvedAt=v.resolved_at, resolvedBy=resolved_by, notes=v.resolution_notes
        )

    @staticmethod
    def _get_subject(session: Session, v: Violation):
        if not v.subject_type: return None
        sub = None
        if v.subject_type == SubjectTypeEnum.STUDENT and v.student_id: sub = session.get(Student, v.student_id)
        elif v.subject_type == SubjectTypeEnum.STAFF and v.staff_id: sub = session.get(StaffMember, v.staff_id)
        elif v.subject_type == SubjectTypeEnum.VISITOR and v.visitor_id: sub = session.get(Visitor, v.visitor_id)
        return ViolationSubject(id=sub.id, name=sub.name, photoUrl=sub.photo_url) if sub else None

    @staticmethod
    def resolve(session: Session, violation_id: str, notes: str, user: SecurityStaff):
        v = session.get(Violation, violation_id)
        if not v or v.resolved: return None
        v.resolved, v.resolved_at, v.resolved_by_staff_id, v.resolution_notes = True, datetime.utcnow(), user.id, notes
        session.add(v)
        session.commit()
        session.refresh(v)
        return v
