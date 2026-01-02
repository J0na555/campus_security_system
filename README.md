# Campus Security System - Backend

FastAPI + SQLite backend for campus gate security management with QR scanning, face verification, and **vehicle tracking**.

## Features

- **Authentication**: JWT-based authentication for security staff
- **Gate Scanning**: QR code validation and face verification (public endpoints)
- **Violation Tracking**: Comprehensive violation management with different types
- **Visitor Management**: Create and manage visitor passes with QR codes
- **Vehicle Tracking**: **NEW** - Complete vehicle entry/exit logging with license plate recognition
- **Real-time Alerts**: WebSocket-based real-time violation and vehicle alerts
- **Dashboard API**: Full CRUD operations for security personnel

## Data Persistence Philosophy

| Entry Type | What Gets Saved | Reason |
|------------|-----------------|--------|
| **Student/Staff** | Only violations (4 types) | Privacy - no tracking of successful entries |
| **Visitor** | Only violations | Same as above |
| **Vehicle** | **ALL entries and exits** | Admin needs full vehicle movement history |

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: SQL database ORM with Pydantic integration
- **SQLite**: Lightweight database for development
- **JWT**: Secure token-based authentication
- **Bcrypt**: Password hashing

## Project Structure

```
campus_security_system/
├── main.py                 # FastAPI application entry point
├── models.py               # SQLModel database models
├── schemas.py              # Pydantic request/response schemas
├── database.py             # Database configuration and initialization
├── auth.py                 # Authentication utilities
├── routers/                # API route handlers
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   ├── scan.py            # QR scan and face verification
│   ├── violations.py      # Violation management
│   └── visitors.py        # Visitor pass management
├── requirements.txt        # Python dependencies
├── api_contract.md        # API contract documentation
└── README.md              # This file
```

## Database Models

### Lookup Tables
- **Gate**: Entry point/gate locations
- **Department**: Academic and administrative departments

### Subject Tables
- **Student**: Student records with QR codes
- **StaffMember**: Faculty/staff records with QR codes
- **Visitor**: Visitor passes with time-limited access

### Vehicle Tables (NEW)
- **Vehicle**: Registered vehicles with owner information
- **VehicleEntry**: ALL vehicle entries/exits (full tracking)
- **VehicleAlert**: Unknown/mismatched vehicle alerts

### Security Tables
- **SecurityStaff**: Dashboard users (security personnel)
- **Violation**: Security violation records (people only)
- **FailAttempt**: Failed face verification attempts
- **AccessLog**: Successful access logs (optional)

## API Endpoints

### Authentication (Protected)
- `POST /api/v1/auth/login` - Login with employee credentials
- `GET /api/v1/auth/me` - Get current user information

### Gate Scanning (Public)
- `POST /api/v1/scan/qr` - Validate QR code at gate
- `POST /api/v1/scan/face/verify` - Verify face against enrolled photo

### Vehicle Tracking (NEW)
**Public (Gate Cameras):**
- `POST /api/v1/vehicle/entry` - Log vehicle entry via license plate
- `POST /api/v1/vehicle/exit` - Log vehicle exit

**Protected (Dashboard):**
- `POST /api/v1/vehicles` - Register a new vehicle
- `GET /api/v1/vehicles` - List registered vehicles
- `GET /api/v1/vehicle/entries` - List all vehicle entries/exits (full history)
- `GET /api/v1/vehicle/alerts` - List vehicle alerts
- `PATCH /api/v1/vehicle/alerts/{id}/resolve` - Resolve vehicle alert

### Violations (Protected)
- `GET /api/v1/violations` - List violations with filters
- `PATCH /api/v1/violations/{id}/resolve` - Resolve a violation

### Visitor Management (Protected)
- `POST /api/v1/visitors/passes` - Create new visitor pass
- `GET /api/v1/visitors/passes` - List visitor passes

### WebSocket (Public)
- `GET /ws/alerts` - Real-time violation and vehicle alerts

## Installation

1. **Create virtual environment**:
```bash
python -m venv pypy
source pypy/bin/activate  # On Windows: pypy\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set environment variables** (optional):
```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///./campus_security.db"
export ACCESS_TOKEN_EXPIRE_MINUTES="480"
```

## Running the Application

1. **Start the server**:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Access the API**:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json

## Sample Data

The application automatically initializes with sample data on first run:

### Security Staff Accounts
- **Email**: `john.smith@campus.edu`
- **Password**: `password123`
- **Role**: Security Officer

Other accounts:
- `sarah.johnson@campus.edu` (Security Supervisor)
- `michael.chen@campus.edu` (Admin)

### Sample Gates
- Main Entrance Gate
- Library Gate
- HR Building Gate
- Engineering Block Gate

### Sample Students & Staff
Pre-populated students and staff members with QR codes for testing

### Sample Vehicles (NEW)
- **ABC-123** - Blue Toyota Camry (Student)
- **XYZ-789** - Black Honda Accord (Staff)  
- **MOT-456** - Red Yamaha R15 (Student)

## API Authentication

Protected endpoints require a JWT token in the Authorization header:

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"employeeId": "EMP-2024-001", "password": "password123"}'

# Use token
curl -X GET http://localhost:8000/api/v1/violations \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Violation Types

**Pedestrian Violations (Privacy-focused - only errors logged):**
1. **unauthorized_qr_scan**: Invalid/tampered QR code
2. **face_verification_mismatch**: Face doesn't match enrolled photo
3. **multiple_fail_attempt**: 3+ verification failures in 5 minutes
4. **expired_visitor_qr_code**: Visitor pass has expired

**Vehicle Alerts (All movements logged + alerts for unknowns):**
1. **unknown_vehicle**: License plate not registered in system
2. **vehicle_mismatch**: Exit without entry or other discrepancies

> **Note**: Vehicle entries are ALL logged (success and failures), unlike pedestrian entries which only log violations.

## Development

### Running Tests
```bash
pytest
```

### Database Reset
Delete the SQLite database file to reset:
```bash
rm campus_security.db
```

The database will be recreated with sample data on next startup.

### Code Structure

- **models.py**: Define database schema with SQLModel
- **schemas.py**: Request/response validation with Pydantic
- **routers/**: Endpoint logic separated by domain
- **auth.py**: JWT token creation/validation
- **database.py**: DB connection and initialization

## Production Considerations

1. **Change SECRET_KEY**: Use a strong, random secret key
2. **Use PostgreSQL**: Replace SQLite with PostgreSQL for production
3. **Configure CORS**: Restrict allowed origins in main.py
4. **Enable HTTPS**: Use SSL/TLS certificates
5. **Rate Limiting**: Add rate limiting middleware
6. **Logging**: Implement proper logging and monitoring
7. **Face Recognition**: Integrate real face recognition service
8. **License Plate Recognition**: Integrate actual LPR hardware/service
9. **Image Storage**: Store captured images in cloud storage (S3, etc.)
10. **Email Service**: Connect email service for visitor notifications
11. **WebSocket Scaling**: Use Redis pub/sub for multi-server WebSocket broadcasting

## API Contract

See [api_contract.md](api_contract.md) for complete API documentation including:
- Request/response schemas
- Error codes
- Flow diagrams
- WebSocket specifications

For vehicle tracking details, see [VEHICLE_INTEGRATION.md](VEHICLE_INTEGRATION.md).

## License

Proprietary - Campus Security System

## Version

**v1.1.0** - January 2, 2026
