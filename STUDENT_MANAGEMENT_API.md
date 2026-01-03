# Student Management API - Complete CRUD Operations

## Overview

The Student Management API now includes **full CRUD operations** for managing students, including creating students with QR codes and photos.

---

## 🆕 NEW: Create Student Endpoint

### POST `/api/v1/students`

Create a new student with optional photo and QR code.

**Authentication:** Required (Bearer Token)

#### Request Body

```json
{
  "name": "Alice Johnson",
  "email": "alice.johnson@campus.edu",
  "departmentId": 1,
  "qrCode": "QR-STU-2024-ABC123XYZ",  // Optional - auto-generated if not provided
  "photo": "data:image/jpeg;base64,..."  // Optional - base64 encoded image
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | **Yes** | Full name of the student |
| `email` | string (email) | **Yes** | Student's email address (must be unique) |
| `departmentId` | integer | No | Department ID (must exist in departments table) |
| `qrCode` | string | No | Custom QR code (auto-generated if not provided) |
| `photo` | string | No | Base64 encoded image with data URI prefix |

#### Success Response (201 Created)

```json
{
  "status": "success",
  "data": {
    "id": "stu_a1b2c3d4",
    "name": "Alice Johnson",
    "email": "alice.johnson@campus.edu",
    "photoUrl": "https://cdn.campus-security.example.com/photos/stu_a1b2c3d4_20260103100000.jpg",
    "departmentId": 1,
    "department": "Computer Science",
    "enrollmentStatus": "active",
    "qrCode": "QR-STU-2024-A1B2C3D4E5F6",
    "enrolledAt": "2026-01-03T10:00:00Z",
    "createdAt": "2026-01-03T10:00:00Z",
    "updatedAt": "2026-01-03T10:00:00Z"
  }
}
```

#### Error Responses

**400 Bad Request - Email Already Exists**
```json
{
  "detail": {
    "status": "error",
    "code": "EMAIL_EXISTS",
    "message": "A student with this email already exists"
  }
}
```

**400 Bad Request - QR Code Already in Use**
```json
{
  "detail": {
    "status": "error",
    "code": "QR_CODE_EXISTS",
    "message": "This QR code is already in use"
  }
}
```

**404 Not Found - Department Not Found**
```json
{
  "detail": {
    "status": "error",
    "code": "DEPARTMENT_NOT_FOUND",
    "message": "Department not found"
  }
}
```

---

## GET `/api/v1/students`

List all students with pagination.

**Authentication:** Required (Bearer Token)

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | 1 | Page number (1-indexed) |
| `limit` | integer | No | 20 | Items per page (max 100) |

#### Success Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "students": [
      {
        "id": "stu_a1b2c3d4",
        "name": "Alice Johnson",
        "email": "alice.johnson@campus.edu",
        "photoUrl": "https://cdn.campus-security.example.com/photos/stu_a1b2c3d4_20260103100000.jpg",
        "departmentId": 1,
        "department": "Computer Science",
        "enrollmentStatus": "active",
        "qrCode": "QR-STU-2024-A1B2C3D4E5F6",
        "enrolledAt": "2026-01-03T10:00:00Z",
        "createdAt": "2026-01-03T10:00:00Z",
        "updatedAt": "2026-01-03T10:00:00Z"
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

## GET `/api/v1/students/{student_id}`

Get a single student by ID.

**Authentication:** Required (Bearer Token)

#### Success Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "id": "stu_a1b2c3d4",
    "name": "Alice Johnson",
    "email": "alice.johnson@campus.edu",
    "photoUrl": "https://cdn.campus-security.example.com/photos/stu_a1b2c3d4_20260103100000.jpg",
    "departmentId": 1,
    "department": "Computer Science",
    "enrollmentStatus": "active",
    "qrCode": "QR-STU-2024-A1B2C3D4E5F6",
    "enrolledAt": "2026-01-03T10:00:00Z",
    "createdAt": "2026-01-03T10:00:00Z",
    "updatedAt": "2026-01-03T10:00:00Z"
  }
}
```

---

## PATCH `/api/v1/students/{student_id}`

Update a student's information, including their QR code.

**Authentication:** Required (Bearer Token)

#### Request Body

All fields are optional - only provide the fields you want to update:

```json
{
  "name": "Alice M. Johnson",
  "email": "alice.m.johnson@campus.edu",
  "departmentId": 2,
  "qrCode": "QR-STU-2024-NEWCODE",
  "enrollmentStatus": "suspended"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full name of the student |
| `email` | string (email) | Student's email address |
| `departmentId` | integer | Department ID |
| `qrCode` | string | QR code (must be unique) |
| `enrollmentStatus` | string | Status: `active`, `suspended`, `graduated` |

#### Success Response (200 OK)

```json
{
  "status": "success",
  "data": {
    "id": "stu_a1b2c3d4",
    "name": "Alice M. Johnson",
    "email": "alice.m.johnson@campus.edu",
    "photoUrl": "https://cdn.campus-security.example.com/photos/stu_a1b2c3d4_20260103100000.jpg",
    "departmentId": 2,
    "department": "Engineering",
    "enrollmentStatus": "suspended",
    "qrCode": "QR-STU-2024-NEWCODE",
    "enrolledAt": "2026-01-03T10:00:00Z",
    "createdAt": "2026-01-03T10:00:00Z",
    "updatedAt": "2026-01-03T10:35:00Z"
  }
}
```

---

## POST `/api/v1/students/enroll-photo`

Enroll or update a student's photo (existing endpoint - unchanged).

See `STUDENT_PHOTO_ENROLLMENT.md` for details.

---

## Complete Workflow Examples

### 1. Create Student with Photo and QR Code

```javascript
// Step 1: Create student with everything in one request
const response = await fetch('http://localhost:8000/api/v1/students', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Alice Johnson',
    email: 'alice@campus.edu',
    departmentId: 1,
    qrCode: 'QR-STU-2024-ALICE123',  // Optional
    photo: 'data:image/jpeg;base64,...'  // Optional
  })
});

const data = await response.json();
console.log('Student created:', data.data);
console.log('QR Code:', data.data.qrCode);
console.log('Photo URL:', data.data.photoUrl);
```

### 2. Create Student, Then Add Photo Later

```javascript
// Step 1: Create student without photo
const createResponse = await fetch('http://localhost:8000/api/v1/students', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Bob Smith',
    email: 'bob@campus.edu',
    departmentId: 1
  })
});

const studentData = await createResponse.json();
const studentId = studentData.data.id;
const qrCode = studentData.data.qrCode;  // Auto-generated!

console.log('Student created with QR code:', qrCode);

// Step 2: Add photo later
const photoResponse = await fetch('http://localhost:8000/api/v1/students/enroll-photo', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    studentId: studentId,
    photo: 'data:image/jpeg;base64,...'
  })
});

const photoData = await photoResponse.json();
console.log('Photo added:', photoData.data.photoUrl);
```

### 3. Update Student's QR Code

```javascript
// Update QR code if the physical card is replaced
const response = await fetch(`http://localhost:8000/api/v1/students/${studentId}`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    qrCode: 'QR-STU-2024-NEWCARD456'
  })
});

const data = await response.json();
console.log('QR code updated:', data.data.qrCode);
```

---

## Python Example

```python
import requests

API_BASE = "http://localhost:8000/api/v1"
token = "your_jwt_token_here"

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Create student
response = requests.post(
    f"{API_BASE}/students",
    headers=headers,
    json={
        'name': 'Alice Johnson',
        'email': 'alice@campus.edu',
        'departmentId': 1,
        # QR code will be auto-generated
    }
)

if response.status_code == 201:
    student = response.json()['data']
    print(f"✅ Student created!")
    print(f"   ID: {student['id']}")
    print(f"   QR Code: {student['qrCode']}")
    
    # Now add photo
    with open('alice_photo.jpg', 'rb') as f:
        import base64
        photo_b64 = base64.b64encode(f.read()).decode()
        photo_data_uri = f"data:image/jpeg;base64,{photo_b64}"
    
    photo_response = requests.post(
        f"{API_BASE}/students/enroll-photo",
        headers=headers,
        json={
            'studentId': student['id'],
            'photo': photo_data_uri
        }
    )
    
    if photo_response.status_code == 200:
        photo_data = photo_response.json()['data']
        print(f"✅ Photo added: {photo_data['photoUrl']}")
```

---

## Key Features

### Automatic QR Code Generation
- If you don't provide a `qrCode`, one is automatically generated
- Format: `QR-STU-{YEAR}-{12 random hex characters}`
- Example: `QR-STU-2024-A1B2C3D4E5F6`
- Guaranteed to be unique

### Student ID Generation
- Student IDs are automatically generated
- Format: `stu_{8 random hex characters}`
- Example: `stu_a1b2c3d4`

### Photo Handling
- Photos can be provided during creation OR added later
- Base64 encoding with data URI prefix supported
- Same storage mechanism as `enroll-photo` endpoint

### QR Code Updates
- QR codes can be updated via PATCH endpoint
- Useful when physical ID cards are replaced
- Uniqueness is validated

---

## Summary

**Now you can:**
✅ Create students with automatic QR code generation  
✅ Provide custom QR codes if needed  
✅ Add photos during creation or later  
✅ Update student information including QR codes  
✅ List all students with pagination  
✅ Get individual student details  

**Your workflow:**
1. **Create student** → Get auto-generated QR code
2. **Add photo** (now or later) → Ready for face verification
3. **Student scans QR** at gate → Face verification compares against photo

---

## Migration Note

If you have existing students without QR codes, you can use the PATCH endpoint to add them:

```bash
curl -X PATCH http://localhost:8000/api/v1/students/stu_789xyz \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"qrCode": "QR-STU-2024-EXISTING123"}'
```

---

**Last Updated:** 2026-01-03  
**API Version:** 1.2.0 (Added full CRUD operations)
