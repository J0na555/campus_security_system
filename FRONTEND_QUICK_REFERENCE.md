# Student Photo Enrollment - Frontend Quick Reference

## 🚀 Quick Start

### Endpoint
```
POST http://localhost:8000/api/v1/students/enroll-photo
```

### Authentication
```javascript
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 📝 Request Format

```javascript
{
  "studentId": "stu_789xyz",      // Required: Student's unique ID
  "photo": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."  // Required: Base64 encoded image
}
```

---

## ✅ Success Response (200 OK)

```javascript
{
  "status": "success",
  "data": {
    "studentId": "stu_789xyz",
    "photoUrl": "https://cdn.campus-security.example.com/photos/stu_789xyz_20260103100000.jpg"
  }
}
```

---

## ❌ Error Responses

### 401 - Not Authenticated
```javascript
{
  "detail": "Invalid or expired authentication token"
}
```

### 404 - Student Not Found
```javascript
{
  "detail": {
    "status": "error",
    "code": "STUDENT_NOT_FOUND",
    "message": "Student with ID 'stu_invalid' not found"
  }
}
```

### 400 - Invalid Image Format
```javascript
{
  "detail": "Invalid base64 image format: <error>"
}
```

---

## 💻 React/TypeScript Example

```typescript
import { useState } from 'react';

interface EnrollPhotoRequest {
  studentId: string;
  photo: string;
}

interface EnrollPhotoResponse {
  status: string;
  data: {
    studentId: string;
    photoUrl: string;
  };
}

function StudentPhotoUpload({ studentId }: { studentId: string }) {
  const [uploading, setUploading] = useState(false);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.match(/image\/(jpeg|jpg|png|gif)/)) {
      setError('Please select a valid image file (JPEG, PNG, or GIF)');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Image size must be less than 5MB');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      // Convert file to base64
      const base64Photo = await fileToBase64(file);

      // Upload to API
      const token = localStorage.getItem('authToken');
      const response = await fetch('http://localhost:8000/api/v1/students/enroll-photo', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          studentId,
          photo: base64Photo,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || 'Failed to upload photo');
      }

      const data: EnrollPhotoResponse = await response.json();
      setPhotoUrl(data.data.photoUrl);
      alert('Photo enrolled successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setUploading(false);
    }
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file);
    });
  };

  return (
    <div className="student-photo-upload">
      <h3>Enroll Student Photo</h3>
      
      <input
        type="file"
        accept="image/jpeg,image/jpg,image/png,image/gif"
        onChange={handleFileSelect}
        disabled={uploading}
      />

      {uploading && <p>Uploading photo...</p>}
      
      {error && <p className="error">{error}</p>}
      
      {photoUrl && (
        <div className="success">
          <p>✓ Photo enrolled successfully!</p>
          <img src={photoUrl} alt="Enrolled photo" width="200" />
        </div>
      )}
    </div>
  );
}

export default StudentPhotoUpload;
```

---

## 🎨 Vue 3 Example

```vue
<template>
  <div class="student-photo-upload">
    <h3>Enroll Student Photo</h3>
    
    <input
      type="file"
      accept="image/jpeg,image/jpg,image/png,image/gif"
      @change="handleFileSelect"
      :disabled="uploading"
    />

    <p v-if="uploading">Uploading photo...</p>
    <p v-if="error" class="error">{{ error }}</p>
    
    <div v-if="photoUrl" class="success">
      <p>✓ Photo enrolled successfully!</p>
      <img :src="photoUrl" alt="Enrolled photo" width="200" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  studentId: string;
}

const props = defineProps<Props>();

const uploading = ref(false);
const photoUrl = ref<string | null>(null);
const error = ref<string | null>(null);

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  // Validate
  if (!file.type.match(/image\/(jpeg|jpg|png|gif)/)) {
    error.value = 'Please select a valid image file';
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    error.value = 'Image size must be less than 5MB';
    return;
  }

  uploading.value = true;
  error.value = null;

  try {
    const base64Photo = await fileToBase64(file);
    
    const token = localStorage.getItem('authToken');
    const response = await fetch('http://localhost:8000/api/v1/students/enroll-photo', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        studentId: props.studentId,
        photo: base64Photo,
      }),
    });

    if (!response.ok) throw new Error('Failed to upload photo');

    const data = await response.json();
    photoUrl.value = data.data.photoUrl;
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error';
  } finally {
    uploading.value = false;
  }
};

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};
</script>

<style scoped>
.error {
  color: red;
}
.success {
  color: green;
}
</style>
```

---

## 📱 React Native Example

```typescript
import React, { useState } from 'react';
import { View, Button, Image, Text, StyleSheet } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import * as FileSystem from 'expo-file-system';

interface Props {
  studentId: string;
  authToken: string;
}

export default function StudentPhotoUpload({ studentId, authToken }: Props) {
  const [uploading, setUploading] = useState(false);
  const [photoUrl, setPhotoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      await uploadPhoto(result.assets[0].uri);
    }
  };

  const uploadPhoto = async (uri: string) => {
    setUploading(true);
    setError(null);

    try {
      // Convert to base64
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });

      const photoData = `data:image/jpeg;base64,${base64}`;

      // Upload to API
      const response = await fetch('http://localhost:8000/api/v1/students/enroll-photo', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          studentId,
          photo: photoData,
        }),
      });

      if (!response.ok) throw new Error('Upload failed');

      const data = await response.json();
      setPhotoUrl(data.data.photoUrl);
      alert('Photo enrolled successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Button
        title={uploading ? 'Uploading...' : 'Select Photo'}
        onPress={pickImage}
        disabled={uploading}
      />
      
      {error && <Text style={styles.error}>{error}</Text>}
      
      {photoUrl && (
        <View>
          <Text style={styles.success}>✓ Photo enrolled successfully!</Text>
          <Image source={{ uri: photoUrl }} style={styles.image} />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
  },
  error: {
    color: 'red',
    marginTop: 10,
  },
  success: {
    color: 'green',
    marginTop: 10,
  },
  image: {
    width: 200,
    height: 200,
    marginTop: 10,
  },
});
```

---

## 🛠️ Testing with Browser DevTools

```javascript
// Open browser console and run:

// 1. Get auth token (replace with your credentials)
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    employeeId: 'EMP-2024-003',
    password: 'password123'
  })
});
const loginData = await loginResponse.json();
const token = loginData.data.token;
console.log('Token:', token);

// 2. Create a test image (1x1 red pixel)
const testPhoto = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/wA/d';

// 3. Enroll the photo
const enrollResponse = await fetch('http://localhost:8000/api/v1/students/enroll-photo', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    studentId: 'stu_789xyz',
    photo: testPhoto
  })
});

const enrollData = await enrollResponse.json();
console.log('Enrollment result:', enrollData);
```

---

## 📋 Checklist for Frontend Integration

- [ ] Add file input for photo selection
- [ ] Validate image file type (JPEG, PNG, GIF)
- [ ] Validate file size (recommend max 5MB)
- [ ] Convert file to base64 with data URI prefix
- [ ] Get auth token from login flow
- [ ] Send POST request with Authorization header
- [ ] Handle loading state during upload
- [ ] Display success message with photo URL
- [ ] Handle error cases (401, 404, 400)
- [ ] Show enrolled photo to confirm upload
- [ ] Add option to re-upload/update photo

---

## 🎯 Best Practices

### 1. Image Quality
- Use clear, frontal face photos
- Good lighting conditions
- No accessories covering face (sunglasses, mask)
- Neutral expression recommended

### 2. Performance
- Resize images before upload (recommend 512x512 or 1024x1024)
- Compress to reduce payload size
- Show upload progress indicator

### 3. User Experience
- Preview image before upload
- Allow crop/rotate functionality
- Confirm before overwriting existing photo
- Show thumbnail of enrolled photo

### 4. Error Handling
- Retry logic for network failures
- Clear error messages for users
- Log errors for debugging
- Fallback UI for failed uploads

---

## 📞 Support

For issues or questions:
- Backend documentation: `STUDENT_PHOTO_ENROLLMENT.md`
- API contract: `api_contract.md`
- System diagram: `STUDENT_ENROLLMENT_DIAGRAM.md`

---

**Last Updated:** 2026-01-03  
**API Version:** 1.1.0
