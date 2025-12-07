# User Authentication & Profile API - Flutter Integration Guide

Base URL: `https://fammo.ai/api/v1`

## Overview
This guide covers user registration, authentication, profile management, and language preferences for the FAMMO mobile app.

---

## Table of Contents
1. [User Registration (Signup)](#1-user-registration-signup)
2. [User Login (Get JWT Token)](#2-user-login-get-jwt-token)
3. [Refresh JWT Token](#3-refresh-jwt-token)
4. [Get User Profile](#4-get-user-profile)
5. [Forgot Password](#5-forgot-password)
6. [Reset Password](#6-reset-password)
7. [Resend Activation Email](#7-resend-activation-email)
8. [Get Available Languages](#8-get-available-languages)
9. [Set User Language Preference](#9-set-user-language-preference)
10. [Delete Test User (Dev Only)](#10-delete-test-user-dev-only)

---

## 1. User Registration (Signup)

**Endpoint:** `POST /auth/signup/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!"
}
```

**Request Example:**
```dart
final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/auth/signup/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'email': 'user@example.com',
    'password': 'SecurePassword123!',
    'password_confirm': 'SecurePassword123!',
  }),
);
```

**Password Requirements:**
- Minimum 8 characters
- Cannot be too similar to email
- Cannot be entirely numeric
- Cannot be too common (e.g., "password123")

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Registration successful. Please check your email to activate your account.",
  "user": {
    "id": 123,
    "email": "user@example.com"
  }
}
```

**Response (400 Bad Request):**
```json
{
  "email": ["A user with this email already exists."]
}
```

OR

```json
{
  "password": ["Password fields didn't match."]
}
```

OR

```json
{
  "password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is too common."
  ]
}
```

**Important Notes:**
- User account is created but **inactive** until email is verified
- An activation email is sent to the provided email address
- User must click the activation link in the email before they can login
- Activation link expires in 24 hours
- User receives email with subject: "Activate your Fammo account"

---

## 2. User Login (Get JWT Token)

**Endpoint:** `POST /auth/token/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Request Example:**
```dart
final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/auth/token/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'email': 'user@example.com',
    'password': 'SecurePassword123!',
  }),
);
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response Fields:**
- `access`: Short-lived JWT token (valid for 5 minutes) - use for API requests
- `refresh`: Long-lived token (valid for 1 day) - use to get new access tokens

**Response (401 Unauthorized):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

**Usage in Flutter:**
```dart
// Store tokens securely
final Map<String, dynamic> data = jsonDecode(response.body);
final accessToken = data['access'];
final refreshToken = data['refresh'];

// Save to secure storage (use flutter_secure_storage)
await storage.write(key: 'access_token', value: accessToken);
await storage.write(key: 'refresh_token', value: refreshToken);

// Use access token in subsequent requests
final authenticatedResponse = await http.get(
  Uri.parse('https://fammo.ai/api/v1/me/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
  },
);
```

---

## 3. Refresh JWT Token

**Endpoint:** `POST /auth/token/refresh/`

**Authentication:** Not required (but requires refresh token)

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Request Example:**
```dart
final refreshToken = await storage.read(key: 'refresh_token');

final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/auth/token/refresh/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'refresh': refreshToken,
  }),
);
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**When to refresh:**
- When access token expires (HTTP 401 error)
- Proactively before expiration (recommended)
- Access token lifetime: 5 minutes
- Refresh token lifetime: 1 day

**Flutter Implementation Example:**
```dart
Future<String> getValidAccessToken() async {
  final accessToken = await storage.read(key: 'access_token');
  
  // Try to use existing token
  final testResponse = await http.get(
    Uri.parse('https://fammo.ai/api/v1/me/'),
    headers: {'Authorization': 'Bearer $accessToken'},
  );
  
  if (testResponse.statusCode == 401) {
    // Token expired, refresh it
    final refreshToken = await storage.read(key: 'refresh_token');
    final response = await http.post(
      Uri.parse('https://fammo.ai/api/v1/auth/token/refresh/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh': refreshToken}),
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final newAccessToken = data['access'];
      await storage.write(key: 'access_token', value: newAccessToken);
      return newAccessToken;
    } else {
      // Refresh token also expired, require login
      throw Exception('Session expired, please login again');
    }
  }
  
  return accessToken!;
}
```

---

## 4. Get User Profile

**Endpoint:** `GET /me/`

**Authentication:** Required

**Request Example:**
```dart
final accessToken = await storage.read(key: 'access_token');

final response = await http.get(
  Uri.parse('https://fammo.ai/api/v1/me/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
  },
);
```

**Response (200 OK):**
```json
{
  "id": 5,
  "user": {
    "id": 12,
    "email": "user@example.com",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-11-20T10:30:00Z"
  },
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+31 20 1234567",
  "address": "Main Street 123",
  "city": "Amsterdam",
  "zip_code": "1011 AB",
  "country": "Netherlands",
  "latitude": "52.370216",
  "longitude": "4.895168",
  "location_consent": true,
  "location_updated_at": "2025-11-20T10:35:00Z",
  "subscription_plan": null,
  "is_writer": false,
  "preferred_language": "en"
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 5. Forgot Password

**Endpoint:** `POST /auth/forgot-password/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Request Example:**
```dart
final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/auth/forgot-password/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'email': 'user@example.com',
  }),
);
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "If an account with this email exists, a password reset link has been sent."
}
```

**Important Notes:**
- Always returns success to prevent email enumeration attacks
- Email contains a password reset link
- Reset link expires after 24 hours
- If email doesn't exist, no email is sent but response is still successful

---

## 6. Reset Password

**Endpoint:** `POST /auth/reset-password/`

**Authentication:** Not required (but requires valid reset token)

**Request Body:**
```json
{
  "uid": "MTI",
  "token": "abc123-def456-ghi789",
  "password": "NewSecurePassword123!",
  "password_confirm": "NewSecurePassword123!"
}
```

**Request Example:**
```dart
// uid and token are extracted from the reset link in the email
// Link format: https://fammo.ai/reset-password/{uid}/{token}/

final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/auth/reset-password/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'uid': 'MTI',
    'token': 'abc123-def456-ghi789',
    'password': 'NewSecurePassword123!',
    'password_confirm': 'NewSecurePassword123!',
  }),
);
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Password has been reset successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Invalid or expired token"
}
```

OR

```json
{
  "password": ["Password fields didn't match."]
}
```

---

## 7. Resend Activation Email

**Endpoint:** `POST /auth/resend-activation/`

**Authentication:** Not required

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Request Example:**
```dart
final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/auth/resend-activation/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'email': 'user@example.com',
  }),
);
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Activation email has been resent successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "This account is already activated"
}
```

**Response (404 Not Found):**
```json
{
  "error": "No account found with this email"
}
```

**Use Case:**
- User didn't receive activation email
- Activation link expired
- User accidentally deleted the email

---

## 8. Get Available Languages

**Endpoint:** `GET /languages/`

**Authentication:** Not required

**Request Example:**
```dart
final response = await http.get(
  Uri.parse('https://fammo.ai/api/v1/languages/'),
);
```

**Response (200 OK):**
```json
{
  "languages": [
    {
      "code": "en",
      "name": "English",
      "native_name": "English"
    },
    {
      "code": "tr",
      "name": "Turkish",
      "native_name": "Turkish"
    },
    {
      "code": "nl",
      "name": "Dutch",
      "native_name": "Dutch"
    },
    {
      "code": "fi",
      "name": "Finnish",
      "native_name": "Finnish"
    }
  ]
}
```

**Use Case:**
- Display language selector in app settings
- Show available languages during onboarding

---

## 9. Set User Language Preference

**Endpoint:** `POST /me/language/`

**Authentication:** Required

**Request Body:**
```json
{
  "language": "tr"
}
```

**Request Example:**
```dart
final accessToken = await storage.read(key: 'access_token');

final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/me/language/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode({
    'language': 'tr',
  }),
);
```

**Valid Language Codes:**
- `en` - English
- `tr` - Turkish
- `nl` - Dutch
- `fi` - Finnish

**Response (200 OK):**
```json
{
  "language": "tr"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "Language code is required"
}
```

OR

```json
{
  "error": "Invalid language code. Valid options are: en, tr, nl, fi"
}
```

**Use Case:**
- Save user's preferred language for app content
- Used to determine which language to display in the app
- Persists across app sessions

---

## 10. Delete Test User (Dev Only)

**Endpoint:** `DELETE /auth/delete-test-user/`

**Authentication:** Not required

⚠️ **WARNING:** Only available when `DEBUG=True` (development/testing environments)

**Request Body:**
```json
{
  "email": "testuser@example.com"
}
```

**Request Example:**
```dart
final response = await http.delete(
  Uri.parse('https://fammo.ai/api/v1/auth/delete-test-user/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'email': 'testuser@example.com',
  }),
);
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "User testuser@example.com has been deleted successfully"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "This endpoint is only available in DEBUG mode"
}
```

**Response (404 Not Found):**
```json
{
  "error": "No account found with this email"
}
```

**Use Case:**
- Clean up test accounts during development
- **Not available in production**
- Automatically cascades to delete Profile and related data

---

## Flutter Model Classes

```dart
class User {
  final int id;
  final String email;
  final bool isActive;
  final bool isStaff;
  final DateTime dateJoined;

  User({
    required this.id,
    required this.email,
    required this.isActive,
    required this.isStaff,
    required this.dateJoined,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      isActive: json['is_active'],
      isStaff: json['is_staff'],
      dateJoined: DateTime.parse(json['date_joined']),
    );
  }
}

class Profile {
  final int id;
  final User user;
  final String firstName;
  final String lastName;
  final String phone;
  final String address;
  final String city;
  final String zipCode;
  final String country;
  final String? latitude;
  final String? longitude;
  final bool locationConsent;
  final DateTime? locationUpdatedAt;
  final int? subscriptionPlan;
  final bool isWriter;
  final String preferredLanguage;

  Profile({
    required this.id,
    required this.user,
    required this.firstName,
    required this.lastName,
    required this.phone,
    required this.address,
    required this.city,
    required this.zipCode,
    required this.country,
    this.latitude,
    this.longitude,
    required this.locationConsent,
    this.locationUpdatedAt,
    this.subscriptionPlan,
    required this.isWriter,
    required this.preferredLanguage,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: json['id'],
      user: User.fromJson(json['user']),
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      phone: json['phone'] ?? '',
      address: json['address'] ?? '',
      city: json['city'] ?? '',
      zipCode: json['zip_code'] ?? '',
      country: json['country'] ?? '',
      latitude: json['latitude'],
      longitude: json['longitude'],
      locationConsent: json['location_consent'] ?? false,
      locationUpdatedAt: json['location_updated_at'] != null
          ? DateTime.parse(json['location_updated_at'])
          : null,
      subscriptionPlan: json['subscription_plan'],
      isWriter: json['is_writer'] ?? false,
      preferredLanguage: json['preferred_language'] ?? 'en',
    );
  }

  String get fullName => '$firstName $lastName'.trim();
}

class AuthTokens {
  final String accessToken;
  final String refreshToken;

  AuthTokens({
    required this.accessToken,
    required this.refreshToken,
  });

  factory AuthTokens.fromJson(Map<String, dynamic> json) {
    return AuthTokens(
      accessToken: json['access'],
      refreshToken: json['refresh'],
    );
  }
}

class Language {
  final String code;
  final String name;
  final String nativeName;

  Language({
    required this.code,
    required this.name,
    required this.nativeName,
  });

  factory Language.fromJson(Map<String, dynamic> json) {
    return Language(
      code: json['code'],
      name: json['name'],
      nativeName: json['native_name'],
    );
  }
}
```

---

## Complete Authentication Flow Example

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  static const String baseUrl = 'https://fammo.ai/api/v1';
  final storage = FlutterSecureStorage();

  // 1. Sign up new user
  Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/signup/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'password_confirm': password,
      }),
    );

    if (response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception(jsonDecode(response.body));
    }
  }

  // 2. Login and store tokens
  Future<AuthTokens> login({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/token/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final tokens = AuthTokens.fromJson(jsonDecode(response.body));
      
      // Store tokens securely
      await storage.write(key: 'access_token', value: tokens.accessToken);
      await storage.write(key: 'refresh_token', value: tokens.refreshToken);
      
      return tokens;
    } else {
      throw Exception('Invalid credentials');
    }
  }

  // 3. Get valid access token (with auto-refresh)
  Future<String> getAccessToken() async {
    String? accessToken = await storage.read(key: 'access_token');
    
    if (accessToken == null) {
      throw Exception('Not logged in');
    }

    // Test if token is still valid
    final testResponse = await http.get(
      Uri.parse('$baseUrl/me/'),
      headers: {'Authorization': 'Bearer $accessToken'},
    );

    if (testResponse.statusCode == 401) {
      // Token expired, refresh it
      final refreshToken = await storage.read(key: 'refresh_token');
      
      if (refreshToken == null) {
        throw Exception('Session expired');
      }

      final refreshResponse = await http.post(
        Uri.parse('$baseUrl/auth/token/refresh/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      );

      if (refreshResponse.statusCode == 200) {
        final data = jsonDecode(refreshResponse.body);
        accessToken = data['access'];
        await storage.write(key: 'access_token', value: accessToken);
      } else {
        // Refresh token also expired
        await logout();
        throw Exception('Session expired, please login again');
      }
    }

    return accessToken;
  }

  // 4. Get user profile
  Future<Profile> getProfile() async {
    final accessToken = await getAccessToken();
    
    final response = await http.get(
      Uri.parse('$baseUrl/me/'),
      headers: {'Authorization': 'Bearer $accessToken'},
    );

    if (response.statusCode == 200) {
      return Profile.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load profile');
    }
  }

  // 5. Set language preference
  Future<void> setLanguage(String languageCode) async {
    final accessToken = await getAccessToken();
    
    await http.post(
      Uri.parse('$baseUrl/me/language/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $accessToken',
      },
      body: jsonEncode({'language': languageCode}),
    );
  }

  // 6. Logout
  Future<void> logout() async {
    await storage.delete(key: 'access_token');
    await storage.delete(key: 'refresh_token');
  }

  // 7. Check if user is logged in
  Future<bool> isLoggedIn() async {
    final accessToken = await storage.read(key: 'access_token');
    return accessToken != null;
  }
}
```

---

## Error Handling

**Common Error Responses:**

**400 Bad Request:**
```json
{
  "field_name": ["Error message"]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

OR

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "error": "No account found with this email"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Registration failed: [error details]"
}
```

---

## Security Best Practices

1. **Token Storage:**
   - Store tokens in secure storage (use `flutter_secure_storage`)
   - Never store tokens in SharedPreferences or regular files
   - Clear tokens on logout

2. **Password Handling:**
   - Never log or display passwords
   - Use secure text fields for password input
   - Implement password strength indicators

3. **HTTPS Only:**
   - Always use HTTPS for API requests
   - Never send credentials over HTTP

4. **Token Refresh:**
   - Implement automatic token refresh
   - Handle expired tokens gracefully
   - Redirect to login when refresh token expires

5. **Error Messages:**
   - Don't expose sensitive information in error messages
   - Use generic messages for security-related errors
   - Log detailed errors server-side only

6. **Email Verification:**
   - Require email verification before full access
   - Implement resend activation functionality
   - Handle expired activation links

---

## Testing Credentials

**Production:** https://fammo.ai/api/v1

**Test Account:**
- Email: `paperas@superhouse.vn`
- Password: `Ali5522340731`

**Note:** Only use test accounts in development/staging environments.
