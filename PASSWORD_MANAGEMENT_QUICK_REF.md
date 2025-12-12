# 🔐 Password Management - Quick Reference

## Three Password Endpoints

### 1. Change Password (Authenticated User)
**User is logged in and wants to change their password**

```
POST /api/v1/auth/change-password/
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json

{
  "old_password": "CurrentPassword123",
  "new_password": "NewPassword456",
  "new_password_confirm": "NewPassword456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password has been changed successfully"
}
```

---

### 2. Forgot Password (Anonymous User)
**User forgot password and needs to reset it**

```
POST /api/v1/auth/forgot-password/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "If an account with this email exists, a password reset link has been sent."
}
```

**Email Received:**
```
Subject: Password Reset Request

Click to reset password:
https://fammo.ai/reset-password/MQ/d0n3rz-f64b0ee4712b9d209c6dcec28a03ffbc/
```

---

### 3. Reset Password (Via Email Link)
**User clicks link from email and sets new password**

#### Option A: Web Page (Browser)
Click link from email → Password form appears → Enter password → Reset

#### Option B: API Call (Mobile)
```
POST /api/v1/auth/reset-password/
Content-Type: application/json

{
  "uid": "MQ",
  "token": "d0n3rz-f64b0ee4712b9d209c6dcec28a03ffbc",
  "password": "NewPassword456",
  "password_confirm": "NewPassword456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password has been reset successfully"
}
```

---

## Decision Tree: Which Endpoint to Use?

```
┌─ Is user logged in?
│
├─ YES → Change Password (/auth/change-password/)
│        Requires: old_password, new_password
│
└─ NO → Did they get an email link?
   │
   ├─ YES → Reset Password (/auth/reset-password/ or web page)
   │        Requires: uid, token, new_password
   │
   └─ NO → Forgot Password (/auth/forgot-password/)
            Requires: email only
            → User gets email with link
```

---

## Flutter Implementation Checklist

### Forgot Password Screen
- [ ] Email input field
- [ ] "Send Reset Link" button
- [ ] Error handling
- [ ] Success message ("Check your email...")

```dart
final response = await http.post(
  Uri.parse('${apiBaseUrl}auth/forgot-password/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'email': email}),
);
```

### Change Password Screen
- [ ] Old password input
- [ ] New password input
- [ ] Confirm password input
- [ ] Validation (min 8 chars)
- [ ] "Change Password" button
- [ ] JWT token in Authorization header

```dart
final response = await http.post(
  Uri.parse('${apiBaseUrl}auth/change-password/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'old_password': oldPassword,
    'new_password': newPassword,
    'new_password_confirm': newPassword,
  }),
);
```

### Reset Password (Mobile)
If handling reset via API instead of web link:

```dart
final response = await http.post(
  Uri.parse('${apiBaseUrl}auth/reset-password/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'uid': uid,  // From email link
    'token': token,  // From email link
    'password': newPassword,
    'password_confirm': newPassword,
  }),
);
```

---

## Testing Commands

### Test 1: Forgot Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com"}'
```

### Test 2: Change Password (need token)
```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password":"OldPass123",
    "new_password":"NewPass456",
    "new_password_confirm":"NewPass456"
  }'
```

### Test 3: Reset Password via API
```bash
curl -X POST http://localhost:8000/api/v1/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid":"MQ",
    "token":"abc123...",
    "password":"NewPass456",
    "password_confirm":"NewPass456"
  }'
```

---

## Error Responses

### 400 Bad Request - Old password incorrect
```json
{"error": "Old password is incorrect"}
```

### 400 Bad Request - Passwords don't match
```json
{"error": "New passwords do not match"}
```

### 400 Bad Request - Password too short
```json
{"error": "Password must be at least 8 characters long"}
```

### 400 Bad Request - Same as old password
```json
{"error": "New password must be different from old password"}
```

### 400 Bad Request - Invalid token
```json
{"error": "Invalid or expired token"}
```

### 401 Unauthorized - No token provided
```json
{"detail": "Authentication credentials were not provided."}
```

---

## URLs Summary

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/auth/signup/` | POST | ❌ | Register new user |
| `/auth/token/` | POST | ❌ | Get JWT token (login) |
| `/auth/token/refresh/` | POST | ❌ | Refresh expired token |
| `/auth/change-password/` | POST | ✅ | Change password (logged in) |
| `/auth/forgot-password/` | POST | ❌ | Request reset email |
| `/auth/reset-password/` | POST | ❌ | Reset with token |
| `/reset-password/<uid>/<token>/` | GET/POST | ❌ | Web page for password reset |

---

## Postman Collection

Save as `fammo-password-endpoints.postman_collection.json`:

```json
{
  "info": {"name": "FAMMO Password Management"},
  "item": [
    {
      "name": "Forgot Password",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {"mode": "raw", "raw": "{\"email\":\"user@example.com\"}"},
        "url": {"raw": "http://localhost:8000/api/v1/auth/forgot-password/"}
      }
    },
    {
      "name": "Change Password",
      "request": {
        "method": "POST",
        "header": [
          {"key": "Authorization", "value": "Bearer YOUR_TOKEN"},
          {"key": "Content-Type", "value": "application/json"}
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"old_password\":\"Old123\",\"new_password\":\"New456\",\"new_password_confirm\":\"New456\"}"
        },
        "url": {"raw": "http://localhost:8000/api/v1/auth/change-password/"}
      }
    },
    {
      "name": "Reset Password",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"uid\":\"MQ\",\"token\":\"abc123\",\"password\":\"NewPass\",\"password_confirm\":\"NewPass\"}"
        },
        "url": {"raw": "http://localhost:8000/api/v1/auth/reset-password/"}
      }
    }
  ]
}
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Missing auth token | Add `Authorization: Bearer <token>` header |
| 400 Passwords don't match | Typo or copy issue | Double-check both password fields |
| Email not received | SMTP not configured | Check Django email settings |
| Link "Not Found" in browser | Wrong URL in email | ✅ FIXED - added web view |
| Token invalid error | Expired (24hr) | Request new reset link |
| 404 on /auth/change-password/ | Endpoint not imported | ✅ FIXED - added to urls |

---

## Production Checklist

Before deploying to production:

- [ ] Configure SMTP email settings
- [ ] Test with real email address
- [ ] Update email templates with correct domain
- [ ] Set up SSL/HTTPS (required for production)
- [ ] Configure CSRF settings for your domain
- [ ] Test complete forgot password flow
- [ ] Test token expiration (24 hours)
- [ ] Set up email backup/retry logic
- [ ] Monitor for failed password resets
- [ ] Implement rate limiting on password endpoints

---

## Support

For issues or questions:
1. Check error messages - they're descriptive
2. Review the detailed guides in docs folder
3. Test in Postman before Flutter
4. Check Django logs for backend errors
5. Verify email configuration

🎉 All set! Password management is complete!
