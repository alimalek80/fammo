# Flutter Profile Edit Implementation Guide

## Overview
This guide provides everything needed to implement user and clinic profile edit screens in Flutter, with proper routing based on user type.

---

## 1. API Endpoints

### Get User Profile (Determine User Type)
```
GET /api/v1/me/
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json
```

**Sample Response (Clinic Owner):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "email": "alianta2016@gmail.com",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-07-28T16:03:14.212694Z"
  },
  "is_clinic_owner": true,
  "owned_clinics": [
    {
      "id": 6,
      "name": "Test Veterinary Clinic"
    }
  ],
  "first_name": "FAMMO",
  "last_name": "TEAM",
  "phone": "05522340731",
  "address": "Sisli Pasa Mah Aralik 1 sk No 6 D 7",
  "city": "Istanbul",
  "zip_code": "34379",
  "country": "Türkiye",
  "latitude": null,
  "longitude": null,
  "location_consent": false,
  "location_updated_at": null,
  "is_writer": false,
  "preferred_language": "en",
  "subscription_plan": 2
}
```

**Sample Response (Regular Pet Owner):**
```json
{
  "id": 2,
  "user": {
    "id": 2,
    "email": "petowner@example.com",
    "is_active": true,
    "is_staff": false,
    "date_joined": "2025-08-15T10:20:30.123456Z"
  },
  "is_clinic_owner": false,
  "owned_clinics": [],
  "first_name": "John",
  "last_name": "Doe",
  "phone": "1234567890",
  "address": "123 Pet Street",
  "city": "New York",
  "zip_code": "10001",
  "country": "USA",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "location_consent": true,
  "location_updated_at": "2025-12-11T14:30:00Z",
  "is_writer": false,
  "preferred_language": "en",
  "subscription_plan": null
}
```

---

### Update User Profile (Pet Owner)
```
PATCH /api/v1/me/
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Body (only send fields you want to update):
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "1234567890",
  "address": "456 New Pet Avenue",
  "city": "Boston",
  "zip_code": "02101",
  "country": "USA",
  "location_consent": true,
  "preferred_language": "en"
}
```

**Response:** Returns the updated profile object (same structure as GET response)

---

### Get Clinic Profile (Vet Profile)
```
GET /api/v1/clinics/{clinic_id}/vet-profile/
Headers:
  Authorization: Bearer {access_token} (optional - public endpoint)
  Content-Type: application/json
```

**Sample Response:**
```json
{
  "id": 1,
  "clinic": 6,
  "vet_name": "Dr. Sarah Johnson",
  "degrees": "DVM, MSc Nutrition",
  "certifications": "AVMA, CVMA",
  "created_at": "2025-08-01T12:00:00Z",
  "updated_at": "2025-12-11T14:30:00Z"
}
```

---

### Update Clinic Profile (Vet Profile)
```
PATCH /api/v1/clinics/{clinic_id}/vet-profile/
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Body:
{
  "vet_name": "Dr. Sarah Johnson",
  "degrees": "DVM, MSc Nutrition, PhD",
  "certifications": "AVMA, CVMA, Certified Nutritionist"
}
```

**Response:** Returns the updated vet profile object

---

### Get Full Clinic Details (for clinic profile page)
```
GET /api/v1/clinics/{clinic_id}/
Headers:
  Authorization: Bearer {access_token} (optional)
  Content-Type: application/json
```

**Sample Response:**
```json
{
  "id": 6,
  "owner": 1,
  "name": "Test Veterinary Clinic",
  "slug": "test-veterinary-clinic",
  "city": "Istanbul",
  "address": "Sisli Pasa Mah Aralik 1 sk No 6 D 7",
  "latitude": 41.0764,
  "longitude": 29.0188,
  "phone": "05522340731",
  "email": "clinic@example.com",
  "website": "https://example.com",
  "instagram": "@exampleclinic",
  "specializations": "Cats, Dogs, Nutrition",
  "working_hours": "Mon–Sat 09:00–18:00",
  "working_hours_schedule": [
    {
      "id": 1,
      "day_of_week": 0,
      "day_name": "Monday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 2,
      "day_of_week": 1,
      "day_name": "Tuesday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 3,
      "day_of_week": 2,
      "day_name": "Wednesday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 4,
      "day_of_week": 3,
      "day_name": "Thursday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 5,
      "day_of_week": 4,
      "day_name": "Friday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 6,
      "day_of_week": 5,
      "day_name": "Saturday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 7,
      "day_of_week": 6,
      "day_name": "Sunday",
      "is_closed": true,
      "open_time": null,
      "close_time": null
    }
  ],
  "formatted_working_hours": [
    "Monday: 09:00 - 18:00",
    "Tuesday: 09:00 - 18:00",
    "Wednesday: 09:00 - 18:00",
    "Thursday: 09:00 - 18:00",
    "Friday: 09:00 - 18:00",
    "Saturday: 09:00 - 18:00",
    "Sunday: Closed"
  ],
  "bio": "Professional veterinary clinic with experienced team",
  "logo": "https://example.com/logo.jpg",
  "is_verified": true,
  "email_confirmed": true,
  "admin_approved": true,
  "clinic_eoi": false,
  "created_at": "2025-08-01T12:00:00Z",
  "updated_at": "2025-12-11T14:30:00Z",
  "vet_profile": {
    "id": 1,
    "clinic": 6,
    "vet_name": "Dr. Sarah Johnson",
    "degrees": "DVM, MSc Nutrition",
    "certifications": "AVMA, CVMA"
  }
}
```

---

### Update Full Clinic Details
```
PATCH /api/v1/clinics/{clinic_id}/
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Body (clinic owner only):
{
  "name": "Test Veterinary Clinic",
  "city": "Istanbul",
  "address": "Sisli Pasa Mah Aralik 1 sk No 6 D 7",
  "phone": "05522340731",
  "email": "clinic@example.com",
  "website": "https://example.com",
  "instagram": "@exampleclinic",
  "specializations": "Cats, Dogs, Nutrition, Emergency",
  "bio": "Professional veterinary clinic with experienced team"
}
```

**Response:** Returns the updated clinic object

---

### Get Clinic Working Hours
```
GET /api/v1/clinics/{clinic_id}/working-hours/
Headers:
  Authorization: Bearer {access_token} (optional)
  Content-Type: application/json
```

**Sample Response:**
```json
[
  {
    "id": 1,
    "day_of_week": 0,
    "day_name": "Monday",
    "is_closed": false,
    "open_time": "09:00:00",
    "close_time": "18:00:00"
  },
  {
    "id": 2,
    "day_of_week": 1,
    "day_name": "Tuesday",
    "is_closed": false,
    "open_time": "09:00:00",
    "close_time": "18:00:00"
  },
  {
    "id": 3,
    "day_of_week": 2,
    "day_name": "Wednesday",
    "is_closed": false,
    "open_time": "09:00:00",
    "close_time": "18:00:00"
  },
  {
    "id": 4,
    "day_of_week": 3,
    "day_name": "Thursday",
    "is_closed": false,
    "open_time": "09:00:00",
    "close_time": "18:00:00"
  },
  {
    "id": 5,
    "day_of_week": 4,
    "day_name": "Friday",
    "is_closed": false,
    "open_time": "09:00:00",
    "close_time": "18:00:00"
  },
  {
    "id": 6,
    "day_of_week": 5,
    "day_name": "Saturday",
    "is_closed": false,
    "open_time": "09:00:00",
    "close_time": "18:00:00"
  },
  {
    "id": 7,
    "day_of_week": 6,
    "day_name": "Sunday",
    "is_closed": true,
    "open_time": null,
    "close_time": null
  }
]
```

---

### Update Clinic Working Hours (Bulk)
```
POST /api/v1/clinics/{clinic_id}/working-hours/
Headers:
  Authorization: Bearer {access_token}
  Content-Type: application/json

Body (array of working hours for each day):
[
  {
    "day_of_week": 0,
    "is_closed": false,
    "open_time": "09:00",
    "close_time": "18:00"
  },
  {
    "day_of_week": 1,
    "is_closed": false,
    "open_time": "09:00",
    "close_time": "18:00"
  },
  {
    "day_of_week": 2,
    "is_closed": false,
    "open_time": "09:00",
    "close_time": "18:00"
  },
  {
    "day_of_week": 3,
    "is_closed": false,
    "open_time": "09:00",
    "close_time": "18:00"
  },
  {
    "day_of_week": 4,
    "is_closed": false,
    "open_time": "09:00",
    "close_time": "18:00"
  },
  {
    "day_of_week": 5,
    "is_closed": false,
    "open_time": "09:00",
    "close_time": "18:00"
  },
  {
    "day_of_week": 6,
    "is_closed": true,
    "open_time": null,
    "close_time": null
  }
]
```

**Response:** Returns the updated working hours array

---

## 2. Editable Fields Summary

### Pet Owner Profile (User Profile)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| first_name | String (100) | Yes | Maximum 100 characters |
| last_name | String (100) | Yes | Maximum 100 characters |
| phone | String (20) | Yes | Maximum 20 characters |
| address | String (Text) | Yes | Full address field |
| city | String (100) | Yes | City name |
| zip_code | String (20) | Yes | Postal/ZIP code |
| country | String (100) | Yes | Country name |
| location_consent | Boolean | No | User consent for location storage |
| preferred_language | String (7) | No | Language code (e.g., 'en', 'tr') |

### Clinic Profile (Clinic Details)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | String (160) | Yes | Unique clinic name |
| city | String (80) | No | City location |
| address | String (220) | No | Full address |
| phone | String (40) | No | Contact phone |
| email | String | No | Contact email |
| website | String | No | Website URL |
| instagram | String (120) | No | Instagram handle or URL |
| specializations | String (200) | No | Comma-separated (e.g., "Cats, Dogs, Nutrition") |
| bio | String (Text) | No | Clinic description |

### Clinic Working Hours (Structured - Selectable Days)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| day_of_week | Integer (0-6) | Yes | 0=Monday, 1=Tuesday, ... 6=Sunday |
| is_closed | Boolean | Yes | True if clinic is closed this day |
| open_time | Time (HH:MM) | No | Opening time (null if closed) |
| close_time | Time (HH:MM) | No | Closing time (null if closed) |

**Important:** Working hours are submitted as an array of 7 objects (one per day). Use the dedicated endpoint `/api/v1/clinics/{clinic_id}/working-hours/` for updates.

### Vet Profile (Veterinarian Details)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| vet_name | String (120) | Yes | Full name of veterinarian |
| degrees | String (200) | No | Degrees (e.g., "DVM, MSc Nutrition") |
| certifications | String (240) | No | Certifications/qualifications |

---

## 3. Flutter Implementation

### Step 1: Create Models

```dart
// models/profile.dart
class UserProfile {
  final int id;
  final UserData user;
  final bool isClinicOwner;
  final List<OwnedClinic> ownedClinics;
  final String firstName;
  final String lastName;
  final String phone;
  final String address;
  final String city;
  final String zipCode;
  final String country;
  final double? latitude;
  final double? longitude;
  final bool locationConsent;
  final String? locationUpdatedAt;
  final bool isWriter;
  final String preferredLanguage;
  final int? subscriptionPlan;

  UserProfile({
    required this.id,
    required this.user,
    required this.isClinicOwner,
    required this.ownedClinics,
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
    required this.isWriter,
    required this.preferredLanguage,
    this.subscriptionPlan,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      user: UserData.fromJson(json['user']),
      isClinicOwner: json['is_clinic_owner'] ?? false,
      ownedClinics: (json['owned_clinics'] as List)
          .map((c) => OwnedClinic.fromJson(c))
          .toList(),
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      phone: json['phone'] ?? '',
      address: json['address'] ?? '',
      city: json['city'] ?? '',
      zipCode: json['zip_code'] ?? '',
      country: json['country'] ?? '',
      latitude: json['latitude'] != null ? double.parse(json['latitude'].toString()) : null,
      longitude: json['longitude'] != null ? double.parse(json['longitude'].toString()) : null,
      locationConsent: json['location_consent'] ?? false,
      locationUpdatedAt: json['location_updated_at'],
      isWriter: json['is_writer'] ?? false,
      preferredLanguage: json['preferred_language'] ?? 'en',
      subscriptionPlan: json['subscription_plan'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'first_name': firstName,
      'last_name': lastName,
      'phone': phone,
      'address': address,
      'city': city,
      'zip_code': zipCode,
      'country': country,
      'location_consent': locationConsent,
      'preferred_language': preferredLanguage,
    };
  }
}

class UserData {
  final int id;
  final String email;
  final bool isActive;
  final bool isStaff;
  final String dateJoined;

  UserData({
    required this.id,
    required this.email,
    required this.isActive,
    required this.isStaff,
    required this.dateJoined,
  });

  factory UserData.fromJson(Map<String, dynamic> json) {
    return UserData(
      id: json['id'],
      email: json['email'],
      isActive: json['is_active'] ?? false,
      isStaff: json['is_staff'] ?? false,
      dateJoined: json['date_joined'] ?? '',
    );
  }
}

class OwnedClinic {
  final int id;
  final String name;

  OwnedClinic({required this.id, required this.name});

  factory OwnedClinic.fromJson(Map<String, dynamic> json) {
    return OwnedClinic(
      id: json['id'],
      name: json['name'],
    );
  }
}

// models/clinic.dart
class Clinic {
  final int id;
  final int owner;
  final String name;
  final String slug;
  final String city;
  final String address;
  final double? latitude;
  final double? longitude;
  final String phone;
  final String email;
  final String website;
  final String instagram;
  final String specializations;
  final String bio;
  final String? logo;
  final bool isVerified;
  final bool emailConfirmed;
  final bool adminApproved;
  final bool clinicEoi;
  final VetProfile? vetProfile;
  final List<WorkingHours> workingHoursSchedule;
  final String createdAt;
  final String updatedAt;

  Clinic({
    required this.id,
    required this.owner,
    required this.name,
    required this.slug,
    required this.city,
    required this.address,
    this.latitude,
    this.longitude,
    required this.phone,
    required this.email,
    required this.website,
    required this.instagram,
    required this.specializations,
    required this.bio,
    this.logo,
    required this.isVerified,
    required this.emailConfirmed,
    required this.adminApproved,
    required this.clinicEoi,
    this.vetProfile,
    required this.workingHoursSchedule,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Clinic.fromJson(Map<String, dynamic> json) {
    return Clinic(
      id: json['id'],
      owner: json['owner'],
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
      city: json['city'] ?? '',
      address: json['address'] ?? '',
      latitude: json['latitude'] != null ? double.parse(json['latitude'].toString()) : null,
      longitude: json['longitude'] != null ? double.parse(json['longitude'].toString()) : null,
      phone: json['phone'] ?? '',
      email: json['email'] ?? '',
      website: json['website'] ?? '',
      instagram: json['instagram'] ?? '',
      specializations: json['specializations'] ?? '',
      bio: json['bio'] ?? '',
      logo: json['logo'],
      isVerified: json['is_verified'] ?? false,
      emailConfirmed: json['email_confirmed'] ?? false,
      adminApproved: json['admin_approved'] ?? false,
      clinicEoi: json['clinic_eoi'] ?? false,
      vetProfile: json['vet_profile'] != null ? VetProfile.fromJson(json['vet_profile']) : null,
      workingHoursSchedule: (json['working_hours_schedule'] as List?)
          ?.map((w) => WorkingHours.fromJson(w))
          .toList() ?? [],
      createdAt: json['created_at'] ?? '',
      updatedAt: json['updated_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'city': city,
      'address': address,
      'phone': phone,
      'email': email,
      'website': website,
      'instagram': instagram,
      'specializations': specializations,
      'bio': bio,
    };
  }
}

class WorkingHours {
  final int id;
  final int dayOfWeek; // 0=Monday, 1=Tuesday, ... 6=Sunday
  final String dayName; // "Monday", "Tuesday", etc.
  final bool isClosed;
  final String? openTime; // Format: "09:00:00"
  final String? closeTime; // Format: "18:00:00"

  WorkingHours({
    required this.id,
    required this.dayOfWeek,
    required this.dayName,
    required this.isClosed,
    this.openTime,
    this.closeTime,
  });

  factory WorkingHours.fromJson(Map<String, dynamic> json) {
    return WorkingHours(
      id: json['id'],
      dayOfWeek: json['day_of_week'],
      dayName: json['day_name'] ?? '',
      isClosed: json['is_closed'] ?? false,
      openTime: json['open_time'],
      closeTime: json['close_time'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'day_of_week': dayOfWeek,
      'is_closed': isClosed,
      'open_time': openTime,
      'close_time': closeTime,
    };
  }
}

class VetProfile {
  final int id;
  final int clinic;
  final String vetName;
  final String degrees;
  final String certifications;
  final String createdAt;
  final String updatedAt;

  VetProfile({
    required this.id,
    required this.clinic,
    required this.vetName,
    required this.degrees,
    required this.certifications,
    required this.createdAt,
    required this.updatedAt,
  });

  factory VetProfile.fromJson(Map<String, dynamic> json) {
    return VetProfile(
      id: json['id'],
      clinic: json['clinic'],
      vetName: json['vet_name'] ?? '',
      degrees: json['degrees'] ?? '',
      certifications: json['certifications'] ?? '',
      createdAt: json['created_at'] ?? '',
      updatedAt: json['updated_at'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'vet_name': vetName,
      'degrees': degrees,
      'certifications': certifications,
    };
  }
}
```

---

### Step 2: Create API Service

```dart
// services/api_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiService {
  static const String baseUrl = 'https://your-domain.com/api/v1';
  static const storage = FlutterSecureStorage();

  // Get user profile and determine user type
  static Future<UserProfile> getUserProfile() async {
    try {
      final token = await storage.read(key: 'access_token');
      final response = await http.get(
        Uri.parse('$baseUrl/me/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return UserProfile.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to load profile: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching profile: $e');
    }
  }

  // Update user profile
  static Future<UserProfile> updateUserProfile(UserProfile profile) async {
    try {
      final token = await storage.read(key: 'access_token');
      final response = await http.patch(
        Uri.parse('$baseUrl/me/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(profile.toJson()),
      );

      if (response.statusCode == 200) {
        return UserProfile.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to update profile: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error updating profile: $e');
    }
  }

  // Get clinic details
  static Future<Clinic> getClinicDetails(int clinicId) async {
    try {
      final token = await storage.read(key: 'access_token');
      final response = await http.get(
        Uri.parse('$baseUrl/clinics/$clinicId/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return Clinic.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to load clinic: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching clinic: $e');
    }
  }

  // Update clinic details
  static Future<Clinic> updateClinicDetails(int clinicId, Clinic clinic) async {
    try {
      final token = await storage.read(key: 'access_token');
      final response = await http.patch(
        Uri.parse('$baseUrl/clinics/$clinicId/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(clinic.toJson()),
      );

      if (response.statusCode == 200) {
        return Clinic.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to update clinic: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error updating clinic: $e');
    }
  }

  // Get clinic working hours
  static Future<List<WorkingHours>> getClinicWorkingHours(int clinicId) async {
    try {
      final token = await storage.read(key: 'access_token');
      final response = await http.get(
        Uri.parse('$baseUrl/clinics/$clinicId/working-hours/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((w) => WorkingHours.fromJson(w)).toList();
      } else {
        throw Exception('Failed to load working hours: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching working hours: $e');
    }
  }

  // Update clinic working hours (bulk)
  static Future<List<WorkingHours>> updateClinicWorkingHours(
    int clinicId,
    List<WorkingHours> workingHours,
  ) async {
    try {
      final token = await storage.read(key: 'access_token');
      
      // Convert to API format
      final List<Map<String, dynamic>> body = workingHours
          .map((w) => w.toJson())
          .toList();

      final response = await http.post(
        Uri.parse('$baseUrl/clinics/$clinicId/working-hours/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(body),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final decodedBody = jsonDecode(response.body);
        // Response might be wrapped in 'working_hours' key
        final List<dynamic> data = decodedBody is List 
            ? decodedBody 
            : decodedBody['working_hours'] ?? [];
        return data.map((w) => WorkingHours.fromJson(w)).toList();
      } else {
        throw Exception('Failed to update working hours: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error updating working hours: $e');
    }
  }

  // Get vet profile
  static Future<VetProfile> getVetProfile(int clinicId) async {
    try {
      final token = await storage.read(key: 'access_token');
      final response = await http.get(
        Uri.parse('$baseUrl/clinics/$clinicId/vet-profile/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return VetProfile.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to load vet profile: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching vet profile: $e');
    }
  }

  // Update vet profile
  static Future<VetProfile> updateVetProfile(int clinicId, VetProfile vetProfile) async {
    try {
      final token = await storage.read(key: 'access_token');
      final response = await http.patch(
        Uri.parse('$baseUrl/clinics/$clinicId/vet-profile/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(vetProfile.toJson()),
      );

      if (response.statusCode == 200) {
        return VetProfile.fromJson(jsonDecode(response.body));
      } else {
        throw Exception('Failed to update vet profile: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error updating vet profile: $e');
    }
  }
}
```

---

### Step 3: Create Navigation/Routing Logic

```dart
// screens/profile/profile_selector.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/profile.dart';
import '../../services/api_service.dart';
import 'user_profile_edit.dart';
import 'clinic_profile_edit.dart';

class ProfileSelectorScreen extends StatefulWidget {
  @override
  State<ProfileSelectorScreen> createState() => _ProfileSelectorScreenState();
}

class _ProfileSelectorScreenState extends State<ProfileSelectorScreen> {
  late Future<UserProfile> _profileFuture;

  @override
  void initState() {
    super.initState();
    _profileFuture = ApiService.getUserProfile();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<UserProfile>(
      future: _profileFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        if (snapshot.hasError) {
          return Scaffold(
            body: Center(child: Text('Error: ${snapshot.error}')),
          );
        }

        final profile = snapshot.data!;

        // Route to appropriate profile edit screen
        if (profile.isClinicOwner && profile.ownedClinics.isNotEmpty) {
          // Go to clinic profile edit
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(
                builder: (context) => ClinicProfileEditScreen(
                  clinicId: profile.ownedClinics.first.id,
                  clinicName: profile.ownedClinics.first.name,
                ),
              ),
            );
          });
        } else {
          // Go to user profile edit
          WidgetsBinding.instance.addPostFrameCallback((_) {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(
                builder: (context) => UserProfileEditScreen(profile: profile),
              ),
            );
          });
        }

        return Scaffold(
          body: Center(child: CircularProgressIndicator()),
        );
      },
    );
  }
}
```

---

### Step 4: Create Pet Owner Profile Edit Screen

```dart
// screens/profile/user_profile_edit.dart
import 'package:flutter/material.dart';
import '../../models/profile.dart';
import '../../services/api_service.dart';

class UserProfileEditScreen extends StatefulWidget {
  final UserProfile profile;

  const UserProfileEditScreen({required this.profile});

  @override
  State<UserProfileEditScreen> createState() => _UserProfileEditScreenState();
}

class _UserProfileEditScreenState extends State<UserProfileEditScreen> {
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late TextEditingController _phoneController;
  late TextEditingController _addressController;
  late TextEditingController _cityController;
  late TextEditingController _zipCodeController;
  late TextEditingController _countryController;
  bool _locationConsent = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _firstNameController = TextEditingController(text: widget.profile.firstName);
    _lastNameController = TextEditingController(text: widget.profile.lastName);
    _phoneController = TextEditingController(text: widget.profile.phone);
    _addressController = TextEditingController(text: widget.profile.address);
    _cityController = TextEditingController(text: widget.profile.city);
    _zipCodeController = TextEditingController(text: widget.profile.zipCode);
    _countryController = TextEditingController(text: widget.profile.country);
    _locationConsent = widget.profile.locationConsent;
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _addressController.dispose();
    _cityController.dispose();
    _zipCodeController.dispose();
    _countryController.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    setState(() => _isLoading = true);

    try {
      final updatedProfile = UserProfile(
        id: widget.profile.id,
        user: widget.profile.user,
        isClinicOwner: widget.profile.isClinicOwner,
        ownedClinics: widget.profile.ownedClinics,
        firstName: _firstNameController.text,
        lastName: _lastNameController.text,
        phone: _phoneController.text,
        address: _addressController.text,
        city: _cityController.text,
        zipCode: _zipCodeController.text,
        country: _countryController.text,
        latitude: widget.profile.latitude,
        longitude: widget.profile.longitude,
        locationConsent: _locationConsent,
        locationUpdatedAt: widget.profile.locationUpdatedAt,
        isWriter: widget.profile.isWriter,
        preferredLanguage: widget.profile.preferredLanguage,
        subscriptionPlan: widget.profile.subscriptionPlan,
      );

      await ApiService.updateUserProfile(updatedProfile);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Profile updated successfully!')),
      );

      Navigator.pop(context);
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
      appBar: AppBar(
        title: Text('Edit Pet Owner Profile'),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _firstNameController,
              decoration: InputDecoration(
                labelText: 'First Name',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _lastNameController,
              decoration: InputDecoration(
                labelText: 'Last Name',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _phoneController,
              decoration: InputDecoration(
                labelText: 'Phone Number',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _addressController,
              decoration: InputDecoration(
                labelText: 'Address',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _cityController,
              decoration: InputDecoration(
                labelText: 'City',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _zipCodeController,
              decoration: InputDecoration(
                labelText: 'ZIP Code',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _countryController,
              decoration: InputDecoration(
                labelText: 'Country',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 16),
            CheckboxListTile(
              title: Text('Allow location storage'),
              value: _locationConsent,
              onChanged: (value) {
                setState(() => _locationConsent = value ?? false);
              },
            ),
            SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _saveProfile,
                child: _isLoading
                    ? CircularProgressIndicator()
                    : Text('Save Changes'),
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

### Step 5: Create Clinic Profile Edit Screen

```dart
// screens/profile/clinic_profile_edit.dart
import 'package:flutter/material.dart';
import '../../models/clinic.dart';
import '../../services/api_service.dart';

class ClinicProfileEditScreen extends StatefulWidget {
  final int clinicId;
  final String clinicName;

  const ClinicProfileEditScreen({
    required this.clinicId,
    required this.clinicName,
  });

  @override
  State<ClinicProfileEditScreen> createState() => _ClinicProfileEditScreenState();
}

class _ClinicProfileEditScreenState extends State<ClinicProfileEditScreen> {
  late Future<Clinic> _clinicFuture;
  late TextEditingController _nameController;
  late TextEditingController _cityController;
  late TextEditingController _addressController;
  late TextEditingController _phoneController;
  late TextEditingController _emailController;
  late TextEditingController _websiteController;
  late TextEditingController _instagramController;
  late TextEditingController _specializationsController;
  late TextEditingController _bioController;
  late TextEditingController _vetNameController;
  late TextEditingController _degreesController;
  late TextEditingController _certificationsController;
  
  late List<WorkingHoursController> _workingHoursControllers;
  bool _isLoading = false;
  bool _isSavingHours = false;
  Clinic? _clinic;

  @override
  void initState() {
    super.initState();
    _clinicFuture = ApiService.getClinicDetails(widget.clinicId);
    _initializeControllers();
  }

  void _initializeControllers() {
    _nameController = TextEditingController();
    _cityController = TextEditingController();
    _addressController = TextEditingController();
    _phoneController = TextEditingController();
    _emailController = TextEditingController();
    _websiteController = TextEditingController();
    _instagramController = TextEditingController();
    _specializationsController = TextEditingController();
    _bioController = TextEditingController();
    _vetNameController = TextEditingController();
    _degreesController = TextEditingController();
    _certificationsController = TextEditingController();
    _workingHoursControllers = [];
  }

  void _populateControllers(Clinic clinic) {
    _nameController.text = clinic.name;
    _cityController.text = clinic.city;
    _addressController.text = clinic.address;
    _phoneController.text = clinic.phone;
    _emailController.text = clinic.email;
    _websiteController.text = clinic.website;
    _instagramController.text = clinic.instagram;
    _specializationsController.text = clinic.specializations;
    _bioController.text = clinic.bio;
    if (clinic.vetProfile != null) {
      _vetNameController.text = clinic.vetProfile!.vetName;
      _degreesController.text = clinic.vetProfile!.degrees;
      _certificationsController.text = clinic.vetProfile!.certifications;
    }
    
    // Initialize working hours controllers
    _workingHoursControllers = clinic.workingHoursSchedule
        .map((w) => WorkingHoursController.fromWorkingHours(w))
        .toList();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _cityController.dispose();
    _addressController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _websiteController.dispose();
    _instagramController.dispose();
    _specializationsController.dispose();
    _workingHoursController.dispose();
    _bioController.dispose();
    _vetNameController.dispose();
    _degreesController.dispose();
    _certificationsController.dispose();
    super.dispose();
  }

  Future<void> _saveClinic() async {
    setState(() => _isLoading = true);

    try {
      final updatedClinic = Clinic(
        id: _clinic!.id,
        owner: _clinic!.owner,
        name: _nameController.text,
        slug: _clinic!.slug,
        city: _cityController.text,
        address: _addressController.text,
        latitude: _clinic!.latitude,
        longitude: _clinic!.longitude,
        phone: _phoneController.text,
        email: _emailController.text,
        website: _websiteController.text,
        instagram: _instagramController.text,
        specializations: _specializationsController.text,
        bio: _bioController.text,
        logo: _clinic!.logo,
        isVerified: _clinic!.isVerified,
        emailConfirmed: _clinic!.emailConfirmed,
        adminApproved: _clinic!.adminApproved,
        clinicEoi: _clinic!.clinicEoi,
        vetProfile: _clinic!.vetProfile,
        workingHoursSchedule: _clinic!.workingHoursSchedule,
        createdAt: _clinic!.createdAt,
        updatedAt: _clinic!.updatedAt,
      );

      await ApiService.updateClinicDetails(widget.clinicId, updatedClinic);

      // Update vet profile if available
      if (_clinic!.vetProfile != null) {
        final updatedVetProfile = VetProfile(
          id: _clinic!.vetProfile!.id,
          clinic: _clinic!.vetProfile!.clinic,
          vetName: _vetNameController.text,
          degrees: _degreesController.text,
          certifications: _certificationsController.text,
          createdAt: _clinic!.vetProfile!.createdAt,
          updatedAt: _clinic!.vetProfile!.updatedAt,
        );

        await ApiService.updateVetProfile(widget.clinicId, updatedVetProfile);
      }

      // Update working hours separately
      await _saveWorkingHours();

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Clinic profile updated successfully!')),
      );

      Navigator.pop(context);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _saveWorkingHours() async {
    setState(() => _isSavingHours = true);

    try {
      final workingHoursList = _workingHoursControllers
          .map((c) => c.toWorkingHours())
          .toList();

      await ApiService.updateClinicWorkingHours(widget.clinicId, workingHoursList);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Working hours updated successfully!')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error updating working hours: $e')),
      );
      rethrow;
    } finally {
      setState(() => _isSavingHours = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Clinic>(
      future: _clinicFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Scaffold(
            appBar: AppBar(title: Text('Edit Clinic Profile')),
            body: Center(child: CircularProgressIndicator()),
          );
        }

        if (snapshot.hasError) {
          return Scaffold(
            appBar: AppBar(title: Text('Edit Clinic Profile')),
            body: Center(child: Text('Error: ${snapshot.error}')),
          );
        }

        if (!snapshot.hasData) {
          return Scaffold(
            appBar: AppBar(title: Text('Edit Clinic Profile')),
            body: Center(child: Text('No clinic data found')),
          );
        }

        _clinic = snapshot.data!;
        _populateControllers(_clinic!);

        return Scaffold(
          appBar: AppBar(
            title: Text('Edit ${widget.clinicName}'),
          ),
          body: SingleChildScrollView(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Clinic Information',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _nameController,
                  decoration: InputDecoration(
                    labelText: 'Clinic Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _cityController,
                  decoration: InputDecoration(
                    labelText: 'City',
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _addressController,
                  decoration: InputDecoration(
                    labelText: 'Address',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _phoneController,
                  decoration: InputDecoration(
                    labelText: 'Phone',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.phone,
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _emailController,
                  decoration: InputDecoration(
                    labelText: 'Email',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.emailAddress,
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _websiteController,
                  decoration: InputDecoration(
                    labelText: 'Website',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.url,
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _instagramController,
                  decoration: InputDecoration(
                    labelText: 'Instagram',
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _specializationsController,
                  decoration: InputDecoration(
                    labelText: 'Specializations',
                    hintText: 'Cats, Dogs, Nutrition',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
                SizedBox(height: 24),
                Text(
                  'Working Hours',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                SizedBox(height: 8),
                Text(
                  'Set your clinic hours for each day of the week',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                SizedBox(height: 16),
                ..._buildWorkingHoursSelectors(),
                SizedBox(height: 16),
                TextField(
                  controller: _bioController,
                  decoration: InputDecoration(
                    labelText: 'Clinic Bio',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 3,
                ),
                SizedBox(height: 24),
                Text(
                  'Veterinarian Information',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _vetNameController,
                  decoration: InputDecoration(
                    labelText: 'Vet Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _degreesController,
                  decoration: InputDecoration(
                    labelText: 'Degrees',
                    hintText: 'DVM, MSc Nutrition',
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                TextField(
                  controller: _certificationsController,
                  decoration: InputDecoration(
                    labelText: 'Certifications',
                    border: OutlineInputBorder(),
                  ),
                  maxLines: 2,
                ),
                SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _saveClinic,
                    child: _isLoading
                        ? CircularProgressIndicator()
                        : Text('Save Changes'),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
```

---

## 4. Usage Example

```dart
// In your main navigation or profile button tap handler:
onTap: () {
  Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => ProfileSelectorScreen(),
    ),
  );
}
```

The `ProfileSelectorScreen` automatically fetches the user's profile from `/api/me/`, checks the `is_clinic_owner` flag, and routes to the appropriate edit screen.

---

## 5. Error Handling & Best Practices

- **Network Errors**: Wrap API calls in try-catch and show user-friendly error messages
- **Validation**: Validate required fields before sending to API
- **Loading States**: Show loading indicators during API calls
- **Success Feedback**: Show snackbars or dialogs confirming successful updates
- **Token Refresh**: Handle 401 responses by refreshing auth token
- **Timeouts**: Set request timeouts for better UX

---

## 6. Helper Classes for Working Hours

Add this class to handle working hours UI state:

```dart
// Helper class to manage working hours form state
class WorkingHoursController {
  final int id;
  final int dayOfWeek;
  final String dayName;
  bool isClosed;
  String? openTime; // HH:MM format
  String? closeTime; // HH:MM format

  WorkingHoursController({
    required this.id,
    required this.dayOfWeek,
    required this.dayName,
    required this.isClosed,
    this.openTime,
    this.closeTime,
  });

  factory WorkingHoursController.fromWorkingHours(WorkingHours w) {
    return WorkingHoursController(
      id: w.id,
      dayOfWeek: w.dayOfWeek,
      dayName: w.dayName,
      isClosed: w.isClosed,
      openTime: w.openTime != null ? w.openTime!.substring(0, 5) : null,
      closeTime: w.closeTime != null ? w.closeTime!.substring(0, 5) : null,
    );
  }

  WorkingHours toWorkingHours() {
    return WorkingHours(
      id: id,
      dayOfWeek: dayOfWeek,
      dayName: dayName,
      isClosed: isClosed,
      openTime: openTime != null ? '$openTime:00' : null,
      closeTime: closeTime != null ? '$closeTime:00' : null,
    );
  }
}
```

Add this method to `_ClinicProfileEditScreenState`:

```dart
  List<Widget> _buildWorkingHoursSelectors() {
    return _workingHoursControllers.asMap().entries.map((entry) {
      final index = entry.key;
      final controller = entry.value;

      return Card(
        child: Padding(
          padding: EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                controller.dayName,
                style: Theme.of(context).textTheme.titleMedium,
              ),
              SizedBox(height: 12),
              CheckboxListTile(
                title: Text('Closed'),
                value: controller.isClosed,
                onChanged: (value) {
                  setState(() {
                    _workingHoursControllers[index].isClosed = value ?? false;
                  });
                },
              ),
              if (!controller.isClosed) ...[
                SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          labelText: 'Open Time',
                          hintText: '09:00',
                          border: OutlineInputBorder(),
                        ),
                        initialValue: controller.openTime ?? '',
                        onChanged: (value) {
                          setState(() {
                            _workingHoursControllers[index].openTime = value;
                          });
                        },
                      ),
                    ),
                    SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        decoration: InputDecoration(
                          labelText: 'Close Time',
                          hintText: '18:00',
                          border: OutlineInputBorder(),
                        ),
                        initialValue: controller.closeTime ?? '',
                        onChanged: (value) {
                          setState(() {
                            _workingHoursControllers[index].closeTime = value;
                          });
                        },
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      );
    }).toList();
  }
```

## 7. Dependencies

Add to `pubspec.yaml`:
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  flutter_secure_storage: ^9.0.0
  provider: ^6.0.0
```

