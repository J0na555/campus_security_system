from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.vehicle import Vehicle
from app.schemas.vehicle import RegisterVehicleRequest, VehicleInfo

class VehicleService:
    @staticmethod
    def register(session: Session, data: RegisterVehicleRequest):
        plate = data.licensePlate.upper().strip()
        if session.exec(select(Vehicle).where(Vehicle.license_plate == plate)).first():
            raise HTTPException(status_code=400, detail="Vehicle already registered")
        
        vehicle = Vehicle(
            license_plate=plate, owner_type=data.ownerType, owner_id=data.ownerId,
            owner_name=data.ownerName, vehicle_type=data.vehicleType,
            color=data.color, make=data.make, model=data.model
        )
        session.add(vehicle)
        session.commit()
        session.refresh(vehicle)
        return vehicle

    @staticmethod
    def list_vehicles(session: Session):
        return session.exec(select(Vehicle).order_by(Vehicle.registered_at.desc())).all()

    @staticmethod
    def get_vehicle_info(vehicle: Vehicle):
        return VehicleInfo(
            id=vehicle.id, licensePlate=vehicle.license_plate, 
            ownerType=vehicle.owner_type.value, ownerId=vehicle.owner_id,
            ownerName=vehicle.owner_name, vehicleType=vehicle.vehicle_type.value,
            color=vehicle.color, make=vehicle.make, model=vehicle.model,
            registeredAt=vehicle.registered_at
        )
