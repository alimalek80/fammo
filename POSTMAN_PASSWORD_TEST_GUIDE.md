# Postman Guide: Testing Password Management Endpoints

## Overview
This guide shows how to test all three password management API endpoints using Postman.

---

## Prerequisites

1. **Postman installed** - Download from https://www.postman.com/downloads/
2. **Your API running** - Make sure Django development server is running
   ```bash
   python manage.py runserver
   ```
3. **Base URL** - `http://localhost:8000/api/v1/`

---

## 1. Setup: Get JWT Access Token

### Step 1: Sign Up a Test User
**Endpoint:** `POST /auth/signup/`

```
POST http://localhost:8000/api/v1/auth/signup/
Content-Type: application/json

{
  "email": "testuser@example.com",
  "password": "TestPassword123",
  "password_confirm": "TestPassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful. Please check your email to activate your account.",
  "user": {
    "id": 1,
    "email": "testuser@example.com"
  }
}
```

### Step 2: Activate the User

In Django admin or database, set the user to `is_active = True`:
```bash
# Or use the admin panel at http://localhost:8000/admin/
```

### Step 3: Get JWT Token
**Endpoint:** `POST /auth/token/`

```
POST http://localhost:8000/api/v1/auth/token/
Content-Type: application/json

{
  "email": "testuser@example.com",
  "password": "TestPassword123"
}
```

**Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Save the `access` token - you'll need it for authenticated endpoints**

---

## 2. Test Change Password Endpoint

**Endpoint:** `POST /auth/change-password/`  
**Authentication:** Required (JWT Bearer Token)  
**Purpose:** Change password for authenticated user

### In Postman:

1. **Create a new request** → `POST`
2. **URL:** `http://localhost:8000/api/v1/auth/change-password/`
3. **Headers tab:**
   ```
   Authorization: Bearer {YOUR_ACCESS_TOKEN}
   Content-Type: application/json
   ```
4. **Body (raw JSON):**
   ```json
   {
     "old_password": "TestPassword123",
     "new_password": "NewPassword456",
     "new_password_confirm": "NewPassword456"
   }
   ```
5. **Click Send**

### Expected Responses:

**✅ Success (200 OK):**
```json
{
  "success": true,
  "message": "Password has been changed successfully"
}
```

**❌ Old password incorrect (400 Bad Request):**
```json
{
  "error": "Old password is incorrect"
}
```

**❌ New passwords don't match (400 Bad Request):**
```json
{
  "error": "New passwords do not match"
}
```

**❌ Password too short (400 Bad Request):**
```json
{
  "error": "Password must be at least 8 characters long"
}
```

**❌ Same as old password (400 Bad Request):**
```json
{
  "error": "New password must be different from old password"
}
```

**❌ No authorization (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 3. Test Forgot Password Endpoint

**Endpoint:** `POST /auth/forgot-password/`  
**Authentication:** Not Required (Public)  
**Purpose:** Request password reset email

### In Postman:

1. **Create a new request** → `POST`
2. **URL:** `http://localhost:8000/api/v1/auth/forgot-password/`
3. **Headers tab:**
   ```
   Content-Type: application/json
   ```
4. **Body (raw JSON):**
   ```json
   {
     "email": "testuser@example.com"
   }
   ```
5. **Click Send**

### Expected Response (Always 200 OK):

```json
{
  "success": true,
  "message": "If an account with this email exists, a password reset link has been sent."
}
```

**Note:** For security, the response is always positive regardless of whether the email exists.

### In Development - Check the Email

In development, Django's console email backend prints emails to console:

```
[Console Output]
Subject: Password Reset Request
From: no-reply@fammo.local
To: testuser@example.com

Message:
Click the link below to reset your password:

http://localhost:8000/reset-password/{uid}/{token}/

If you didn't request this, please ignore this email.
```

**Copy the `{uid}` and `{token}` values for the next step.**

---

## 4. Test Reset Password Endpoint

**Endpoint:** `POST /auth/reset-password/`  
**Authentication:** Not Required (Public)  
**Purpose:** Reset password using email token

### Step 1: Get Reset Link from Email (Forgot Password)
(See section 3 above - copy the `uid` and `token`)

### Step 2: Reset the Password

In Postman:

1. **Create a new request** → `POST`
2. **URL:** `http://localhost:8000/api/v1/auth/reset-password/`
3. **Headers tab:**
   ```
   Content-Type: application/json
   ```
4. **Body (raw JSON):**
   ```json
   {
     "uid": "MQ",
     "token": "a1b2c3d4e5f6g7h8...",
     "password": "FinalPassword789",
     "password_confirm": "FinalPassword789"
   }
   ```
5. **Click Send**

### Expected Responses:

**✅ Success (200 OK):**
```json
{
  "success": true,
  "message": "Password has been reset successfully"
}
```

**❌ Invalid token (400 Bad Request):**
```json
{
  "error": "Invalid or expired token"
}
```

**❌ Passwords don't match (400 Bad Request):**
```json
{
  "error": "New passwords do not match"
}
```

**❌ Password too short (400 Bad Request):**
```json
{
  "error": "Password must be at least 8 characters long"
}
```

---

## 5. Test Complete Workflow

### Test Scenario 1: Change Password (Authenticated User)

```
1. Sign up new user
   POST /auth/signup/
   
2. Activate user (manually in admin)

3. Get JWT token
   POST /auth/token/
   
4. Change password
   POST /auth/change-password/
   (requires Bearer token)
   
5. Try logging in with old password → FAILS
6. Try logging in with new password → SUCCESS
```

### Test Scenario 2: Forgot & Reset Password (Anonymous)

```
1. Request password reset
   POST /auth/forgot-password/
   
2. Copy uid & token from console email
   
3. Reset password
   POST /auth/reset-password/
   (using uid & token)
   
4. Try logging in with old password → FAILS
5. Try logging in with new password → SUCCESS
```

### Test Scenario 3: Invalid Cases

**Test invalid old password:**
```json
POST /auth/change-password/
{
  "old_password": "WrongPassword",
  "new_password": "NewPassword456",
  "new_password_confirm": "NewPassword456"
}
→ Expected: 400 "Old password is incorrect"
```

**Test password mismatch:**
```json
POST /auth/change-password/
{
  "old_password": "TestPassword123",
  "new_password": "NewPassword456",
  "new_password_confirm": "DifferentPassword"
}
→ Expected: 400 "New passwords do not match"
```

**Test short password:**
```json
POST /auth/change-password/
{
  "old_password": "TestPassword123",
  "new_password": "Short1",
  "new_password_confirm": "Short1"
}
→ Expected: 400 "Password must be at least 8 characters long"
```

**Test same password:**
```json
POST /auth/change-password/
{
  "old_password": "TestPassword123",
  "new_password": "TestPassword123",
  "new_password_confirm": "TestPassword123"
}
→ Expected: 400 "New password must be different from old password"
```

**Test without authorization:**
```
POST /auth/change-password/
(without Bearer token in headers)
→ Expected: 401 "Authentication credentials were not provided."
```

---

## Postman Collection JSON

Save this as `FAMMO_Password_API.postman_collection.json` and import into Postman:

```json
{
  "info": {
    "name": "FAMMO Password Management API",
    "description": "Collection for testing password endpoints",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth Setup",
      "item": [
        {
          "name": "1. Sign Up",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"testuser@example.com\",\n  \"password\": \"TestPassword123\",\n  \"password_confirm\": \"TestPassword123\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/v1/auth/signup/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "v1", "auth", "signup"]
            }
          }
        },
        {
          "name": "2. Get JWT Token",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"testuser@example.com\",\n  \"password\": \"TestPassword123\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/v1/auth/token/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "v1", "auth", "token"]
            }
          }
        }
      ]
    },
    {
      "name": "Password Management",
      "item": [
        {
          "name": "Change Password",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer YOUR_ACCESS_TOKEN_HERE"
              },
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"old_password\": \"TestPassword123\",\n  \"new_password\": \"NewPassword456\",\n  \"new_password_confirm\": \"NewPassword456\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/v1/auth/change-password/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "v1", "auth", "change-password"]
            }
          }
        },
        {
          "name": "Forgot Password",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"testuser@example.com\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/v1/auth/forgot-password/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "v1", "auth", "forgot-password"]
            }
          }
        },
        {
          "name": "Reset Password",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"uid\": \"MQ\",\n  \"token\": \"a1b2c3d4e5f6g7h8-your-token-here\",\n  \"password\": \"FinalPassword789\",\n  \"password_confirm\": \"FinalPassword789\"\n}"
            },
            "url": {
              "raw": "http://localhost:8000/api/v1/auth/reset-password/",
              "protocol": "http",
              "host": ["localhost"],
              "port": "8000",
              "path": ["api", "v1", "auth", "reset-password"]
            }
          }
        }
      ]
    }
  ]
}
```

---

## Quick Reference: All Password Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/auth/signup/` | POST | ❌ No | Register new user |
| `/auth/token/` | POST | ❌ No | Get JWT access token |
| `/auth/change-password/` | POST | ✅ Yes | Change password (logged in) |
| `/auth/forgot-password/` | POST | ❌ No | Request password reset email |
| `/auth/reset-password/` | POST | ❌ No | Reset password with token |
| `/auth/resend-activation/` | POST | ❌ No | Resend activation email |

---

## Tips for Postman

### 1. **Store Variables for Reuse**

Click **Environment** → Create new environment → Add variables:

```
Variable Name: base_url
Initial Value: http://localhost:8000/api/v1

Variable Name: access_token
Initial Value: (leave blank, will populate after login)

Variable Name: test_email
Initial Value: testuser@example.com
```

Then in requests, use: `{{base_url}}/auth/change-password/`

### 2. **Automatically Capture Access Token**

After Get JWT Token request, click **Tests** tab and add:

```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access);
}
```

Then use `Bearer {{access_token}}` in Authorization headers.

### 3. **Create Test Scripts**

Click **Tests** tab in any request:

```javascript
// Test successful response
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Test response structure
pm.test("Response has success field", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property("success");
});

// Test error message
pm.test("Error message is correct", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.error).to.include("Old password");
});
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Make sure Bearer token is in Authorization header |
| 400 Bad Request | Check JSON syntax and field names match exactly |
| 404 Not Found | Verify URL path is correct (check for typos) |
| CSRF error | Add `X-CSRFToken` header (not needed for API endpoints) |
| Email not sent | Check Django's console output (dev mode prints emails) |
| Token expired | Generate a new token using `/auth/token/` |

---

## Next Steps

1. **Test in Postman** using the endpoints above
2. **Integrate into Flutter** app using the `FLUTTER_PASSWORD_MANAGEMENT_GUIDE.md`
3. **Add test scripts** to validate responses automatically
4. **Export collection** and share with team
