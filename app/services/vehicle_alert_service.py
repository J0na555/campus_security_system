import math
from datetime import datetime
from sqlmodel import Session, select, func
from app.models.vehicle_alert import VehicleAlert
from app.models.security_staff import SecurityStaff
from app.schemas.common import PaginationInfo

class VehicleAlertService:
    @staticmethod
    def list_alerts(session: Session, page: int, limit: int, alert_type: str = None, resolved: bool = None):
        query = select(VehicleAlert).order_by(VehicleAlert.timestamp.desc())
        if alert_type: query = query.where(VehicleAlert.alert_type == alert_type)
        if resolved is not None: query = query.where(VehicleAlert.resolved == resolved)
        
        total = session.exec(select(func.count()).select_from(query.subquery())).one()
        alerts = session.exec(query.offset((page - 1) * limit).limit(limit)).all()
        
        pagination = PaginationInfo(
            currentPage=page, totalPages=math.ceil(total / limit), totalItems=total,
            itemsPerPage=limit, hasNextPage=page * limit < total, hasPreviousPage=page > 1
        )
        return alerts, pagination

    @staticmethod
    def resolve(session: Session, alert_id: int, notes: str, user: SecurityStaff):
        alert = session.get(VehicleAlert, alert_id)
        if not alert or alert.resolved: return None
        alert.resolved, alert.resolved_at, alert.resolved_by_staff_id, alert.resolution_notes = True, datetime.utcnow(), user.id, notes
        session.add(alert)
        session.commit()
        session.refresh(alert)
        return alert
