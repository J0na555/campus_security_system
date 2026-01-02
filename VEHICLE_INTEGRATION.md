# Vehicle Tracking Integration - Summary

## Overview

The Campus Security System has been successfully extended with **vehicle tracking capabilities** that log ALL vehicle entries and exits, while maintaining the privacy-focused approach for pedestrian access (violations only).

## Data Persistence Philosophy

| Entry Type | What Gets Saved | Reason |
|------------|-----------------|--------|
| **Student/Staff** | Only violations (4 types) | Privacy - no tracking of successful entries |
| **Visitor** | Only violations | Same as above |
| **Vehicle** | **ALL entries and exits** | Admin needs full vehicle movement history |

## New Database Models

### 1. Vehicle Table
Stores registered vehicles with owner information:
- `id`, `license_plate` (unique)
- `owner_type` (student/staff/visitor), `owner_id`, `owner_name`
- `vehicle_type` (car/motorcycle/truck/van/bus/other)
- `color`, `make`, `model`
- `registered_at`, timestamps

### 2. VehicleEntry Table
Logs **ALL vehicle entries and exits**:
- `id`, `license_plate`, `vehicle_id` (FK, nullable)
- `entry_time`, `exit_time` (nullable)
- `entry_image_path`, `exit_image_path`
- `status` (entered/exited/flagged)
- `gate_id`, `notes`

### 3. VehicleAlert Table
Tracks unknown or mismatched vehicles:
- `id`, `license_plate`, `timestamp`
- `alert_type` (unknown_vehicle/vehicle_mismatch)
- `captured_image_path`, `details`
- `resolved`, `resolved_at`, `resolved_by_staff_id`, `resolution_notes`
- `gate_id`

## New API Endpoints

### Public Endpoints (Gate Cameras - No Auth)

#### POST `/api/v1/vehicle/entry`
Log vehicle entry via license plate recognition
- **Request**: `{licensePlate, gateId?, entryImagePath?, timestamp}`
- **Response**: Entry record + alert if unknown vehicle
- **Behavior**: 
  - Creates VehicleEntry for ALL vehicles (registered or not)
  - Creates VehicleAlert if plate not registered

#### POST `/api/v1/vehicle/exit`
Log vehicle exit
- **Request**: `{licensePlate, gateId?, exitImagePath?, timestamp}`
- **Response**: Updated entry record with exit time
- **Behavior**:
  - Finds matching entry, updates with exit time
  - Creates alert if no matching entry found

### Protected Endpoints (Dashboard - Auth Required)

#### POST `/api/v1/vehicles`
Register a new vehicle
- **Auth**: Required
- **Request**: `{licensePlate, ownerType, ownerId?, ownerName, vehicleType, color?, make?, model?}`
- **Response**: Registered vehicle info

#### GET `/api/v1/vehicles`
List all registered vehicles
- **Auth**: Required
- **Response**: Array of vehicle records

#### GET `/api/v1/vehicle/entries`
List all vehicle entries/exits with pagination
- **Auth**: Required
- **Query Params**: `page`, `limit`, `licensePlate?`, `status?`
- **Response**: **Full vehicle movement history** with pagination
- **Note**: Returns ALL entries, not just violations

#### GET `/api/v1/vehicle/alerts`
List vehicle security alerts
- **Auth**: Required
- **Query Params**: `page`, `limit`, `alertType?`, `resolved?`
- **Response**: Vehicle alerts with pagination

#### PATCH `/api/v1/vehicle/alerts/{id}/resolve`
Resolve a vehicle alert
- **Auth**: Required
- **Request**: `{notes?}`
- **Response**: Updated alert status

## WebSocket Integration

### Endpoint: `GET /ws/alerts`
Real-time alert broadcasting (public, no auth)

**Broadcasts:**
- `violation_alert` - Pedestrian security violations
- `vehicle_alert` - Unknown/mismatched vehicles
- `heartbeat` - Keep-alive messages

**Message Format:**
```json
{
  "type": "vehicle_alert",
  "timestamp": "2026-01-02T14:30:00Z",
  "data": {
    "alertId": 1,
    "licensePlate": "XYZ-999",
    "alertType": "unknown_vehicle",
    "gateId": "gate_parking_entrance",
    "message": "Unknown vehicle detected"
  }
}
```

## Sample Data

The database now includes 3 sample registered vehicles:
- **ABC-123** - Blue Toyota Camry (Student: Alice Johnson)
- **XYZ-789** - Black Honda Accord (Staff: Dr. Robert Chen)
- **MOT-456** - Red Yamaha R15 (Student: Bob Williams)

## Updated Architecture

```
┌─────────────────────────────────────────────────┐
│              Gate Entry Points                   │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐ │
│  │ QR Scanner│  │Face Camera│  │License Plate  │ │
│  │           │  │           │  │Recognition    │ │
│  └──────────┘  └──────────┘  └───────────────┘ │
└─────────────────────────────────────────────────┘
            │            │              │
            v            v              v
┌─────────────────────────────────────────────────┐
│              Backend API                         │
│  /scan/qr     /face/verify     /vehicle/entry   │
│                                 /vehicle/exit    │
└─────────────────────────────────────────────────┘
            │            │              │
            v            v              v
┌─────────────────────────────────────────────────┐
│              SQLite Database                     │
│  ┌──────────┐  ┌────────────┐  ┌─────────────┐ │
│  │Violations│  │VehicleEntry│  │VehicleAlert │ │
│  │(errors   │  │(ALL logs)  │  │(unknown)    │ │
│  │only)     │  │            │  │             │ │
│  └──────────┘  └────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────┘
            │            │              │
            └────────────┴──────────────┘
                         │
                         v
                ┌───────────────┐
                │ /ws/alerts    │
                │ (WebSocket)   │
                └───────────────┘
```

## Key Differences: People vs Vehicles

| Feature | People (Student/Staff/Visitor) | Vehicles |
|---------|-------------------------------|----------|
| **Success Logging** | ❌ Not logged | ✅ Always logged |
| **Error Logging** | ✅ Violations table | ✅ VehicleAlert table |
| **History** | No success history | Full entry/exit history |
| **Privacy** | Privacy-focused | Full tracking |
| **Alert Types** | 4 violation types | 2 alert types |

## Alert Types

### Vehicle Alerts
1. **unknown_vehicle** - License plate not registered in system
2. **vehicle_mismatch** - Exit without entry or other discrepancies

### Pedestrian Violations (Unchanged)
1. **unauthorized_qr_scan** - Invalid/tampered QR code
2. **face_verification_mismatch** - Face doesn't match photo
3. **multiple_fail_attempt** - 3+ failures in 5 minutes
4. **expired_visitor_qr_code** - Visitor pass expired

## Testing the Vehicle System

### 1. Register a Vehicle
```bash
curl -X POST http://localhost:8000/api/v1/vehicles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "licensePlate": "TEST-123",
    "ownerType": "student",
    "ownerName": "Test Student",
    "vehicleType": "car",
    "color": "White",
    "make": "Tesla",
    "model": "Model 3"
  }'
```

### 2. Log Vehicle Entry
```bash
curl -X POST http://localhost:8000/api/v1/vehicle/entry \
  -H "Content-Type: application/json" \
  -d '{
    "licensePlate": "TEST-123",
    "gateId": "gate_parking",
    "timestamp": "2026-01-02T14:30:00Z"
  }'
```

### 3. Log Unknown Vehicle (Creates Alert)
```bash
curl -X POST http://localhost:8000/api/v1/vehicle/entry \
  -H "Content-Type: application/json" \
  -d '{
    "licensePlate": "UNKNOWN-999",
    "gateId": "gate_parking",
    "timestamp": "2026-01-02T14:31:00Z"
  }'
```

### 4. View Vehicle Entries
```bash
curl -X GET "http://localhost:8000/api/v1/vehicle/entries?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. View Vehicle Alerts
```bash
curl -X GET "http://localhost:8000/api/v1/vehicle/alerts?resolved=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Connect to WebSocket Alerts
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts');

ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log('Alert received:', alert);
  
  if (alert.type === 'vehicle_alert') {
    console.log('Vehicle alert:', alert.data);
  }
};
```

## Files Modified/Created

### New Files:
- `routers/vehicles_public.py` - Public vehicle entry/exit endpoints
- `routers/vehicles_dashboard.py` - Protected vehicle management endpoints
- `websocket_alerts.py` - WebSocket broadcaster for real-time alerts

### Modified Files:
- `models.py` - Added Vehicle, VehicleEntry, VehicleAlert models + enums
- `schemas.py` - Added vehicle request/response schemas
- `database.py` - Added vehicle seed data
- `main.py` - Added vehicle routers + WebSocket endpoint
- `routers/__init__.py` - Exported new vehicle routers
- `requirements.txt` - Added websockets dependency

## Production Considerations

1. **WebSocket Scaling**: Current in-memory broadcaster works for single-server deployment. For multi-server, use Redis pub/sub.
2. **Image Storage**: Store captured images in cloud storage (S3, GCS) instead of local paths.
3. **License Plate Recognition**: Integrate actual LPR service/hardware.
4. **Performance**: Add indexes on frequently queried fields (already included).
5. **Analytics**: VehicleEntry table enables rich analytics (peak hours, average duration, etc.).
6. **Alerts**: Connect vehicle alerts to notification system (email, SMS, push).

## Summary

✅ **Complete vehicle tracking system** integrated
✅ **All vehicle movements logged** (different from pedestrian approach)
✅ **Real-time alerts** via WebSocket
✅ **Unknown vehicle detection** automatic
✅ **Full vehicle history** available for auditing
✅ **Backward compatible** with existing pedestrian system
✅ **Sample data** included for testing

The system now provides **comprehensive campus security** covering both pedestrian access control (privacy-focused, violations-only) and vehicle tracking (full history logging).
