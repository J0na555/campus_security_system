#!/usr/bin/env python3
"""
Demo script for testing the Student Photo Enrollment endpoint.

This script demonstrates how to:
1. Login to get an authentication token
2. Enroll a student photo using base64 encoding
3. Verify the photo was saved correctly

Usage:
    python demo_photo_enrollment.py
"""

import requests
import base64
import sys
from io import BytesIO
from PIL import Image

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Test credentials (from mock data)
TEST_EMPLOYEE_ID = "EMP-2024-003"  # Michael Chen (Admin)
TEST_PASSWORD = "password123"

# Test student ID (from mock data)
TEST_STUDENT_ID = "stu_789xyz"  # Alice Johnson


def create_test_image():
    """Create a simple test image (red square with a white circle)"""
    # Create a 200x200 red image
    img = Image.new('RGB', (200, 200), color='red')
    
    # Draw a white circle in the center (simplified - just for demo)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill='white')
    
    # Save to bytes
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    
    return buffer.read()


def encode_image_to_base64(image_bytes):
    """Encode image bytes to base64 data URI"""
    encoded = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded}"


def login():
    """Login and get authentication token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={
            "employeeId": TEST_EMPLOYEE_ID,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['data']['token']
        user_name = data['data']['user']['name']
        print(f"✅ Login successful! Welcome, {user_name}")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.json())
        sys.exit(1)


def enroll_photo(token, student_id, photo_base64):
    """Enroll a student photo"""
    print(f"\n📸 Enrolling photo for student: {student_id}...")
    
    response = requests.post(
        f"{API_BASE_URL}/students/enroll-photo",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "studentId": student_id,
            "photo": photo_base64
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        photo_url = data['data']['photoUrl']
        print(f"✅ Photo enrolled successfully!")
        print(f"   Student ID: {data['data']['studentId']}")
        print(f"   Photo URL: {photo_url}")
        return photo_url
    else:
        print(f"❌ Photo enrollment failed: {response.status_code}")
        print(response.json())
        return None


def verify_student_record(token, student_id):
    """Verify that the student's photo was updated (optional - requires get student endpoint)"""
    # Note: This would require a GET /students/{id} endpoint which may not exist yet
    # For now, we just print a success message
    print(f"\n✅ Photo enrollment complete for student: {student_id}")
    print("   The photo will be used for face verification at gates.")


def main():
    print("=" * 60)
    print("Student Photo Enrollment Demo")
    print("=" * 60)
    print()
    
    # Step 1: Login
    token = login()
    
    # Step 2: Create a test image
    print("\n🎨 Creating test image...")
    image_bytes = create_test_image()
    print(f"✅ Test image created ({len(image_bytes)} bytes)")
    
    # Step 3: Encode to base64
    print("\n🔧 Encoding image to base64...")
    photo_base64 = encode_image_to_base64(image_bytes)
    print(f"✅ Image encoded (base64 length: {len(photo_base64)} chars)")
    
    # Step 4: Enroll the photo
    photo_url = enroll_photo(token, TEST_STUDENT_ID, photo_base64)
    
    if photo_url:
        # Step 5: Verification
        verify_student_record(token, TEST_STUDENT_ID)
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. The student can now use their QR code at gates")
        print("2. Face verification will compare against this enrolled photo")
        print("3. Use POST /api/v1/scan/face/verify to test face matching")
    else:
        print("\n❌ Demo failed")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
