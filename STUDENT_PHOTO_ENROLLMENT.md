# Student Photo Enrollment API

## Overview

This document describes the Student Photo Enrollment endpoint that allows security staff to upload base photos for students. These photos serve as the reference images for face verification at campus gates.

## Endpoint Details

### POST `/api/v1/students/enroll-photo`

Upload or update a student's base photo for face verification.

**Authentication:** Required (Bearer Token)

**Tags:** Students

---

## Request

### Headers

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Request Body

```json
{
  "studentId": "stu_789xyz",
  "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `studentId` | string | Yes | The unique ID of the student |
| `photo` | string | Yes | Base64 encoded image with data URI prefix (e.g., `data:image/jpeg;base64,...`) |

#### Supported Image Formats

- JPEG/JPG
- PNG
- GIF

The photo should be a clear, frontal face image with good lighting for optimal face verification accuracy.

---

## Response

### Success Response (200 OK)

```json
{
  "status": "success",
  "message": "Student photo enrolled successfully",
  "data": {
    "studentId": "stu_789xyz",
    "photoUrl": "https://cdn.campus-security.example.com/photos/stu_789xyz_20260103100000.jpg"
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `studentId` | string | The student's unique ID |
| `photoUrl` | string | CDN URL of the uploaded photo (used for face verification) |

### Error Responses

#### 401 Unauthorized - Invalid/Missing Token

```json
{
  "detail": "Invalid or expired authentication token"
}
```

#### 404 Not Found - Student Does Not Exist

```json
{
  "detail": {
    "status": "error",
    "code": "STUDENT_NOT_FOUND",
    "message": "Student with ID 'stu_invalid' not found"
  }
}
```

#### 400 Bad Request - Invalid Image Format

```json
{
  "detail": "Invalid base64 image format: <error details>"
}
```

---

## Usage Examples

### JavaScript/TypeScript (Fetch API)

```javascript
async function enrollStudentPhoto(studentId, photoBase64, token) {
  const response = await fetch('http://localhost:8000/api/v1/students/enroll-photo', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      studentId: studentId,
      photo: photoBase64
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log('Photo enrolled successfully:', data.data.photoUrl);
  return data;
}

// Usage with file input
document.getElementById('photoInput').addEventListener('change', async (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = async (e) => {
      const base64Image = e.target.result; // Already in data:image/jpeg;base64,... format
      const token = localStorage.getItem('authToken');
      
      try {
        await enrollStudentPhoto('stu_789xyz', base64Image, token);
        alert('Photo enrolled successfully!');
      } catch (error) {
        console.error('Error enrolling photo:', error);
        alert('Failed to enroll photo');
      }
    };
    reader.readAsDataURL(file);
  }
});
```

### Python (requests)

```python
import requests
import base64

def enroll_student_photo(student_id: str, image_path: str, token: str):
    # Read and encode the image
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Determine image format from file extension
    image_format = 'jpeg' if image_path.endswith(('.jpg', '.jpeg')) else 'png'
    photo_data_uri = f"data:image/{image_format};base64,{encoded_image}"
    
    # Make the API request
    response = requests.post(
        'http://localhost:8000/api/v1/students/enroll-photo',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={
            'studentId': student_id,
            'photo': photo_data_uri
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Photo enrolled successfully: {data['data']['photoUrl']}")
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        raise Exception(f"Failed to enroll photo: {response.text}")

# Usage
token = "your_jwt_token_here"
result = enroll_student_photo('stu_789xyz', 'path/to/photo.jpg', token)
```

### cURL

```bash
# First, encode your image to base64
IMAGE_BASE64=$(base64 -w 0 student_photo.jpg)
DATA_URI="data:image/jpeg;base64,${IMAGE_BASE64}"

# Make the API request
curl -X POST http://localhost:8000/api/v1/students/enroll-photo \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"studentId\": \"stu_789xyz\",
    \"photo\": \"${DATA_URI}\"
  }"
```

---

## Integration with Face Verification

Once a student's photo is enrolled:

1. The photo is saved to the `student_photos/` directory
2. The `photo_url` field in the student's database record is updated
3. The `/api/v1/scan/face/verify` endpoint uses this photo as the reference for face matching

### Face Verification Flow

```
1. Student scans QR code at gate
   └─> POST /api/v1/scan/qr
       └─> Returns student info including photoUrl

2. Gate camera captures face image
   └─> POST /api/v1/scan/face/verify
       └─> Compares captured image with enrolled photoUrl
       └─> Returns verification result (match/mismatch)
```

**Important:** Students without an enrolled photo (`photoUrl: null`) can still scan their QR code, but face verification will fail or be skipped.

---

## File Storage

### Current Implementation

Photos are stored in the `student_photos/` directory with the naming pattern:
```
{studentId}_{timestamp}.{extension}
```

Example: `stu_789xyz_20260103100000.jpg`

### Production Considerations

In a production environment, you should:

1. **Use a CDN/Cloud Storage:**
   - AWS S3 + CloudFront
   - Google Cloud Storage
   - Azure Blob Storage

2. **Implement Image Optimization:**
   - Resize images to a standard resolution (e.g., 512x512)
   - Compress images to reduce storage and bandwidth
   - Convert to WebP for better compression

3. **Add Security Measures:**
   - Scan uploaded images for malware
   - Validate image dimensions and file size
   - Implement rate limiting to prevent abuse

4. **Handle Old Photos:**
   - Archive or delete old photos when new ones are uploaded
   - Implement a cleanup job for orphaned photos

---

## Testing

### Unit Test Example

```python
def test_student_photo_enrollment(client, auth_token, session):
    """Test enrolling a student's photo for face verification"""
    from app.models.student import Student
    
    # Get a student from the database
    student = session.exec(select(Student)).first()
    
    # Minimal valid base64 encoded 1x1 pixel JPEG image for testing
    test_photo_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
    
    # Enroll the photo
    response = client.post(
        "/api/v1/students/enroll-photo",
        json={
            "studentId": student.id,
            "photo": test_photo_base64
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "photoUrl" in response.json()["data"]
```

Run tests with:
```bash
pytest tests/test_endpoints.py::test_student_photo_enrollment -v
```

---

## Security Considerations

1. **Authentication Required:** Only authenticated security staff can upload photos
2. **Student Validation:** The endpoint verifies that the student exists before accepting the photo
3. **Input Validation:** Base64 decoding errors are caught and return appropriate error messages
4. **File System Security:** Photos are stored outside the web root to prevent direct access

---

## Database Schema

### Students Table

The endpoint updates the `students` table:

```sql
CREATE TABLE students (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    photo_url VARCHAR,  -- Updated by this endpoint
    department_id INTEGER,
    enrollment_status VARCHAR NOT NULL,
    qr_code VARCHAR UNIQUE NOT NULL,
    enrolled_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL  -- Updated by this endpoint
);
```

---

## Rate Limiting (Future Enhancement)

Consider implementing rate limiting for this endpoint:

```python
# Example using slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/enroll-photo")
@limiter.limit("10/minute")  # Max 10 photo uploads per minute per IP
async def enroll_student_photo(...):
    ...
```

---

## Troubleshooting

### Common Issues

**Issue:** `Student with ID 'xxx' not found`
- **Solution:** Verify the student exists in the database. Use the student management system to check the student ID.

**Issue:** `Invalid base64 image format`
- **Solution:** Ensure the image is properly encoded as base64 with the data URI prefix (e.g., `data:image/jpeg;base64,...`)

**Issue:** `Invalid or expired authentication token`
- **Solution:** Get a new authentication token by logging in again through `/api/v1/auth/login`

**Issue:** Photos not appearing in face verification
- **Solution:** 
  1. Check that `photo_url` was updated in the database
  2. Verify the file exists in the `student_photos/` directory
  3. Ensure the face verification service can access the stored photos

---

## Related Endpoints

- **POST `/api/v1/auth/login`** - Authenticate to get a bearer token
- **POST `/api/v1/scan/qr`** - Scan student QR code (returns photoUrl)
- **POST `/api/v1/scan/face/verify`** - Verify face against enrolled photo

---

## Changelog

### Version 1.0.0 (2026-01-03)
- Initial implementation
- Support for JPEG, PNG, and GIF formats
- Base64 decoding with data URI prefix support
- File storage in `student_photos/` directory
- Authentication required via Bearer token
- Photo URL returned in CDN format for future cloud migration
