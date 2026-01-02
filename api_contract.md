# Campus Security System - API Contract Document

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication Endpoints](#2-authentication-endpoints)
3. [Gate Scanning Endpoints](#3-gate-scanning-endpoints)
4. [Dashboard Endpoints](#4-dashboard-endpoints)
5. [WebSocket](#5-websocket)
6. [Data Types & Enums](#6-data-types--enums)
7. [Flow Diagrams](#7-flow-diagrams)

---

## 1. Overview

### Base URL

```
Production:  https://api.campus-security.example.com/api/v1
Development: http://localhost:8000/api/v1
```

### Authentication Method

The API uses **JWT Bearer Token** authentication for protected endpoints.

Include the token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

### Common Response Format

#### Success Response

```json
{
  "status": "success",
  "data": { ... }
}
```

#### Error Response

```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Human readable message"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication token |
| `FORBIDDEN` | 403 | Insufficient permissions for this action |
| `NOT_FOUND` | 404 | Requested resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request payload |
| `INTERNAL_ERROR` | 500 | Server-side error |

---

## 2. Authentication Endpoints

### POST `/api/v1/auth/login`

Login with employee credentials.

**Authentication Required:** No

#### Request

```json
{
  "employeeId": "EMP-2024-001",
  "password": "securePassword123"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `employeeId` | string | Yes | Unique employee identifier |
| `password` | string | Yes | Employee password |

#### Success Response (200 OK)

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

#### Error Responses

**401 Unauthorized - Invalid Credentials**

```json
{
  "status": "error",
  "code": "INVALID_CREDENTIALS",
  "message": "Invalid employee ID or password"
}
```

**423 Locked - Account Locked**

```json
{
  "status": "error",
  "code": "ACCOUNT_LOCKED",
  "message": "Account locked due to multiple failed attempts. Try again in 15 minutes."
}
```

---

### GET `/api/v1/auth/me`

Get current authenticated user information.

**Authentication Required:** Yes

#### Request Headers

```
Authorization: Bearer <jwt_token>
```

#### Success Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "id": "usr_abc123",
    "employeeId": "EMP-2024-001",
    "name": "John Smith",
    "email": "john.smith@campus.edu",
    "role": "security_officer",
    "department": "Campus Security",
    "createdAt": "2024-03-15T08:00:00Z",
    "lastLoginAt": "2026-01-02T09:15:00Z"
  }
}
```

#### Error Responses

**401 Unauthorized - Invalid/Expired Token**

```json
{
  "status": "error",
  "code": "UNAUTHORIZED",
  "message": "Invalid or expired authentication token"
}
```

---

## 3. Gate Scanning Endpoints (Public - No Auth)

These endpoints are called by gate scanner devices and do not require authentication.

### POST `/api/v1/scan/qr`

Validate a QR code at a gate.

**Authentication Required:** No

#### Request

```json
{
  "qrCode": "QR-STU-2024-ABC123XYZ",
  "gateId": "gate_main_entrance",
  "scanTimestamp": "2026-01-02T14:30:00Z"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `qrCode` | string | Yes | Scanned QR code content |
| `gateId` | string | Yes | Identifier of the scanning gate |
| `scanTimestamp` | string (ISO 8601) | Yes | Timestamp when scan occurred |

#### Success Response (200 OK) - Valid QR Code

```json
{
  "status": "success",
  "data": {
    "valid": true,
    "subjectType": "student",
    "subject": {
      "id": "stu_789xyz",
      "name": "Alice Johnson",
      "photoUrl": "https://cdn.campus-security.example.com/photos/stu_789xyz.jpg",
      "department": "Computer Science",
      "enrollmentStatus": "active"
    },
    "accessGranted": true,
    "message": "Access granted",
    "requiresFaceVerification": true
  }
}
```

#### Success Response (200 OK) - Visitor Pass

```json
{
  "status": "success",
  "data": {
    "valid": true,
    "subjectType": "visitor",
    "subject": {
      "id": "vis_pass_456",
      "name": "Bob Williams",
      "photoUrl": null,
      "purpose": "Interview at HR Department",
      "hostName": "Jane Doe",
      "hostDepartment": "Human Resources",
      "validFrom": "2026-01-02T09:00:00Z",
      "validUntil": "2026-01-02T17:00:00Z"
    },
    "accessGranted": true,
    "message": "Visitor pass valid",
    "requiresFaceVerification": false
  }
}
```

#### Error Response (200 OK) - Invalid QR Code

> **Note:** For `unauthorized_qr_scan` violations, no subject information is saved to the database since the QR code is invalid/tampered and cannot be linked to any known subject. Only the raw scanned QR data and gate camera capture are stored for investigation purposes.

```json
{
  "status": "success",
  "data": {
    "valid": false,
    "accessGranted": false,
    "violationType": "unauthorized_qr_scan",
    "message": "Invalid or tampered QR code",
    "violationId": "vio_abc123",
    "subjectPersisted": false
  }
}
```

#### Error Response (200 OK) - Expired Visitor Pass

> **Note:** For `expired_visitor_qr_code` violations, the visitor's information is saved to the database since we can identify the subject from the valid (but expired) QR code.

```json
{
  "status": "success",
  "data": {
    "valid": false,
    "accessGranted": false,
    "violationType": "expired_visitor_qr_code",
    "message": "Visitor pass has expired",
    "violationId": "vio_def456",
    "subjectPersisted": true,
    "subject": {
      "id": "vis_pass_789",
      "name": "Charlie Brown",
      "validUntil": "2026-01-01T17:00:00Z"
    }
  }
}
```

---

### POST `/api/v1/face/verify`

Verify a captured face against the enrolled photo.

**Authentication Required:** No

#### Request

```json
{
  "subjectId": "stu_789xyz",
  "subjectType": "student",
  "faceImage": "base64_encoded_image_data...",
  "gateId": "gate_main_entrance",
  "scanTimestamp": "2026-01-02T14:30:05Z"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `subjectId` | string | Yes | ID of the subject from QR scan |
| `subjectType` | string | Yes | Type of subject (`student`, `staff`, `visitor`) |
| `faceImage` | string (base64) | Yes | Base64 encoded face image captured at gate |
| `gateId` | string | Yes | Identifier of the scanning gate |
| `scanTimestamp` | string (ISO 8601) | Yes | Timestamp when image was captured |

#### Success Response (200 OK) - Face Match

```json
{
  "status": "success",
  "data": {
    "verified": true,
    "confidence": 0.94,
    "accessGranted": true,
    "message": "Face verification successful"
  }
}
```

#### Error Response (200 OK) - Face Mismatch

> **Note:** For `face_verification_mismatch` violations, the subject information AND the captured face image are saved to the database. This allows security personnel to review the mismatch and investigate potential unauthorized access attempts.

```json
{
  "status": "success",
  "data": {
    "verified": false,
    "confidence": 0.32,
    "accessGranted": false,
    "violationType": "face_verification_mismatch",
    "message": "Face does not match enrolled photo",
    "violationId": "vio_ghi789",
    "subjectPersisted": true,
    "capturedImagePersisted": true,
    "subject": {
      "id": "stu_789xyz",
      "name": "Alice Johnson",
      "type": "student"
    }
  }
}
```

#### Error Response (200 OK) - Multiple Failed Attempts

> **Note:** For `multiple_fail_attempt` violations, the subject information and all captured face images from the failed attempts are saved to the database. This creates an audit trail for security review and helps identify potential tailgating or impersonation attempts.

```json
{
  "status": "success",
  "data": {
    "verified": false,
    "accessGranted": false,
    "violationType": "multiple_fail_attempt",
    "message": "Access blocked: 3+ verification failures in 5 minutes",
    "violationId": "vio_jkl012",
    "subjectPersisted": true,
    "capturedImagePersisted": true,
    "lockoutUntil": "2026-01-02T14:40:00Z",
    "failedAttemptCount": 3,
    "subject": {
      "id": "stu_789xyz",
      "name": "Alice Johnson",
      "type": "student"
    }
  }
}
```

---

## 4. Dashboard Endpoints (Auth Required)

### GET `/api/v1/violations`

List violation history with optional filters.

**Authentication Required:** Yes

> **Note on Subject Data:** Violations of type `unauthorized_qr_scan` will have `subject: null` and `subjectType: null` since invalid/tampered QR codes cannot be linked to any known subject. All other violation types will include complete subject information.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number for pagination |
| `limit` | integer | No | 20 | Number of items per page (max: 100) |
| `type` | string | No | - | Filter by violation type |
| `subjectType` | string | No | - | Filter by subject type |
| `gateId` | string | No | - | Filter by gate ID |
| `startDate` | string (ISO 8601) | No | - | Filter violations from this date |
| `endDate` | string (ISO 8601) | No | - | Filter violations until this date |
| `resolved` | boolean | No | - | Filter by resolution status |

#### Example Request

```
GET /api/v1/violations?page=1&limit=20&type=face_verification_mismatch&startDate=2026-01-01T00:00:00Z
Authorization: Bearer <jwt_token>
```

#### Success Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "violations": [
      {
        "id": "vio_ghi789",
        "type": "face_verification_mismatch",
        "subjectType": "student",
        "subject": {
          "id": "stu_789xyz",
          "name": "Alice Johnson",
          "photoUrl": "https://cdn.campus-security.example.com/photos/stu_789xyz.jpg"
        },
        "gateId": "gate_main_entrance",
        "gateName": "Main Entrance Gate",
        "occurredAt": "2026-01-02T14:30:05Z",
        "details": {
          "confidence": 0.32,
          "capturedImageUrl": "https://cdn.campus-security.example.com/captures/vio_ghi789.jpg"
        },
        "resolved": false,
        "resolvedAt": null,
        "resolvedBy": null,
        "notes": null
      },
      {
        "id": "vio_abc123",
        "type": "unauthorized_qr_scan",
        "subjectType": null,
        "subject": null,
        "gateId": "gate_library",
        "gateName": "Library Gate",
        "occurredAt": "2026-01-02T11:45:00Z",
        "details": {
          "scannedQrCode": "INVALID_QR_DATA_xyz",
          "capturedImageUrl": "https://cdn.campus-security.example.com/captures/vio_abc123.jpg"
        },
        "resolved": true,
        "resolvedAt": "2026-01-02T12:00:00Z",
        "resolvedBy": {
          "id": "usr_abc123",
          "name": "John Smith"
        },
        "notes": "Investigated - student using old expired ID card"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "totalItems": 97,
      "itemsPerPage": 20,
      "hasNextPage": true,
      "hasPreviousPage": false
    }
  }
}
```

---

### POST `/api/v1/visitors/passes`

Create a new visitor pass with QR code.

**Authentication Required:** Yes

#### Request

```json
{
  "visitorName": "Bob Williams",
  "visitorEmail": "bob.williams@email.com",
  "visitorPhone": "+1-555-123-4567",
  "purpose": "Interview at HR Department",
  "hostEmployeeId": "EMP-2024-015",
  "validFrom": "2026-01-03T09:00:00Z",
  "validUntil": "2026-01-03T17:00:00Z",
  "allowedGates": ["gate_main_entrance", "gate_hr_building"],
  "notes": "Candidate for Software Engineer position"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `visitorName` | string | Yes | Full name of the visitor |
| `visitorEmail` | string | No | Visitor's email address |
| `visitorPhone` | string | No | Visitor's phone number |
| `purpose` | string | Yes | Purpose of the visit |
| `hostEmployeeId` | string | Yes | Employee ID of the host |
| `validFrom` | string (ISO 8601) | Yes | Start of pass validity period |
| `validUntil` | string (ISO 8601) | Yes | End of pass validity period |
| `allowedGates` | array of strings | No | List of gate IDs visitor can access (default: all) |
| `notes` | string | No | Additional notes about the visit |

#### Validation Rules

- `validFrom` must be in the future or within the last hour
- `validUntil` must be after `validFrom`
- Maximum pass duration: 24 hours
- `hostEmployeeId` must be a valid, active employee

#### Success Response (201 Created)

```json
{
  "status": "success",
  "data": {
    "passId": "vis_pass_new789",
    "visitorName": "Bob Williams",
    "visitorEmail": "bob.williams@email.com",
    "visitorPhone": "+1-555-123-4567",
    "purpose": "Interview at HR Department",
    "host": {
      "employeeId": "EMP-2024-015",
      "name": "Jane Doe",
      "department": "Human Resources",
      "email": "jane.doe@campus.edu"
    },
    "validFrom": "2026-01-03T09:00:00Z",
    "validUntil": "2026-01-03T17:00:00Z",
    "allowedGates": [
      {
        "id": "gate_main_entrance",
        "name": "Main Entrance Gate"
      },
      {
        "id": "gate_hr_building",
        "name": "HR Building Gate"
      }
    ],
    "qrCode": {
      "content": "QR-VIS-2026-NEW789XYZ",
      "imageUrl": "https://cdn.campus-security.example.com/qrcodes/vis_pass_new789.png",
      "imageBase64": "iVBORw0KGgoAAAANSUhEUgAA..."
    },
    "createdAt": "2026-01-02T15:00:00Z",
    "createdBy": {
      "id": "usr_abc123",
      "name": "John Smith"
    }
  }
}
```

#### Error Responses

**400 Bad Request - Validation Error**

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Validation failed",
  "details": [
    {
      "field": "validUntil",
      "message": "End time must be after start time"
    },
    {
      "field": "hostEmployeeId",
      "message": "Employee not found or inactive"
    }
  ]
}
```

---

## 5. WebSocket

### `/ws/alerts`

Real-time violation alerts stream for dashboard monitoring.

**Authentication Required:** No (but connection may be IP-restricted in production)

#### Connection

```javascript
const ws = new WebSocket('wss://api.campus-security.example.com/ws/alerts');

ws.onopen = () => {
  console.log('Connected to alerts stream');
};

ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  handleAlert(alert);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from alerts stream');
  // Implement reconnection logic
};
```

#### Alert Message Format

```json
{
  "type": "violation_alert",
  "timestamp": "2026-01-02T14:30:05Z",
  "data": {
    "violationId": "vio_ghi789",
    "violationType": "face_verification_mismatch",
    "severity": "high",
    "gate": {
      "id": "gate_main_entrance",
      "name": "Main Entrance Gate",
      "location": "Building A - North Side"
    },
    "subject": {
      "id": "stu_789xyz",
      "name": "Alice Johnson",
      "type": "student",
      "photoUrl": "https://cdn.campus-security.example.com/photos/stu_789xyz.jpg"
    },
    "capturedImageUrl": "https://cdn.campus-security.example.com/captures/vio_ghi789.jpg",
    "message": "Face verification failed at Main Entrance Gate"
  }
}
```

#### Alert Types

| Type | Severity | Description |
|------|----------|-------------|
| `violation_alert` | varies | New security violation detected |
| `system_status` | info | System health/status update |
| `gate_status` | info/warning | Gate online/offline status change |

#### Severity Levels

| Severity | Description |
|----------|-------------|
| `low` | Minor issue, informational |
| `medium` | Requires attention but not urgent |
| `high` | Urgent, requires immediate attention |
| `critical` | Security breach, immediate action required |

#### Heartbeat Messages

The server sends periodic heartbeat messages to keep the connection alive:

```json
{
  "type": "heartbeat",
  "timestamp": "2026-01-02T14:35:00Z"
}
```

Clients should respond with:

```json
{
  "type": "pong"
}
```

---

## 6. Data Types & Enums

### Violation Types

| Value | Description |
|-------|-------------|
| `unauthorized_qr_scan` | Invalid, tampered, or unrecognized QR code scanned |
| `face_verification_mismatch` | Captured face does not match the enrolled photo |
| `multiple_fail_attempt` | 3 or more verification failures within 5 minutes |
| `expired_visitor_qr_code` | Visitor pass has exceeded its validity period |

### Violation Data Persistence

Different violation types persist different levels of data to the database:

| Violation Type | Subject Info Saved | Captured Image Saved | Notes |
|----------------|-------------------|---------------------|-------|
| `unauthorized_qr_scan` | ❌ No | ✅ Yes (gate camera) | QR is invalid/tampered - no identifiable subject. Only raw QR data and gate camera capture stored for investigation. |
| `face_verification_mismatch` | ✅ Yes | ✅ Yes | Full subject info from QR + mismatched face image saved for security review. |
| `multiple_fail_attempt` | ✅ Yes | ✅ Yes (all attempts) | Subject info + all failed face captures saved to create audit trail. |
| `expired_visitor_qr_code` | ✅ Yes | ✅ Yes (gate camera) | Visitor info from expired pass saved along with gate camera capture. |

**Frontend Implications:**
- For `unauthorized_qr_scan`: The violations list will show `subject: null` and `subjectType: null`
- For all other violations: The violations list will include full subject details for display and filtering

### Subject Types

| Value | Description |
|-------|-------------|
| `student` | Enrolled student with active campus access |
| `staff` | Faculty or staff member |
| `visitor` | Temporary visitor with issued pass |

### User Roles

| Value | Description |
|-------|-------------|
| `security_officer` | Standard security personnel |
| `security_supervisor` | Supervisory access with enhanced permissions |
| `admin` | Full system administration access |

### Common Response Schemas

#### Subject Object (Student)

```json
{
  "id": "stu_789xyz",
  "name": "Alice Johnson",
  "photoUrl": "https://cdn.campus-security.example.com/photos/stu_789xyz.jpg",
  "department": "Computer Science",
  "enrollmentStatus": "active"
}
```

#### Subject Object (Staff)

```json
{
  "id": "stf_456abc",
  "name": "Dr. Robert Chen",
  "photoUrl": "https://cdn.campus-security.example.com/photos/stf_456abc.jpg",
  "department": "Engineering",
  "position": "Professor",
  "employmentStatus": "active"
}
```

#### Subject Object (Visitor)

```json
{
  "id": "vis_pass_789",
  "name": "Bob Williams",
  "photoUrl": null,
  "purpose": "Interview at HR Department",
  "hostName": "Jane Doe",
  "hostDepartment": "Human Resources",
  "validFrom": "2026-01-02T09:00:00Z",
  "validUntil": "2026-01-02T17:00:00Z"
}
```

#### Gate Object

```json
{
  "id": "gate_main_entrance",
  "name": "Main Entrance Gate",
  "location": "Building A - North Side",
  "status": "online"
}
```

#### Pagination Object

```json
{
  "currentPage": 1,
  "totalPages": 5,
  "totalItems": 97,
  "itemsPerPage": 20,
  "hasNextPage": true,
  "hasPreviousPage": false
}
```

---

## 7. Flow Diagrams

### QR Scan + Face Verification Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Gate       │     │   Backend   │     │  Dashboard  │
│  Scanner    │     │   Server    │     │  (WebSocket)│
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  POST /scan/qr    │                   │
       │──────────────────>│                   │
       │                   │                   │
       │    QR Valid?      │                   │
       │<──────────────────│                   │
       │                   │                   │
       ├─── If Invalid ────┼───────────────────┤
       │                   │                   │
       │                   │  violation_alert  │
       │                   │──────────────────>│
       │                   │                   │
       │   ACCESS DENIED   │                   │
       │<──────────────────│                   │
       │                   │                   │
       ├─── If Valid ──────┤                   │
       │                   │                   │
       │   Capture Face    │                   │
       │                   │                   │
       │ POST /face/verify │                   │
       │──────────────────>│                   │
       │                   │                   │
       │   Face Match?     │                   │
       │<──────────────────│                   │
       │                   │                   │
       ├─── If Mismatch ───┼───────────────────┤
       │                   │                   │
       │                   │  violation_alert  │
       │                   │──────────────────>│
       │                   │                   │
       │   ACCESS DENIED   │                   │
       │<──────────────────│                   │
       │                   │                   │
       ├─── If Match ──────┤                   │
       │                   │                   │
       │  ACCESS GRANTED   │                   │
       │<──────────────────│                   │
       │                   │                   │
       ▼                   ▼                   ▼
```

### Error Scenarios and Violation Triggers

```
┌────────────────────────────────────────────────────────────────────┐
│                    VIOLATION TRIGGER CONDITIONS                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐                                                │
│  │  QR Code Scan   │                                                │
│  └────────┬────────┘                                                │
│           │                                                         │
│           ▼                                                         │
│  ┌────────────────────────────────────────────┐                     │
│  │ Is QR code format valid & signature ok?    │                     │
│  └────────────────────┬───────────────────────┘                     │
│                       │                                             │
│         ┌─── NO ──────┴─────── YES ───┐                             │
│         │                             │                             │
│         ▼                             ▼                             │
│  ┌──────────────────┐     ┌─────────────────────────┐               │
│  │ VIOLATION:       │     │ Is QR for a visitor?    │               │
│  │ unauthorized_    │     └───────────┬─────────────┘               │
│  │ qr_scan          │                 │                             │
│  └──────────────────┘       ┌── YES ──┴── NO ──┐                    │
│                             │                  │                    │
│                             ▼                  ▼                    │
│              ┌─────────────────────┐  ┌───────────────────┐         │
│              │ Is pass expired?    │  │ Face Verification │         │
│              └──────────┬──────────┘  └─────────┬─────────┘         │
│                         │                       │                   │
│            ┌── YES ─────┴───── NO ──┐           │                   │
│            │                        │           │                   │
│            ▼                        ▼           ▼                   │
│  ┌──────────────────┐    ┌────────────────────────────────┐         │
│  │ VIOLATION:       │    │ Does face match enrolled?      │         │
│  │ expired_visitor_ │    └───────────────┬────────────────┘         │
│  │ qr_code          │                    │                          │
│  └──────────────────┘      ┌─── YES ─────┴───── NO ───┐             │
│                            │                          │             │
│                            ▼                          ▼             │
│                  ┌──────────────────┐    ┌────────────────────────┐ │
│                  │  ACCESS GRANTED  │    │ 3+ failures in 5 min?  │ │
│                  └──────────────────┘    └───────────┬────────────┘ │
│                                                      │              │
│                                         ┌── YES ─────┴───── NO ──┐  │
│                                         │                        │  │
│                                         ▼                        ▼  │
│                              ┌──────────────────┐  ┌────────────────┐
│                              │ VIOLATION:       │  │ VIOLATION:     │
│                              │ multiple_fail_   │  │ face_verifi-   │
│                              │ attempt          │  │ cation_mismatch│
│                              │ (+ lockout)      │  └────────────────┘
│                              └──────────────────┘                   │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Visitor Pass Creation Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Security   │     │   Backend   │     │   Email     │
│  Dashboard  │     │   Server    │     │   Service   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ POST /visitors/   │                   │
       │ passes            │                   │
       │──────────────────>│                   │
       │                   │                   │
       │                   │ Validate host     │
       │                   │ employee exists   │
       │                   │                   │
       │                   │ Generate QR code  │
       │                   │                   │
       │                   │ Store visitor pass│
       │                   │                   │
       │   Pass Created    │                   │
       │   + QR Code       │                   │
       │<──────────────────│                   │
       │                   │                   │
       │                   │ Send notification │
       │                   │ to host + visitor │
       │                   │──────────────────>│
       │                   │                   │
       │                   │   Email sent      │
       │                   │<──────────────────│
       │                   │                   │
       ▼                   ▼                   ▼
```

---

## Appendix: HTTP Status Codes Reference

| Status Code | Usage |
|-------------|-------|
| 200 OK | Successful GET, PUT, or scan/verify operations |
| 201 Created | Successful POST that creates a resource |
| 400 Bad Request | Invalid request payload or parameters |
| 401 Unauthorized | Missing or invalid authentication |
| 403 Forbidden | Authenticated but not authorized |
| 404 Not Found | Resource does not exist |
| 422 Unprocessable Entity | Validation errors |
| 423 Locked | Account/resource temporarily locked |
| 429 Too Many Requests | Rate limit exceeded |
| 500 Internal Server Error | Server-side error |

---

*Document Version: 1.1.0*  
*Last Updated: January 2, 2026*  
*Changelog: v1.1.0 - Added data persistence behavior documentation for violation types*

