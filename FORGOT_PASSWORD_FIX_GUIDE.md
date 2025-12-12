# Flutter Forgot Password Flow - Fixed Implementation Guide

## Issue & Solution

### Problem
When a user clicked "Forgot Password" in the Flutter app, they received an email with a reset link like:
```
https://fammo.ai/reset-password/MQ/d0n3rz-f64b0ee4712b9d209c6dcec28a03ffbc/
```

But clicking the link showed "Not Found" error because the web page didn't exist.

### Root Cause
The API was generating a link to `/reset-password/{uid}/{token}/` but Django didn't have a web view for that route.

### Solution ✅
Created a new web page that handles the password reset form:
- **URL**: `https://fammo.ai/reset-password/<uid>/<token>/`
- **Handler**: `reset_password_from_email()` view in `userapp/views.py`
- **Template**: `password_reset_from_email.html`
- **Flow**: User clicks link → Sees password form → Enters new password → Resets it

---

## Complete Forgot Password Workflow

### Step 1: User Clicks "Forgot Password" in Flutter App

**Endpoint**: `POST /api/v1/auth/forgot-password/`

```dart
// Flutter code
final response = await http.post(
  Uri.parse('${apiBaseUrl}auth/forgot-password/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'email': 'user@example.com',
  }),
);

if (response.statusCode == 200) {
  showSnackBar('Check your email for password reset link');
  Navigator.of(context).pop(); // Close forgot password screen
}
```

### Step 2: User Receives Email

Django sends email with link:
```
Subject: Password Reset Request

Click the link below to reset your password:
https://fammo.ai/reset-password/MQ/d0n3rz-f64b0ee4712b9d209c6dcec28a03ffbc/

If you didn't request this, please ignore this email.
```

### Step 3: User Clicks Link (from email on mobile)

Link opens in device browser → Shows password reset page:
```
┌─────────────────────────────────────────┐
│ 🔐 Reset Your Password                  │
│ Account: user@example.com               │
├─────────────────────────────────────────┤
│ New Password                            │
│ [________________]  (min. 8 chars)      │
│                                         │
│ Confirm Password                        │
│ [________________]                      │
│                                         │
│ [Reset Password] Button                 │
└─────────────────────────────────────────┘
```

### Step 4: User Enters New Password

- Validates password (min 8 characters)
- Confirms both passwords match
- Submits form

### Step 5: Password Reset Succeeds

User sees success message:
```
✅ Your password has been reset successfully! 
   You can now log in with your new password.
```

Automatically redirected to login page (3 seconds)

### Step 6: User Logs In with New Password

**Endpoint**: `POST /api/v1/auth/token/`

```dart
// Flutter code
final response = await http.post(
  Uri.parse('${apiBaseUrl}auth/token/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'email': 'user@example.com',
    'password': 'NewPassword456', // New password set via email link
  }),
);

if (response.statusCode == 200) {
  final data = jsonDecode(response.body);
  final accessToken = data['access'];
  // Save token and navigate to home
}
```

---

## Implementation Details

### Backend Changes

1. **View**: `userapp/views.py` - Added `reset_password_from_email()` function
   - Validates token
   - Shows password form
   - Handles form submission
   - Resets password on success

2. **URL**: `userapp/urls.py` - Added route
   ```python
   path('reset-password/<uidb64>/<token>/', views.reset_password_from_email, name='reset_password_from_email'),
   ```

3. **URL**: `famo/urls.py` - Added root-level route
   ```python
   path('reset-password/<uidb64>/<token>/', reset_password_from_email, name='api_reset_password_from_email'),
   ```

4. **Templates**: Created two new templates
   - `password_reset_from_email.html` - Password reset form
   - `password_reset_error.html` - Error page for invalid/expired tokens

### API Endpoint (No Changes Needed)

`ForgotPasswordView` in `api/views.py` already works correctly:
- Generates valid token using `default_token_generator`
- Encodes user ID in base64 format
- Sends email with proper link

---

## Testing Flow in Postman & Flutter

### Test 1: Complete Forgot Password Flow

```
1. POST /api/v1/auth/forgot-password/
   Body: {"email": "testuser@example.com"}
   
2. Check console/email for link with uid and token
   Example: https://fammo.ai/reset-password/MQ/abc123def456.../
   
3. Open link in browser
   → Shows password reset form
   
4. Enter new password, confirm it
   → Click "Reset Password"
   
5. Success message appears
   → Redirected to login
   
6. POST /api/v1/auth/token/
   Body: {"email": "testuser@example.com", "password": "NewPassword"}
   → Get new access token
   
7. SUCCESS ✅
```

### Test 2: Invalid Token

```
1. Open link with invalid token:
   https://fammo.ai/reset-password/INVALID/INVALID/
   
2. Error page appears:
   "This password reset link is invalid or has expired"
   
3. Options: "Go to Login" or "Request New Reset Link"
```

### Test 3: Expired Token (24 hours later)

```
1. Email link generated at 2:00 PM Monday
2. User tries to use it Tuesday at 2:01 PM
3. Token validation fails
4. Error page displayed
5. User must request new password reset
```

---

## Email Configuration

### Console Output (Development)

During development, Django prints emails to console:
```
[Console Output]
Subject: Password Reset Request
From: no-reply@fammo.local
To: testuser@example.com

Content:
Click the link below to reset your password:
https://localhost:8000/reset-password/MQ/abc123.../

Copy uid "MQ" and token "abc123..." for testing.
```

### Production Email

In production, actual email is sent to user's mailbox with professional template.

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Not Found" error | URL doesn't exist | ✅ Fixed - added view and route |
| Password form doesn't appear | View not configured | ✅ Fixed - added view in urls |
| Form submission fails | CSRF token missing | ✅ Template includes {% csrf_token %} |
| Token shows "invalid" | Expired (24hr limit) | Request new password reset |
| Email not received | SMTP not configured | Check Django email backend settings |
| Link redirect fails | URL pattern mismatch | ✅ Fixed - added root-level route |

---

## Flutter Implementation (Unchanged)

Your Flutter code remains the same - no changes needed!

```dart
// ForgotPasswordScreen.dart
class ForgotPasswordScreen extends StatefulWidget {
  @override
  _ForgotPasswordScreenState createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  bool _isLoading = false;

  void _sendResetEmail() async {
    if (_emailController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please enter your email')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('https://fammo.ai/api/v1/auth/forgot-password/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': _emailController.text}),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Check your email for password reset link'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Forgot Password')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _sendResetEmail,
              child: Text(_isLoading ? 'Sending...' : 'Send Reset Link'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## Summary

✅ **What's Fixed**:
1. Backend now has web view for `/reset-password/<uid>/<token>/` URL
2. Password reset page displays correctly when user clicks email link
3. User can enter new password and reset it
4. Success/error messages display appropriately
5. Proper token validation (24-hour expiry)

✅ **What Works**:
1. Email generation and sending
2. Token validation
3. Password hashing
4. Flutter app flow (no changes needed)
5. Complete forgot password workflow

✅ **User Experience**:
1. Click link in email → Password form appears
2. Enter new password → Reset successful
3. Login with new password → App access

No changes needed in Flutter! The backend is now complete.
