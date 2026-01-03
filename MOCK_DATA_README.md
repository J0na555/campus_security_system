# Mock Data for Frontend Testing

This document provides information about the mock data available in the database for frontend testing.

## Populating Mock Data

To populate the database with comprehensive mock data, run:

```bash
source pypy/bin/activate  # Activate virtual environment
python populate_mock_data.py
```

This script will:
- Create base data (gates, departments, security staff, students, staff, vehicles)
- Add comprehensive mock data (visitors, violations, vehicle entries, alerts)
- Add additional admin users if they don't already exist

## Admin Login Credentials

Use these credentials to login as an admin user:

| Employee ID | Password | Role | Name |
|-------------|----------|------|------|
| `ADMIN-001` | `admin123` | Admin | Admin User |
| `ADMIN-002` | `admin123` | Admin | Super Admin |
| `EMP-2024-003` | `password123` | Admin | Michael Chen |
| `SUPER-001` | `super123` | Supervisor | Supervisor One |

## Other User Credentials

| Employee ID | Password | Role | Name |
|-------------|----------|------|------|
| `EMP-2024-001` | `password123` | Security Officer | John Smith |
| `EMP-2024-002` | `password123` | Supervisor | Sarah Johnson |

## Test QR Codes

### Students
- `QR-STU-2024-ABC123XYZ` - Alice Johnson
- `QR-STU-2024-DEF456ABC` - Bob Williams
- `QR-STU-2024-GHI789XYZ` - Charlie Davis
- `QR-STU-2024-JKL012ABC` - Diana Martinez
- `QR-STU-2024-MNO345DEF` - Ethan Wilson

### Staff
- `QR-STF-2024-XYZ789ABC` - Dr. Robert Chen
- `QR-STF-2024-JKL012DEF` - Jane Doe (HR Manager)
- `QR-STF-2024-PQR678GHI` - Dr. Sarah Thompson
- `QR-STF-2024-STU901JKL` - Mark Johnson

### Visitors
- `QR-VIS-2026-MOCK001` - Bob Williams (Valid, expires in ~6 hours)
- `QR-VIS-2026-MOCK002` - Alice Cooper (Valid, expires in ~2 hours)
- `QR-VIS-2026-MOCK003` - Charlie Brown (Expired - will trigger violation)
- `QR-VIS-2026-MOCK004` - Diana Prince (Valid, starts in ~1 hour)

## Mock Data Summary

The database includes:

### Violations (6 total)
- **Face Verification Mismatch** (2) - One resolved, one unresolved
- **Unauthorized QR Scan** (2) - One resolved, one unresolved
- **Expired Visitor QR Code** (1) - Unresolved
- **Multiple Fail Attempt** (1) - Unresolved

### Visitors (4 total)
- 3 active visitor passes
- 1 expired visitor pass (for testing violations)

### Vehicle Entries (4 total)
- 2 exited vehicles
- 1 currently entered vehicle
- 1 flagged unknown vehicle

### Vehicle Alerts (3 total)
- 2 unknown vehicle alerts (1 resolved, 1 unresolved)
- 1 vehicle mismatch alert (unresolved)

## Testing Dashboard Features

With the mock data, you can test:

1. **Violations Dashboard**
   - View all violations
   - Filter by type, status, gate, date range
   - Resolve violations
   - See resolved vs unresolved counts

2. **Visitors Management**
   - View all visitor passes
   - Create new visitor passes
   - See active vs expired passes

3. **Vehicle Management**
   - View registered vehicles
   - View vehicle entries/exits
   - View vehicle alerts
   - Resolve alerts

4. **Authentication**
   - Login with different user roles
   - Test role-based access control

## Notes

- All timestamps are relative to when the data was populated
- Violations include various types for comprehensive testing
- Some violations are already resolved to test filtering
- Vehicle entries include both registered and unknown vehicles
- The database is SQLite by default (`campus_security.db`)

## Resetting Mock Data

To reset and repopulate the database:

```bash
# Delete the database file
rm campus_security.db

# Run the populate script
python populate_mock_data.py
```

Or simply run the populate script again - it will add any missing data without duplicating existing records.
