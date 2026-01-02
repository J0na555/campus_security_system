# Quick Start Guide - Campus Security System Backend

## 1. Install Dependencies

```bash
# Activate virtual environment
source pypy/bin/activate

# Install requirements
pip install -r requirements.txt
```

## 2. Run Setup Verification

```bash
python test_setup.py
```

Expected output:
```
✓ Python version OK
✓ All dependencies found
✓ All application modules loaded
✓ Setup verification PASSED!
```

## 3. Start the Server

```bash
# Option 1: Direct
python main.py

# Option 2: With uvicorn
uvicorn main:app --reload

# Option 3: Custom host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 4. Access the API

- **Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 5. Test Authentication

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "employeeId": "EMP-2024-001",
    "password": "password123"
  }'
```

Response:
```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresAt": "2026-01-03T10:30:00Z",
    "user": {
      "id": "usr_abc123",
      "employeeId": "EMP-2024-001",
      "name": "John Smith",
      "email": "john.smith@campus.edu",
      "role": "security_officer"
    }
  }
}
```

### Get Current User
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 6. Test QR Scanning (Public Endpoints)

### Valid Student QR Scan
```bash
curl -X POST http://localhost:8000/api/v1/scan/qr \
  -H "Content-Type: application/json" \
  -d '{
    "qrCode": "QR-STU-2024-ABC123XYZ",
    "gateId": "gate_main_entrance",
    "scanTimestamp": "2026-01-02T14:30:00Z"
  }'
```

### Invalid QR Scan (Creates Violation)
```bash
curl -X POST http://localhost:8000/api/v1/scan/qr \
  -H "Content-Type: application/json" \
  -d '{
    "qrCode": "INVALID-QR-CODE",
    "gateId": "gate_main_entrance",
    "scanTimestamp": "2026-01-02T14:30:00Z"
  }'
```

### Face Verification
```bash
curl -X POST http://localhost:8000/api/v1/scan/face/verify \
  -H "Content-Type: application/json" \
  -d '{
    "subjectId": "stu_789xyz",
    "subjectType": "student",
    "faceImage": "base64_encoded_image...",
    "gateId": "gate_main_entrance",
    "scanTimestamp": "2026-01-02T14:30:05Z"
  }'
```

## 7. Test Violations API (Protected)

### List Violations
```bash
curl -X GET "http://localhost:8000/api/v1/violations?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### With Filters
```bash
curl -X GET "http://localhost:8000/api/v1/violations?type=face_verification_mismatch&resolved=false" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Resolve Violation
```bash
curl -X PATCH http://localhost:8000/api/v1/violations/vio_abc123/resolve \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Investigated - false positive"
  }'
```

## 8. Test Visitor Pass Creation (Protected)

```bash
curl -X POST http://localhost:8000/api/v1/visitors/passes \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "visitorName": "Test Visitor",
    "visitorEmail": "visitor@example.com",
    "visitorPhone": "+1-555-123-4567",
    "purpose": "Campus tour",
    "hostEmployeeId": "stf_456abc",
    "validFrom": "2026-01-03T09:00:00Z",
    "validUntil": "2026-01-03T17:00:00Z",
    "allowedGates": ["gate_main_entrance"],
    "notes": "VIP guest"
  }'
```

## 9. Using Interactive Docs

1. Go to http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Login using `/api/v1/auth/login` endpoint
4. Copy the token from response
5. Paste token in authorization dialog
6. Now you can test all protected endpoints interactively

## 10. Sample Accounts

### Security Staff (Dashboard Users)
| Email | Password | Role |
|-------|----------|------|
| john.smith@campus.edu | password123 | Security Officer |
| sarah.johnson@campus.edu | password123 | Security Supervisor |
| michael.chen@campus.edu | password123 | Admin |

### Sample Students (for QR testing)
| Name | QR Code | Department |
|------|---------|------------|
| Alice Johnson | QR-STU-2024-ABC123XYZ | Computer Science |
| Bob Williams | QR-STU-2024-DEF456ABC | Engineering |

### Sample Staff (for QR testing & hosting visitors)
| Name | QR Code | Department |
|------|---------|------------|
| Dr. Robert Chen | QR-STF-2024-XYZ789ABC | Engineering |
| Jane Doe | QR-STF-2024-JKL012DEF | Human Resources |

### Sample Gates
- gate_main_entrance
- gate_library
- gate_hr_building
- gate_engineering

## 11. Database Management

### View Database
```bash
sqlite3 campus_security.db
```

```sql
-- List all tables
.tables

-- View violations
SELECT * FROM violations;

-- View security staff
SELECT * FROM security_staff;

-- Exit
.quit
```

### Reset Database
```bash
# Stop the server
# Delete database
rm campus_security.db

# Restart server - will recreate with sample data
python main.py
```

## 12. Troubleshooting

### Dependencies Not Found
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
# Use different port
uvicorn main:app --port 8001
```

### Database Locked
```bash
# Close all connections and restart
rm campus_security.db
python main.py
```

### Token Expired
```bash
# Login again to get new token
curl -X POST http://localhost:8000/api/v1/auth/login ...
```

## 13. Development Workflow

1. Make code changes
2. Server auto-reloads (if using `--reload`)
3. Test in `/docs` or with curl
4. Check terminal for logs
5. View database if needed

## 14. Next Steps

- Integrate real face recognition service
- Set up cloud storage for images
- Add WebSocket for real-time alerts
- Connect email service
- Write comprehensive tests
- Deploy to production

## 15. Useful Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# View server logs (verbose)
uvicorn main:app --reload --log-level debug

# Format code
black *.py routers/*.py

# Type checking
mypy *.py

# Run tests (when implemented)
pytest
```

---

**Need Help?**
- Check IMPLEMENTATION.md for detailed documentation
- View API contract: api_contract.md
- Interactive docs: http://localhost:8000/docs
