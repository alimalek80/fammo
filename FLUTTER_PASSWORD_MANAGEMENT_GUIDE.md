# Flutter Password Management Guide

## Overview
This guide provides complete implementation for password management features in Flutter, including:
- Change password (for authenticated users)
- Forgot password (sends reset email)
- Reset password (via email link)

---

## 1. API Endpoints

### Change Password (Authenticated User)
```
POST /api/v1/auth/change-password/
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Body:
{
  "old_password": "current_password_here",
  "new_password": "new_secure_password",
  "new_password_confirm": "new_secure_password"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password has been changed successfully"
}
```

**Error Responses:**
```json
{
  "error": "Old password is incorrect"
}
```
```json
{
  "error": "New password must be different from old password"
}
```
```json
{
  "error": "New passwords do not match"
}
```
```json
{
  "error": "Password must be at least 8 characters long"
}
```

---

### Forgot Password (Request Reset Email)
```
POST /api/v1/auth/forgot-password/
Headers:
  Content-Type: application/json

Body:
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "If an account with this email exists, a password reset link has been sent."
}
```

**Note:** Same response regardless of whether email exists (for security)

---

### Reset Password (Using Email Token)
```
POST /api/v1/auth/reset-password/
Headers:
  Content-Type: application/json

Body:
{
  "uid": "base64_encoded_user_id",
  "token": "reset_token_from_email",
  "password": "new_password",
  "password_confirm": "new_password"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Password has been reset successfully"
}
```

---

## 2. Validation Requirements

### Password Requirements
- Minimum 8 characters
- Must not match old password
- Must be confirmed (match twice)
- Cannot be blank

### Email Validation
- Must be valid email format
- Must exist in database (for forgot password)

---

## 3. Flutter Implementation

### Step 1: Create Models

```dart
// models/password.dart

class ChangePasswordRequest {
  final String oldPassword;
  final String newPassword;
  final String newPasswordConfirm;

  ChangePasswordRequest({
    required this.oldPassword,
    required this.newPassword,
    required this.newPasswordConfirm,
  });

  Map<String, dynamic> toJson() {
    return {
      'old_password': oldPassword,
      'new_password': newPassword,
      'new_password_confirm': newPasswordConfirm,
    };
  }
}

class ForgotPasswordRequest {
  final String email;

  ForgotPasswordRequest({required this.email});

  Map<String, dynamic> toJson() {
    return {'email': email};
  }
}

class ResetPasswordRequest {
  final String uid;
  final String token;
  final String password;
  final String passwordConfirm;

  ResetPasswordRequest({
    required this.uid,
    required this.token,
    required this.password,
    required this.passwordConfirm,
  });

  Map<String, dynamic> toJson() {
    return {
      'uid': uid,
      'token': token,
      'password': password,
      'password_confirm': passwordConfirm,
    };
  }
}

class PasswordResponse {
  final bool success;
  final String message;
  final String? error;

  PasswordResponse({
    required this.success,
    required this.message,
    this.error,
  });

  factory PasswordResponse.fromJson(Map<String, dynamic> json) {
    return PasswordResponse(
      success: json['success'] ?? false,
      message: json['message'] ?? json['error'] ?? 'Unknown error',
      error: json['error'],
    );
  }
}
```

---

### Step 2: Create API Service Methods

Add these methods to your existing `ApiService` class:

```dart
// services/api_service.dart

class ApiService {
  static const String baseUrl = 'https://your-domain.com/api/v1';
  static const storage = FlutterSecureStorage();

  // Change password for authenticated user
  static Future<PasswordResponse> changePassword({
    required String oldPassword,
    required String newPassword,
    required String newPasswordConfirm,
  }) async {
    try {
      final token = await storage.read(key: 'access_token');
      
      if (token == null) {
        return PasswordResponse(
          success: false,
          message: 'Not authenticated',
          error: 'access_token_missing',
        );
      }

      final request = ChangePasswordRequest(
        oldPassword: oldPassword,
        newPassword: newPassword,
        newPasswordConfirm: newPasswordConfirm,
      );

      final response = await http.post(
        Uri.parse('$baseUrl/auth/change-password/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return PasswordResponse.fromJson(jsonDecode(response.body));
      } else if (response.statusCode == 400) {
        final errorData = jsonDecode(response.body);
        return PasswordResponse(
          success: false,
          message: errorData['error'] ?? 'Invalid password',
          error: errorData['error'],
        );
      } else {
        return PasswordResponse(
          success: false,
          message: 'Failed to change password: ${response.statusCode}',
          error: 'http_error',
        );
      }
    } catch (e) {
      return PasswordResponse(
        success: false,
        message: 'Error: $e',
        error: 'network_error',
      );
    }
  }

  // Request password reset email
  static Future<PasswordResponse> forgotPassword({
    required String email,
  }) async {
    try {
      final request = ForgotPasswordRequest(email: email);

      final response = await http.post(
        Uri.parse('$baseUrl/auth/forgot-password/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return PasswordResponse.fromJson(jsonDecode(response.body));
      } else {
        return PasswordResponse(
          success: false,
          message: 'Failed to send reset email: ${response.statusCode}',
          error: 'http_error',
        );
      }
    } catch (e) {
      return PasswordResponse(
        success: false,
        message: 'Error: $e',
        error: 'network_error',
      );
    }
  }

  // Reset password using token from email
  static Future<PasswordResponse> resetPassword({
    required String uid,
    required String token,
    required String password,
    required String passwordConfirm,
  }) async {
    try {
      final request = ResetPasswordRequest(
        uid: uid,
        token: token,
        password: password,
        passwordConfirm: passwordConfirm,
      );

      final response = await http.post(
        Uri.parse('$baseUrl/auth/reset-password/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return PasswordResponse.fromJson(jsonDecode(response.body));
      } else if (response.statusCode == 400) {
        final errorData = jsonDecode(response.body);
        return PasswordResponse(
          success: false,
          message: errorData['error'] ?? 'Invalid or expired token',
          error: errorData['error'],
        );
      } else {
        return PasswordResponse(
          success: false,
          message: 'Failed to reset password: ${response.statusCode}',
          error: 'http_error',
        );
      }
    } catch (e) {
      return PasswordResponse(
        success: false,
        message: 'Error: $e',
        error: 'network_error',
      );
    }
  }
}
```

---

### Step 3: Create UI Screens

#### Change Password Screen

```dart
// screens/auth/change_password_screen.dart

import 'package:flutter/material.dart';
import '../../models/password.dart';
import '../../services/api_service.dart';

class ChangePasswordScreen extends StatefulWidget {
  @override
  State<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  final _oldPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  
  bool _isLoading = false;
  bool _oldPasswordVisible = false;
  bool _newPasswordVisible = false;
  bool _confirmPasswordVisible = false;

  @override
  void dispose() {
    _oldPasswordController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }
    if (value.length < 8) {
      return 'Password must be at least 8 characters';
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please confirm your password';
    }
    if (value != _newPasswordController.text) {
      return 'Passwords do not match';
    }
    return null;
  }

  Future<void> _changePassword() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final response = await ApiService.changePassword(
        oldPassword: _oldPasswordController.text,
        newPassword: _newPasswordController.text,
        newPasswordConfirm: _confirmPasswordController.text,
      );

      if (response.success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response.message),
            backgroundColor: Colors.green,
          ),
        );
        
        // Clear form
        _oldPasswordController.clear();
        _newPasswordController.clear();
        _confirmPasswordController.clear();
        
        // Navigate back after 1 second
        await Future.delayed(Duration(seconds: 1));
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response.message),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Change Password'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Info message
              Container(
                padding: EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue[200]!),
                ),
                child: Text(
                  'Enter your current password and choose a new one',
                  style: TextStyle(
                    color: Colors.blue[900],
                    fontSize: 14,
                  ),
                ),
              ),
              SizedBox(height: 24),

              // Old Password Field
              Text(
                'Current Password',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _oldPasswordController,
                obscureText: !_oldPasswordVisible,
                decoration: InputDecoration(
                  labelText: 'Enter current password',
                  border: OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _oldPasswordVisible ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() => _oldPasswordVisible = !_oldPasswordVisible);
                    },
                  ),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Current password is required';
                  }
                  return null;
                },
              ),
              SizedBox(height: 20),

              // New Password Field
              Text(
                'New Password',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _newPasswordController,
                obscureText: !_newPasswordVisible,
                decoration: InputDecoration(
                  labelText: 'Enter new password (min 8 characters)',
                  border: OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _newPasswordVisible ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() => _newPasswordVisible = !_newPasswordVisible);
                    },
                  ),
                ),
                validator: _validatePassword,
              ),
              SizedBox(height: 20),

              // Confirm Password Field
              Text(
                'Confirm New Password',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _confirmPasswordController,
                obscureText: !_confirmPasswordVisible,
                decoration: InputDecoration(
                  labelText: 'Confirm new password',
                  border: OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _confirmPasswordVisible ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() => _confirmPasswordVisible = !_confirmPasswordVisible);
                    },
                  ),
                ),
                validator: _validateConfirmPassword,
              ),
              SizedBox(height: 32),

              // Submit Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _changePassword,
                  child: _isLoading
                      ? SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation(Colors.white),
                          ),
                        )
                      : Text('Change Password'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

---

#### Forgot Password Screen

```dart
// screens/auth/forgot_password_screen.dart

import 'package:flutter/material.dart';
import '../../models/password.dart';
import '../../services/api_service.dart';

class ForgotPasswordScreen extends StatefulWidget {
  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  
  bool _isLoading = false;
  bool _emailSent = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }
    final emailRegex = RegExp(r'^[^@]+@[^@]+\.[^@]+');
    if (!emailRegex.hasMatch(value)) {
      return 'Please enter a valid email';
    }
    return null;
  }

  Future<void> _sendResetEmail() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final response = await ApiService.forgotPassword(
        email: _emailController.text,
      );

      if (response.success) {
        setState(() => _emailSent = true);
        
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Password reset email sent. Check your inbox!'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Navigate back after 2 seconds
        await Future.delayed(Duration(seconds: 2));
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response.message),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Reset Password'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon
            Center(
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.lock_reset,
                  size: 40,
                  color: Colors.blue[600],
                ),
              ),
            ),
            SizedBox(height: 24),

            // Title
            Text(
              'Forgot your password?',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 8),

            // Subtitle
            Text(
              'No worries! Enter your email and we\'ll send you instructions to reset it.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            SizedBox(height: 32),

            // Email Form
            Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Email Address',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  SizedBox(height: 8),
                  TextFormField(
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: InputDecoration(
                      labelText: 'Enter your email',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.email_outlined),
                    ),
                    validator: _validateEmail,
                  ),
                ],
              ),
            ),
            SizedBox(height: 32),

            // Submit Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _sendResetEmail,
                child: _isLoading
                    ? SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation(Colors.white),
                        ),
                      )
                    : Text('Send Reset Link'),
              ),
            ),
            SizedBox(height: 16),

            // Back to Login
            Center(
              child: TextButton(
                onPressed: () => Navigator.pop(context),
                child: Text('Back to Login'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

#### Reset Password Screen (From Email Link)

```dart
// screens/auth/reset_password_screen.dart

import 'package:flutter/material.dart';
import '../../models/password.dart';
import '../../services/api_service.dart';

class ResetPasswordScreen extends StatefulWidget {
  final String uid;
  final String token;

  const ResetPasswordScreen({
    required this.uid,
    required this.token,
  });

  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  
  bool _isLoading = false;
  bool _passwordVisible = false;
  bool _confirmPasswordVisible = false;

  @override
  void dispose() {
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }
    if (value.length < 8) {
      return 'Password must be at least 8 characters';
    }
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please confirm your password';
    }
    if (value != _passwordController.text) {
      return 'Passwords do not match';
    }
    return null;
  }

  Future<void> _resetPassword() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final response = await ApiService.resetPassword(
        uid: widget.uid,
        token: widget.token,
        password: _passwordController.text,
        passwordConfirm: _confirmPasswordController.text,
      );

      if (response.success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Password reset successfully! Please log in.'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Navigate to login after 1 second
        await Future.delayed(Duration(seconds: 1));
        Navigator.of(context).pushNamedAndRemoveUntil(
          '/login',
          (route) => false,
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(response.message),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Reset Password'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Icon
              Center(
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Colors.green[50],
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    Icons.check_circle_outline,
                    size: 40,
                    color: Colors.green[600],
                  ),
                ),
              ),
              SizedBox(height: 24),

              // Title
              Text(
                'Create New Password',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 8),

              // Subtitle
              Text(
                'Please enter a new secure password',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
              SizedBox(height: 32),

              // Password Field
              Text(
                'New Password',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _passwordController,
                obscureText: !_passwordVisible,
                decoration: InputDecoration(
                  labelText: 'Enter new password (min 8 characters)',
                  border: OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _passwordVisible ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() => _passwordVisible = !_passwordVisible);
                    },
                  ),
                ),
                validator: _validatePassword,
              ),
              SizedBox(height: 20),

              // Confirm Password Field
              Text(
                'Confirm Password',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(height: 8),
              TextFormField(
                controller: _confirmPasswordController,
                obscureText: !_confirmPasswordVisible,
                decoration: InputDecoration(
                  labelText: 'Confirm new password',
                  border: OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _confirmPasswordVisible ? Icons.visibility : Icons.visibility_off,
                    ),
                    onPressed: () {
                      setState(() => _confirmPasswordVisible = !_confirmPasswordVisible);
                    },
                  ),
                ),
                validator: _validateConfirmPassword,
              ),
              SizedBox(height: 32),

              // Submit Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _resetPassword,
                  child: _isLoading
                      ? SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation(Colors.white),
                          ),
                        )
                      : Text('Reset Password'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

---

### Step 4: Navigation Integration

Add routes to your app:

```dart
// main.dart or routes.dart

class AppRoutes {
  static const changePassword = '/change-password';
  static const forgotPassword = '/forgot-password';
  static const resetPassword = '/reset-password';
  
  static Map<String, WidgetBuilder> getRoutes() {
    return {
      changePassword: (context) => ChangePasswordScreen(),
      forgotPassword: (context) => ForgotPasswordScreen(),
      resetPassword: (context) {
        // Extract uid and token from deep link
        final uri = Uri.base;
        final uid = uri.queryParameters['uid'] ?? '';
        final token = uri.queryParameters['token'] ?? '';
        
        return ResetPasswordScreen(uid: uid, token: token);
      },
    };
  }
}
```

---

### Step 5: Add to Settings Screen

```dart
// Example: Add change password to settings

ListTile(
  title: Text('Change Password'),
  subtitle: Text('Update your password'),
  trailing: Icon(Icons.arrow_forward),
  onTap: () => Navigator.pushNamed(
    context,
    AppRoutes.changePassword,
  ),
),
ListTile(
  title: Text('Forgot Password'),
  subtitle: Text('Reset password via email'),
  trailing: Icon(Icons.arrow_forward),
  onTap: () => Navigator.pushNamed(
    context,
    AppRoutes.forgotPassword,
  ),
),
```

---

## 4. Error Handling

The API provides specific error messages for different scenarios:

| Error | Cause | Solution |
|-------|-------|----------|
| `Old password is incorrect` | User entered wrong current password | Ask user to verify old password |
| `New passwords do not match` | Confirmation doesn't match | Ensure both passwords are identical |
| `Password must be at least 8 characters` | Password too short | Require minimum 8 characters |
| `New password must be different from old` | Same as current | Ask for new, different password |
| `Invalid or expired token` | Reset token expired | Request new reset email |

---

## 5. Security Best Practices

1. ✅ **Always use HTTPS** - Never send passwords over HTTP
2. ✅ **Store tokens securely** - Use `flutter_secure_storage`
3. ✅ **Validate passwords** - Check length and format
4. ✅ **Hide passwords** - Toggle visibility as shown
5. ✅ **Clear sensitive data** - Clear controllers after use
6. ✅ **Add rate limiting** - Limit password reset attempts
7. ✅ **Use HTTPS certificates** - Enable certificate pinning in production

---

## 6. Testing

Test these scenarios:

```dart
// Test change password
Future<void> testChangePassword() async {
  final response = await ApiService.changePassword(
    oldPassword: 'current_pass',
    newPassword: 'new_secure_password_123',
    newPasswordConfirm: 'new_secure_password_123',
  );
  print('Success: ${response.success}');
  print('Message: ${response.message}');
}

// Test forgot password
Future<void> testForgotPassword() async {
  final response = await ApiService.forgotPassword(
    email: 'user@example.com',
  );
  print('Email sent: ${response.success}');
}

// Test reset password
Future<void> testResetPassword() async {
  final response = await ApiService.resetPassword(
    uid: 'base64_uid',
    token: 'reset_token',
    password: 'new_password_123',
    passwordConfirm: 'new_password_123',
  );
  print('Password reset: ${response.success}');
}
```

---

## 7. Dependencies

Ensure your `pubspec.yaml` includes:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  flutter_secure_storage: ^9.0.0
```
