from sqlmodel import Session
from app.core.database import engine, create_db_and_tables
from app.utils.sample_data import (
    create_gates, create_departments, create_security_staff
)
from app.utils.sample_data_subjects import (
    create_students, create_staff_members, create_vehicles
)
from app.utils.mock_data import populate_mock_data

def init_db():
    with Session(engine) as session:
        # Check if data already exists
        from app.models.gate import Gate
        try:
            if session.query(Gate).first():
                return
        except Exception:
            pass
        
        print("Initializing database with sample data...")
        create_db_and_tables()
        
        gates = create_gates(session)
        departments = create_departments(session)
        session.commit()
        
        staff = create_security_staff(session)
        students = create_students(session, departments)
        staff_members = create_staff_members(session, departments)
        vehicles = create_vehicles(session, students, staff_members)
        
        session.commit()
        
        # Populate comprehensive mock data for frontend testing
        populate_mock_data(session, students, staff_members, vehicles, gates, staff)
        
        print("Database initialized successfully!")
