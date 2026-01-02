"""
Vehicle management API endpoints
Protected endpoints for dashboard - authentication required
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, func
from database import get_session
from auth import get_current_user
from schemas import (
    RegisterVehicleRequest, VehicleInfo, VehicleListResponse,
    VehicleEntryInfo, VehicleEntryListResponse,
    VehicleAlertInfo, VehicleAlertListResponse,
    SuccessResponse, PaginationInfo, ViolationResolvedBy
)
from models import SecurityStaff, Vehicle, VehicleEntry, VehicleAlert
from datetime import datetime
import math

router = APIRouter(prefix="/vehicles", tags=["Vehicle Management"])


@router.post("", response_model=SuccessResponse, status_code=201)
async def register_vehicle(
    vehicle_data: RegisterVehicleRequest,
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    Register a new vehicle
    
    Requires authentication
    """
    license_plate = vehicle_data.licensePlate.upper().strip()
    
    # Check if vehicle already exists
    statement = select(Vehicle).where(Vehicle.license_plate == license_plate)
    existing = session.exec(statement).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "code": "VEHICLE_EXISTS",
                "message": f"Vehicle with license plate {license_plate} already registered"
            }
        )
    
    # Create vehicle
    vehicle = Vehicle(
        license_plate=license_plate,
        owner_type=vehicle_data.ownerType,
        owner_id=vehicle_data.ownerId,
        owner_name=vehicle_data.ownerName,
        vehicle_type=vehicle_data.vehicleType,
        color=vehicle_data.color,
        make=vehicle_data.make,
        model=vehicle_data.model
    )
    
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    
    vehicle_info = VehicleInfo(
        id=vehicle.id,
        licensePlate=vehicle.license_plate,
        ownerType=vehicle.owner_type.value,
        ownerId=vehicle.owner_id,
        ownerName=vehicle.owner_name,
        vehicleType=vehicle.vehicle_type.value,
        color=vehicle.color,
        make=vehicle.make,
        model=vehicle.model,
        registeredAt=vehicle.registered_at
    )
    
    return {
        "status": "success",
        "data": vehicle_info.model_dump()
    }


@router.get("", response_model=SuccessResponse)
async def list_vehicles(
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    List all registered vehicles
    
    Requires authentication
    """
    statement = select(Vehicle).order_by(Vehicle.registered_at.desc())
    vehicles = session.exec(statement).all()
    
    vehicle_list = []
    for vehicle in vehicles:
        vehicle_list.append(VehicleInfo(
            id=vehicle.id,
            licensePlate=vehicle.license_plate,
            ownerType=vehicle.owner_type.value,
            ownerId=vehicle.owner_id,
            ownerName=vehicle.owner_name,
            vehicleType=vehicle.vehicle_type.value,
            color=vehicle.color,
            make=vehicle.make,
            model=vehicle.model,
            registeredAt=vehicle.registered_at
        ))
    
    response_data = VehicleListResponse(
        vehicles=vehicle_list,
        total=len(vehicle_list)
    )
    
    return {
        "status": "success",
        "data": response_data.model_dump()
    }


@router.get("/entries", response_model=SuccessResponse)
async def list_vehicle_entries(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    licensePlate: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    List all vehicle entries/exits with pagination
    
    Requires authentication
    Returns FULL vehicle movement history
    """
    query = select(VehicleEntry)
    
    # Apply filters
    if licensePlate:
        query = query.where(VehicleEntry.license_plate == licensePlate.upper().strip())
    
    if status:
        query = query.where(VehicleEntry.status == status)
    
    # Order by most recent first
    query = query.order_by(VehicleEntry.entry_time.desc())
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total_items = session.exec(count_query).one()
    
    # Calculate pagination
    total_pages = math.ceil(total_items / limit)
    offset = (page - 1) * limit
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    entries = session.exec(query).all()
    
    # Build response
    entry_list = []
    for entry in entries:
        vehicle_info = None
        if entry.vehicle_id:
            vehicle = session.get(Vehicle, entry.vehicle_id)
            if vehicle:
                vehicle_info = VehicleInfo(
                    id=vehicle.id,
                    licensePlate=vehicle.license_plate,
                    ownerType=vehicle.owner_type.value,
                    ownerId=vehicle.owner_id,
                    ownerName=vehicle.owner_name,
                    vehicleType=vehicle.vehicle_type.value,
                    color=vehicle.color,
                    make=vehicle.make,
                    model=vehicle.model,
                    registeredAt=vehicle.registered_at
                )
        
        entry_list.append(VehicleEntryInfo(
            id=entry.id,
            licensePlate=entry.license_plate,
            vehicleId=entry.vehicle_id,
            entryTime=entry.entry_time,
            exitTime=entry.exit_time,
            status=entry.status.value,
            gateId=entry.gate_id,
            vehicle=vehicle_info
        ))
    
    pagination = PaginationInfo(
        currentPage=page,
        totalPages=total_pages,
        totalItems=total_items,
        itemsPerPage=limit,
        hasNextPage=page < total_pages,
        hasPreviousPage=page > 1
    )
    
    response_data = VehicleEntryListResponse(
        entries=entry_list,
        pagination=pagination
    )
    
    return {
        "status": "success",
        "data": response_data.model_dump()
    }


@router.get("/alerts", response_model=SuccessResponse)
async def list_vehicle_alerts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    alertType: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    List vehicle security alerts
    
    Requires authentication
    """
    query = select(VehicleAlert)
    
    # Apply filters
    if alertType:
        query = query.where(VehicleAlert.alert_type == alertType)
    
    if resolved is not None:
        query = query.where(VehicleAlert.resolved == resolved)
    
    # Order by most recent first
    query = query.order_by(VehicleAlert.timestamp.desc())
    
    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total_items = session.exec(count_query).one()
    
    # Calculate pagination
    total_pages = math.ceil(total_items / limit)
    offset = (page - 1) * limit
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute query
    alerts = session.exec(query).all()
    
    # Build response
    alert_list = []
    for alert in alerts:
        resolved_by_data = None
        if alert.resolved_by_staff_id:
            resolved_by_staff = session.get(SecurityStaff, alert.resolved_by_staff_id)
            if resolved_by_staff:
                resolved_by_data = ViolationResolvedBy(
                    id=resolved_by_staff.id,
                    name=resolved_by_staff.name
                )
        
        alert_list.append(VehicleAlertInfo(
            id=alert.id,
            licensePlate=alert.license_plate,
            timestamp=alert.timestamp,
            alertType=alert.alert_type.value,
            gateId=alert.gate_id,
            resolved=alert.resolved,
            resolvedAt=alert.resolved_at,
            resolvedBy=resolved_by_data,
            notes=alert.resolution_notes
        ))
    
    pagination = PaginationInfo(
        currentPage=page,
        totalPages=total_pages,
        totalItems=total_items,
        itemsPerPage=limit,
        hasNextPage=page < total_pages,
        hasPreviousPage=page > 1
    )
    
    response_data = VehicleAlertListResponse(
        alerts=alert_list,
        pagination=pagination
    )
    
    return {
        "status": "success",
        "data": response_data.model_dump()
    }


@router.patch("/alerts/{alert_id}/resolve", response_model=SuccessResponse)
async def resolve_vehicle_alert(
    alert_id: int,
    notes: Optional[str] = None,
    session: Session = Depends(get_session),
    current_user: SecurityStaff = Depends(get_current_user)
):
    """
    Mark a vehicle alert as resolved
    
    Requires authentication
    """
    alert = session.get(VehicleAlert, alert_id)
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "status": "error",
                "code": "NOT_FOUND",
                "message": "Vehicle alert not found"
            }
        )
    
    if alert.resolved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "code": "ALREADY_RESOLVED",
                "message": "Alert is already resolved"
            }
        )
    
    # Mark as resolved
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by_staff_id = current_user.id
    alert.resolution_notes = notes
    
    session.add(alert)
    session.commit()
    session.refresh(alert)
    
    return {
        "status": "success",
        "data": {
            "alertId": alert_id,
            "resolved": True,
            "resolvedAt": alert.resolved_at.isoformat() + "Z",
            "resolvedBy": {
                "id": current_user.id,
                "name": current_user.name
            },
            "notes": notes
        }
    }
