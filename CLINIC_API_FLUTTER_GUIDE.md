# Clinic API Endpoints - Flutter Integration Guide

Base URL: `https://fammo.ai/api/v1`

## Authentication Required
All clinic management endpoints (except listing and search) require JWT authentication.

Add to request headers:
```dart
'Authorization': 'Bearer $accessToken'
```

---

## 1. List All Active Clinics

**Endpoint:** `GET /clinics/`

**Authentication:** Not required

**Query Parameters:**
- `show_all` (optional): `true` to include pending clinics, default shows only active
- `city` (optional): Filter by city name
- `eoi` (optional): `true/false` to filter by EOI status

**Request Example:**
```dart
final response = await http.get(
  Uri.parse('https://fammo.ai/api/v1/clinics/'),
);
```

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "name": "Ibadoyos klinik",
    "slug": "ibadoyos-klinik",
    "city": "Istanbul",
    "address": "Cevizli, 30 Ağustos Cd. No:15, 34846 Maltepe/İstanbul",
    "latitude": "41.006381",
    "longitude": "28.975872",
    "phone": "05523553091",
    "email": "ibadoyos@gmail.com",
    "website": "",
    "instagram": "",
    "specializations": "Köpek ve kedi",
    "logo": "https://fammo.ai/fammo/media/clinic_logos/58f4f779-51d7-4c8f-b4d9-a6bc1d17f61c.jpeg",
    "is_verified": false,
    "email_confirmed": true,
    "admin_approved": true,
    "is_active_clinic": true,
    "referral_code": "vet-ibadoyoskl"
  }
]
```

---

## 2. Register New Clinic

**Endpoint:** `POST /clinics/`

**Authentication:** Required

**Request Body:**
```json
{
  "name": "My Veterinary Clinic",
  "city": "Amsterdam",
  "address": "Main Street 123",
  "latitude": 52.370216,
  "longitude": 4.895168,
  "phone": "+31 20 1234567",
  "email": "clinic@example.com",
  "website": "https://myclinic.com",
  "instagram": "@myclinic",
  "specializations": "Dogs, Cats, Birds",
  "working_hours": "Mon-Fri 09:00-18:00",
  "bio": "Professional veterinary care for your pets",
  "clinic_eoi": true,
  "vet_name": "Dr. Jane Smith",
  "degrees": "DVM, PhD",
  "certifications": "Board Certified in Surgery"
}
```

**Request Example:**
```dart
final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/clinics/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode({
    'name': 'My Veterinary Clinic',
    'city': 'Amsterdam',
    'address': 'Main Street 123',
    'phone': '+31 20 1234567',
    'email': 'clinic@example.com',
    'specializations': 'Dogs, Cats, Birds',
    'bio': 'Professional veterinary care for your pets',
    'clinic_eoi': true,
    'vet_name': 'Dr. Jane Smith',
    'degrees': 'DVM',
  }),
);
```

**Required Fields:**
- `name`

**Optional Fields:**
- `city`, `address`, `latitude`, `longitude`
- `phone`, `email`, `website`, `instagram`
- `specializations`, `working_hours`, `bio`
- `logo` (use multipart/form-data for file upload)
- `clinic_eoi` (default: false)
- `vet_name`, `degrees`, `certifications` (for vet profile)

**Response (201 Created):**
```json
{
  "id": 3,
  "name": "My Veterinary Clinic",
  "slug": "my-veterinary-clinic",
  "city": "Amsterdam",
  "address": "Main Street 123",
  "latitude": "52.370216",
  "longitude": "4.895168",
  "phone": "+31 20 1234567",
  "email": "clinic@example.com",
  "website": "https://myclinic.com",
  "instagram": "@myclinic",
  "specializations": "Dogs, Cats, Birds",
  "logo": null,
  "is_verified": false,
  "email_confirmed": false,
  "admin_approved": false,
  "is_active_clinic": false,
  "referral_code": null
}
```

**Note:** After registration, a confirmation email is sent. Clinic appears in public listings only after email confirmation AND admin approval.

---

## 3. Get My Clinic

**Endpoint:** `GET /clinics/my/`

**Authentication:** Required

**Request Example:**
```dart
final response = await http.get(
  Uri.parse('https://fammo.ai/api/v1/clinics/my/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
  },
);
```

**Response (200 OK):**
```json
{
  "id": 2,
  "name": "Ibadoyos klinik",
  "slug": "ibadoyos-klinik",
  "city": "Istanbul",
  "address": "Cevizli, 30 Ağustos Cd. No:15, 34846 Maltepe/İstanbul",
  "latitude": "41.006381",
  "longitude": "28.975872",
  "phone": "05523553091",
  "email": "ibadoyos@gmail.com",
  "website": "",
  "instagram": "",
  "specializations": "Köpek ve kedi",
  "working_hours": "",
  "bio": "Ibadoyos Veteriner Kliniği...",
  "logo": "https://fammo.ai/fammo/media/clinic_logos/58f4f779-51d7-4c8f-b4d9-a6bc1d17f61c.jpeg",
  "is_verified": false,
  "clinic_eoi": true,
  "email_confirmed": true,
  "admin_approved": false,
  "is_active_clinic": false,
  "owner_email": "ibadoyos@gmail.com",
  "working_hours_schedule": [
    {
      "id": 8,
      "day_of_week": 0,
      "day_name": "Monday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    }
  ],
  "formatted_working_hours": [
    "Monday: 09:00 - 18:00",
    "Tuesday: 09:00 - 18:00"
  ],
  "vet_profile": {
    "id": 2,
    "vet_name": "Orhan demir",
    "degrees": "",
    "certifications": ""
  },
  "referral_codes": [
    {
      "id": 2,
      "code": "vet-ibadoyoskl",
      "is_active": true,
      "created_at": "2025-11-28T19:22:30.842665Z"
    }
  ],
  "active_referral_code": "vet-ibadoyoskl",
  "created_at": "2025-11-28T19:21:53.208379Z",
  "updated_at": "2025-11-28T19:22:30.830929Z"
}
```

**Response (404 Not Found):**
```json
{
  "error": "You don't have a clinic registered"
}
```

---

## 4. Get Clinic Details

**Endpoint:** `GET /clinics/{id}/`

**Authentication:** Not required

**Request Example:**
```dart
final clinicId = 2;
final response = await http.get(
  Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/'),
);
```

**Response (200 OK):** Same as "Get My Clinic" response

---

## 5. Update Clinic

**Endpoint:** `PUT /clinics/{id}/` or `PATCH /clinics/{id}/`

**Authentication:** Required (must be clinic owner)

**Request Body (PATCH - partial update):**
```json
{
  "bio": "Updated clinic description",
  "phone": "+31 20 9999999",
  "website": "https://newwebsite.com"
}
```

**Request Example:**
```dart
final clinicId = 2;
final response = await http.patch(
  Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode({
    'bio': 'Updated clinic description',
    'phone': '+31 20 9999999',
  }),
);
```

**Updatable Fields:**
- `name`, `city`, `address`, `latitude`, `longitude`
- `phone`, `email`, `website`, `instagram`
- `specializations`, `working_hours`, `bio`
- `logo`, `clinic_eoi`

**Response (200 OK):**
```json
{
  "name": "Ibadoyos klinik",
  "city": "Istanbul",
  "address": "Cevizli, 30 Ağustos Cd. No:15",
  "latitude": "41.006381",
  "longitude": "28.975872",
  "phone": "+31 20 9999999",
  "email": "ibadoyos@gmail.com",
  "website": "https://newwebsite.com",
  "instagram": "",
  "specializations": "Köpek ve kedi",
  "working_hours": "",
  "bio": "Updated clinic description",
  "logo": "https://fammo.ai/fammo/media/clinic_logos/...",
  "clinic_eoi": true
}
```

**Response (403 Forbidden):**
```json
{
  "detail": "You don't have permission to edit this clinic"
}
```

---

## 6. Delete Clinic

**Endpoint:** `DELETE /clinics/{id}/`

**Authentication:** Required (must be clinic owner)

**Request Example:**
```dart
final clinicId = 2;
final response = await http.delete(
  Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
  },
);
```

**Response (204 No Content):** Empty response

**Response (403 Forbidden):**
```json
{
  "detail": "You don't have permission to delete this clinic"
}
```

---

## 7. Get Clinic Working Hours

**Endpoint:** `GET /clinics/{clinic_id}/working-hours/`

**Authentication:** Not required

**Request Example:**
```dart
final clinicId = 2;
final response = await http.get(
  Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/working-hours/'),
);
```

**Response (200 OK):**
```json
[
  {
    "id": 8,
    "day_of_week": 0,
    "day_name": "Monday",
    "is_closed": false,
    "open_time": "09:00:00",
    "close_time": "18:00:00"
  },
  {
    "id": 9,
    "day_of_week": 1,
    "day_name": "Tuesday",
    "is_closed": false,
    "open_time": "09:00:00",
    "close_time": "18:00:00"
  },
  {
    "id": 14,
    "day_of_week": 6,
    "day_name": "Sunday",
    "is_closed": true,
    "open_time": null,
    "close_time": null
  }
]
```

**day_of_week values:**
- 0 = Monday
- 1 = Tuesday
- 2 = Wednesday
- 3 = Thursday
- 4 = Friday
- 5 = Saturday
- 6 = Sunday

---

## 8. Update Clinic Working Hours (Bulk)

**Endpoint:** `POST /clinics/{clinic_id}/working-hours/`

**Authentication:** Required (must be clinic owner)

**Request Body:**
```json
[
  {
    "day_of_week": 0,
    "is_closed": false,
    "open_time": "09:00",
    "close_time": "17:00"
  },
  {
    "day_of_week": 1,
    "is_closed": false,
    "open_time": "09:00",
    "close_time": "17:00"
  },
  {
    "day_of_week": 6,
    "is_closed": true
  }
]
```

**Request Example:**
```dart
final clinicId = 2;
final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/working-hours/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode([
    {
      'day_of_week': 0,
      'is_closed': false,
      'open_time': '09:00',
      'close_time': '17:00',
    },
    {
      'day_of_week': 1,
      'is_closed': false,
      'open_time': '09:00',
      'close_time': '17:00',
    },
    {
      'day_of_week': 6,
      'is_closed': true,
    },
  ]),
);
```

**Time Format:** `"HH:MM"` (24-hour format, e.g., "09:00", "18:30")

**Response (201 Created):**
```json
{
  "success": true,
  "working_hours": [
    {
      "id": 8,
      "day_of_week": 0,
      "day_name": "Monday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "17:00:00"
    },
    {
      "id": 9,
      "day_of_week": 1,
      "day_name": "Tuesday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "17:00:00"
    }
  ]
}
```

**Response (403 Forbidden):**
```json
{
  "error": "You don't have permission to edit this clinic's working hours"
}
```

---

## 9. Get Vet Profile

**Endpoint:** `GET /clinics/{clinic_id}/vet-profile/`

**Authentication:** Not required

**Request Example:**
```dart
final clinicId = 2;
final response = await http.get(
  Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/vet-profile/'),
);
```

**Response (200 OK):**
```json
{
  "id": 2,
  "vet_name": "Orhan demir",
  "degrees": "DVM, PhD",
  "certifications": "Board Certified in Surgery"
}
```

**Response (404 Not Found):**
```json
{
  "error": "No vet profile found for this clinic"
}
```

---

## 10. Update Vet Profile

**Endpoint:** `PUT /clinics/{clinic_id}/vet-profile/` or `PATCH /clinics/{clinic_id}/vet-profile/`

**Authentication:** Required (must be clinic owner)

**Request Body:**
```json
{
  "vet_name": "Dr. Jane Smith",
  "degrees": "DVM, PhD",
  "certifications": "Board Certified in Internal Medicine"
}
```

**Request Example:**
```dart
final clinicId = 2;
final response = await http.put(
  Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/vet-profile/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode({
    'vet_name': 'Dr. Jane Smith',
    'degrees': 'DVM, PhD',
    'certifications': 'Board Certified in Internal Medicine',
  }),
);
```

**Response (200 OK):**
```json
{
  "id": 2,
  "vet_name": "Dr. Jane Smith",
  "degrees": "DVM, PhD",
  "certifications": "Board Certified in Internal Medicine"
}
```

**Note:** If no vet profile exists, it will be created automatically.

---

## 11. Search Clinics

**Endpoint:** `POST /clinics/search/`

**Authentication:** Not required

**Request Body:**
```json
{
  "search": "clinic name or city",
  "latitude": 52.370216,
  "longitude": 4.895168,
  "radius": 50,
  "eoi": true
}
```

**Request Example:**
```dart
final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/clinics/search/'),
  headers: {
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'search': 'Istanbul',
    'latitude': 41.0082,
    'longitude': 28.9784,
    'radius': 50,
  }),
);
```

**Parameters:**
- `search` (optional): Text search in name, city, specializations
- `latitude` (optional): User's latitude
- `longitude` (optional): User's longitude
- `radius` (optional): Search radius in km (default: 50)
- `eoi` (optional): Filter by EOI status (true/false)

**Response (200 OK):**
```json
{
  "count": 1,
  "results": [
    {
      "id": 2,
      "name": "Ibadoyos klinik",
      "slug": "ibadoyos-klinik",
      "city": "Istanbul",
      "address": "Cevizli, 30 Ağustos Cd. No:15",
      "latitude": "41.006381",
      "longitude": "28.975872",
      "phone": "05523553091",
      "email": "ibadoyos@gmail.com",
      "website": "",
      "instagram": "",
      "specializations": "Köpek ve kedi",
      "logo": "https://fammo.ai/fammo/media/clinic_logos/...",
      "is_verified": false,
      "email_confirmed": true,
      "admin_approved": true,
      "is_active_clinic": true,
      "referral_code": "vet-ibadoyoskl"
    }
  ]
}
```

---

## 12. Confirm Clinic Email

**Endpoint:** `GET /clinics/confirm-email/{token}/`

**Authentication:** Not required

**Request Example:**
```dart
final token = 'abc123-token-from-email';
final response = await http.get(
  Uri.parse('https://fammo.ai/api/v1/clinics/confirm-email/$token/'),
);
```

**Response (200 OK):**
```json
{
  "message": "Email confirmed successfully. Your clinic is now pending admin approval.",
  "clinic_id": 2,
  "admin_approved": false
}
```

**Response (404 Not Found):**
```json
{
  "error": "Invalid confirmation token"
}
```

---

## Flutter Model Classes

```dart
class Clinic {
  final int id;
  final String name;
  final String slug;
  final String city;
  final String address;
  final String? latitude;
  final String? longitude;
  final String phone;
  final String email;
  final String? website;
  final String? instagram;
  final String specializations;
  final String? workingHours;
  final String bio;
  final String? logo;
  final bool isVerified;
  final bool emailConfirmed;
  final bool adminApproved;
  final bool isActiveClinic;
  final bool clinicEoi;
  final String? ownerEmail;
  final List<WorkingHoursSchedule>? workingHoursSchedule;
  final List<String>? formattedWorkingHours;
  final VetProfile? vetProfile;
  final List<ReferralCode>? referralCodes;
  final String? activeReferralCode;
  final DateTime createdAt;
  final DateTime updatedAt;

  Clinic({
    required this.id,
    required this.name,
    required this.slug,
    required this.city,
    required this.address,
    this.latitude,
    this.longitude,
    required this.phone,
    required this.email,
    this.website,
    this.instagram,
    required this.specializations,
    this.workingHours,
    required this.bio,
    this.logo,
    required this.isVerified,
    required this.emailConfirmed,
    required this.adminApproved,
    required this.isActiveClinic,
    required this.clinicEoi,
    this.ownerEmail,
    this.workingHoursSchedule,
    this.formattedWorkingHours,
    this.vetProfile,
    this.referralCodes,
    this.activeReferralCode,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Clinic.fromJson(Map<String, dynamic> json) {
    return Clinic(
      id: json['id'],
      name: json['name'],
      slug: json['slug'],
      city: json['city'] ?? '',
      address: json['address'] ?? '',
      latitude: json['latitude'],
      longitude: json['longitude'],
      phone: json['phone'] ?? '',
      email: json['email'] ?? '',
      website: json['website'],
      instagram: json['instagram'],
      specializations: json['specializations'] ?? '',
      workingHours: json['working_hours'],
      bio: json['bio'] ?? '',
      logo: json['logo'],
      isVerified: json['is_verified'] ?? false,
      emailConfirmed: json['email_confirmed'] ?? false,
      adminApproved: json['admin_approved'] ?? false,
      isActiveClinic: json['is_active_clinic'] ?? false,
      clinicEoi: json['clinic_eoi'] ?? false,
      ownerEmail: json['owner_email'],
      workingHoursSchedule: json['working_hours_schedule'] != null
          ? (json['working_hours_schedule'] as List)
              .map((e) => WorkingHoursSchedule.fromJson(e))
              .toList()
          : null,
      formattedWorkingHours: json['formatted_working_hours'] != null
          ? List<String>.from(json['formatted_working_hours'])
          : null,
      vetProfile: json['vet_profile'] != null
          ? VetProfile.fromJson(json['vet_profile'])
          : null,
      referralCodes: json['referral_codes'] != null
          ? (json['referral_codes'] as List)
              .map((e) => ReferralCode.fromJson(e))
              .toList()
          : null,
      activeReferralCode: json['active_referral_code'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'city': city,
      'address': address,
      'latitude': latitude,
      'longitude': longitude,
      'phone': phone,
      'email': email,
      'website': website,
      'instagram': instagram,
      'specializations': specializations,
      'working_hours': workingHours,
      'bio': bio,
      'clinic_eoi': clinicEoi,
    };
  }
}

class WorkingHoursSchedule {
  final int id;
  final int dayOfWeek;
  final String dayName;
  final bool isClosed;
  final String? openTime;
  final String? closeTime;

  WorkingHoursSchedule({
    required this.id,
    required this.dayOfWeek,
    required this.dayName,
    required this.isClosed,
    this.openTime,
    this.closeTime,
  });

  factory WorkingHoursSchedule.fromJson(Map<String, dynamic> json) {
    return WorkingHoursSchedule(
      id: json['id'],
      dayOfWeek: json['day_of_week'],
      dayName: json['day_name'],
      isClosed: json['is_closed'],
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
  final String vetName;
  final String degrees;
  final String certifications;

  VetProfile({
    required this.id,
    required this.vetName,
    required this.degrees,
    required this.certifications,
  });

  factory VetProfile.fromJson(Map<String, dynamic> json) {
    return VetProfile(
      id: json['id'],
      vetName: json['vet_name'],
      degrees: json['degrees'] ?? '',
      certifications: json['certifications'] ?? '',
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

class ReferralCode {
  final int id;
  final String code;
  final bool isActive;
  final DateTime createdAt;

  ReferralCode({
    required this.id,
    required this.code,
    required this.isActive,
    required this.createdAt,
  });

  factory ReferralCode.fromJson(Map<String, dynamic> json) {
    return ReferralCode(
      id: json['id'],
      code: json['code'],
      isActive: json['is_active'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
```

---

## Error Responses

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

**403 Forbidden:**
```json
{
  "detail": "You don't have permission to perform this action."
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```
