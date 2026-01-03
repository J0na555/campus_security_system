# Student Photo Enrollment - System Integration

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      STUDENT PHOTO ENROLLMENT FLOW                       │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Security   │
    │   Dashboard  │
    │   (Frontend) │
    └──────┬───────┘
           │
           │ 1. Login to get JWT token
           │
           ▼
    ┌──────────────────────────┐
    │ POST /api/v1/auth/login  │
    │ {"employeeId": "...",    │
    │  "password": "..."}      │
    └──────┬───────────────────┘
           │
           │ 2. Returns JWT token
           │
           ▼
    ┌──────────────────────────────────────────────┐
    │  Security Staff uploads student photo via:   │
    │  POST /api/v1/students/enroll-photo         │
    │  Authorization: Bearer <jwt_token>           │
    │  {                                           │
    │    "studentId": "stu_789xyz",               │
    │    "photo": "data:image/jpeg;base64,..."   │
    │  }                                           │
    └──────┬───────────────────────────────────────┘
           │
           │ 3. Validate & Save Photo
           │
           ▼
    ┌─────────────────────────────────────────┐
    │        StudentService.enroll_photo()    │
    │  ┌──────────────────────────────────┐  │
    │  │ 1. Verify student exists in DB   │  │
    │  │ 2. Decode base64 image           │  │
    │  │ 3. Save to student_photos/ dir   │  │
    │  │ 4. Update students.photo_url     │  │
    │  │ 5. Update students.updated_at    │  │
    │  └──────────────────────────────────┘  │
    └─────────────────┬───────────────────────┘
                      │
                      │ 4. Return photo URL
                      │
                      ▼
    ┌──────────────────────────────────────────────┐
    │  Response:                                   │
    │  {                                           │
    │    "status": "success",                     │
    │    "data": {                                │
    │      "studentId": "stu_789xyz",            │
    │      "photoUrl": "https://cdn.../photo.jpg"│
    │    }                                         │
    │  }                                           │
    └──────────────────┬───────────────────────────┘
                       │
                       │
    ╔══════════════════╧═════════════════════════════════════════════╗
    ║           PHOTO NOW AVAILABLE FOR FACE VERIFICATION            ║
    ╚══════════════════╤═════════════════════════════════════════════╝
                       │
                       │
    ┌──────────────────┴──────────────────────────────────────┐
    │                                                          │
    ▼                                                          ▼
┌────────────────────┐                              ┌──────────────────┐
│  Gate QR Scanner   │                              │  Face Verification│
│                    │                              │  System          │
└────────┬───────────┘                              └──────┬───────────┘
         │                                                 │
         │ 5. Student scans QR                            │
         │                                                 │
         ▼                                                 │
┌──────────────────────────┐                              │
│ POST /api/v1/scan/qr     │                              │
│ {"qrCode": "...",        │                              │
│  "gateId": "...",        │                              │
│  "scanTimestamp": "..."} │                              │
└──────┬───────────────────┘                              │
       │                                                   │
       │ 6. Returns student info with photoUrl            │
       │                                                   │
       ▼                                                   │
┌──────────────────────────┐                              │
│ Response includes:       │                              │
│ {                        │                              │
│   "subject": {           │                              │
│     "photoUrl": "..."    │◄────────────────────────────┤
│   }                      │  7. Uses this URL for       │
│ }                        │     face comparison         │
└──────┬───────────────────┘                              │
       │                                                   │
       │ 8. Capture face at gate                          │
       │                                                   │
       ▼                                                   │
┌──────────────────────────────┐                          │
│ POST /api/v1/scan/face/verify│                          │
│ {                            │                          │
│   "subjectId": "stu_789xyz", │──────────────────────────┘
│   "faceImage": "base64...",  │  9. Compare captured face
│   "subjectType": "student"   │     with enrolled photo
│ }                            │
└──────┬───────────────────────┘
       │
       │ 10. Return match result
       │
       ▼
┌──────────────────────────┐
│ {"verified": true,       │
│  "confidence": 0.94,     │
│  "accessGranted": true}  │
└──────────────────────────┘
       │
       │ 11. Gate opens/closes
       │
       ▼
   [Access Granted/Denied]


═══════════════════════════════════════════════════════════════════════

                         DATABASE SCHEMA

┌─────────────────────────────────────────────────────────────────┐
│                         STUDENTS TABLE                          │
├─────────────────────────────────────────────────────────────────┤
│ id              │ VARCHAR  │ PK       │ "stu_789xyz"           │
│ name            │ VARCHAR  │          │ "Alice Johnson"        │
│ email           │ VARCHAR  │ UNIQUE   │ "alice@campus.edu"     │
│ photo_url       │ VARCHAR  │ NULLABLE │ "https://cdn.../..." ◄─── UPDATED
│ department_id   │ INTEGER  │ FK       │ 1                      │
│ enrollment_status│VARCHAR  │          │ "active"               │
│ qr_code         │ VARCHAR  │ UNIQUE   │ "QR-STU-2024-..."      │
│ enrolled_at     │ TIMESTAMP│          │ "2024-09-01..."        │
│ created_at      │ TIMESTAMP│          │ "2024-09-01..."        │
│ updated_at      │ TIMESTAMP│          │ "2026-01-03..." ◄────── UPDATED
└─────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════

                     FILE SYSTEM STRUCTURE

project_root/
├── app/
│   ├── routers/
│   │   └── students.py              ← NEW ROUTER
│   ├── services/
│   │   └── student_service.py       ← NEW SERVICE
│   └── schemas/
│       └── student.py                ← UPDATED SCHEMAS
│
└── student_photos/                   ← NEW DIRECTORY
    ├── stu_789xyz_20260103100000.jpg
    ├── stu_456abc_20260103100500.jpg
    └── ...

                    ▲
                    │
                    │ Photos stored here
                    │ Filename: {studentId}_{timestamp}.{ext}
                    │


═══════════════════════════════════════════════════════════════════

                       AUTHENTICATION FLOW

    ┌──────────────┐
    │   Frontend   │
    └──────┬───────┘
           │
           │ Login Request
           ▼
    ┌──────────────────────┐
    │  AuthService         │
    │  - Verify password   │
    │  - Create JWT token  │
    └──────┬───────────────┘
           │
           │ JWT Token
           ▼
    ┌──────────────────────────┐
    │  Frontend stores token   │
    └──────┬───────────────────┘
           │
           │ All subsequent requests include:
           │ Authorization: Bearer <token>
           ▼
    ┌────────────────────────────┐
    │  Protected Endpoint        │
    │  (enroll-photo)           │
    │  - Validates token         │
    │  - Extracts user info      │
    │  - Authorizes request      │
    └────────────────────────────┘


═══════════════════════════════════════════════════════════════════

                      ERROR HANDLING

    Request to /api/v1/students/enroll-photo
                     │
                     ▼
          ┌──────────────────────┐
          │ No/Invalid Token?    │──── YES ──► 401 Unauthorized
          └──────┬───────────────┘
                 │ NO
                 ▼
          ┌──────────────────────┐
          │ Student exists?      │──── NO ───► 404 Not Found
          └──────┬───────────────┘            "STUDENT_NOT_FOUND"
                 │ YES
                 ▼
          ┌──────────────────────┐
          │ Valid base64 image?  │──── NO ───► 400 Bad Request
          └──────┬───────────────┘            "Invalid base64 format"
                 │ YES
                 ▼
          ┌──────────────────────┐
          │ Save image & update  │
          │ database             │
          └──────┬───────────────┘
                 │
                 ▼
          ┌──────────────────────┐
          │ 200 OK              │
          │ Return photoUrl     │
          └─────────────────────┘


═══════════════════════════════════════════════════════════════════

                    SECURITY CONSIDERATIONS

    ┌─────────────────────────────────────────────────────────┐
    │                  SECURITY LAYERS                        │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │  1. Authentication (JWT Bearer Token)                   │
    │     └─ Only authenticated security staff can upload     │
    │                                                         │
    │  2. Authorization                                       │
    │     └─ Token must be valid and not expired             │
    │                                                         │
    │  3. Input Validation                                    │
    │     └─ Pydantic schemas validate request structure     │
    │                                                         │
    │  4. Student Verification                                │
    │     └─ Student must exist in database                  │
    │                                                         │
    │  5. File Type Validation                                │
    │     └─ Only JPEG, PNG, GIF accepted                    │
    │                                                         │
    │  6. Error Message Safety                                │
    │     └─ No sensitive data in error responses            │
    │                                                         │
    │  7. File System Security                                │
    │     └─ Photos stored outside web root                  │
    │                                                         │
    └─────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════

                   INTEGRATION SUMMARY

┌─────────────────────────────────────────────────────────────────┐
│                    COMPONENT INTERACTIONS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Frontend Dashboard                                             │
│       │                                                         │
│       ├─► Auth Router ────────► AuthService                    │
│       │                              │                         │
│       │                              └─► JWT Token             │
│       │                                                         │
│       └─► Students Router ───► StudentService                  │
│                 │                    │                         │
│                 │                    ├─► Decode Base64         │
│                 │                    ├─► Save File             │
│                 │                    └─► Update DB             │
│                 │                                               │
│                 └─► Database (students table)                  │
│                                                                 │
│  Gate Scanner                                                   │
│       │                                                         │
│       ├─► Scan Router ────────► QRService                      │
│       │                              │                         │
│       │                              └─► Returns photoUrl      │
│       │                                                         │
│       └─► Scan Router ────────► FaceMatchService               │
│                                      │                         │
│                                      └─► Uses photoUrl         │
│                                          for verification      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

```
