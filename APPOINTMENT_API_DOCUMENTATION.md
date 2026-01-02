# 📅 FAMMO Appointment API Documentation

**Base URL:** `https://fammo.ai/api/v1/`

---

## 🌍 Multi-Language Support

The API supports multiple languages. To get responses in a specific language, add the `Accept-Language` header:

| Language | Header Value |
|----------|--------------|
| English | `en` |
| Turkish | `tr` |
| Dutch | `nl` |
| Finnish | `fi` |

**Example Header:**
```
Accept-Language: tr
```

**Translated Fields:**
- Appointment Reason `name` and `description` are translated based on the language header.

**Example Response (Turkish):**
```json
{
    "id": 1,
    "name": "Yıllık Sağlık Kontrolü",
    "description": "Rutin yıllık muayene"
}
```

**Example Response (English - default):**
```json
{
    "id": 1,
    "name": "Annual Wellness Exam",
    "description": "Routine yearly checkup"
}
```

> **Note:** If no `Accept-Language` header is provided, English (`en`) is used as the default fallback language.

---

## 🔐 Authentication

All endpoints (except `Appointment Reasons`) require JWT Bearer token authentication.

### Login / Get Token

```
POST https://fammo.ai/api/v1/auth/token/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "user@example.com",
    "password": "yourpassword"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Use in all subsequent requests:**
```
Authorization: Bearer <access_token>
```

---

# 👤 USER SIDE ENDPOINTS

## 1. Get Appointment Reasons

Get list of available appointment reasons for booking.

```
GET https://fammo.ai/api/v1/appointments/reasons/
```

**Headers:**
```
Content-Type: application/json
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "Annual Wellness Exam",
        "description": "Routine yearly checkup"
    },
    {
        "id": 2,
        "name": "Behavior Consultation",
        "description": "Anxiety or aggression issues"
    },
    {
        "id": 3,
        "name": "Dental Checkup",
        "description": "Oral health examination"
    },
    {
        "id": 4,
        "name": "Dental Cleaning",
        "description": "Professional teeth cleaning"
    },
    {
        "id": 5,
        "name": "Deworming",
        "description": "Internal parasite treatment"
    },
    {
        "id": 6,
        "name": "Digestive Issues",
        "description": "Vomiting, diarrhea, or loss of appetite"
    },
    {
        "id": 7,
        "name": "Ear Infection",
        "description": "Scratching, odor, or head shaking"
    },
    {
        "id": 8,
        "name": "Emergency / Urgent Care",
        "description": "Acute illness or injury"
    },
    {
        "id": 9,
        "name": "Eye Problems",
        "description": "Discharge, redness, or cloudiness"
    },
    {
        "id": 10,
        "name": "Flea & Tick Prevention",
        "description": "Preventive treatment consultation"
    },
    {
        "id": 11,
        "name": "Follow-up Visit",
        "description": "Post-treatment checkup"
    },
    {
        "id": 12,
        "name": "Grooming Services",
        "description": "Professional grooming if offered"
    },
    {
        "id": 13,
        "name": "Health Certificate",
        "description": "Official travel documentation"
    },
    {
        "id": 14,
        "name": "Laboratory Tests",
        "description": "Blood work and urinalysis"
    },
    {
        "id": 15,
        "name": "Limping / Mobility Issues",
        "description": "Joint pain or difficulty walking"
    },
    {
        "id": 16,
        "name": "Microchipping",
        "description": "Permanent identification implant"
    },
    {
        "id": 17,
        "name": "Nutrition Consultation",
        "description": "Diet and weight management"
    },
    {
        "id": 18,
        "name": "Pregnancy Checkup",
        "description": "Prenatal care"
    },
    {
        "id": 19,
        "name": "Preventive Care",
        "description": "General health and prevention services"
    },
    {
        "id": 20,
        "name": "Puppy / Kitten Checkup",
        "description": "Initial examination for young pets"
    },
    {
        "id": 21,
        "name": "Respiratory Problems",
        "description": "Coughing, sneezing, or breathing difficulty"
    },
    {
        "id": 22,
        "name": "Senior Pet Wellness",
        "description": "Geriatric health assessment"
    },
    {
        "id": 23,
        "name": "Skin Problems",
        "description": "Itching, rashes, hair loss, and allergies"
    },
    {
        "id": 24,
        "name": "Spay / Neuter",
        "description": "Sterilization surgery"
    },
    {
        "id": 25,
        "name": "Tooth Extraction",
        "description": "Removal of damaged teeth"
    },
    {
        "id": 26,
        "name": "Travel / Passport Preparation",
        "description": "Documents and health checks for traveling abroad"
    },
    {
        "id": 27,
        "name": "Tumor Removal",
        "description": "Growth or mass removal"
    },
    {
        "id": 28,
        "name": "Urinary Issues",
        "description": "Frequent urination, blood in urine, or straining"
    },
    {
        "id": 29,
        "name": "Vaccination",
        "description": "Core vaccines such as rabies, distemper, and parvovirus"
    },
    {
        "id": 30,
        "name": "Wound Treatment",
        "description": "Cuts, bite wounds, or injuries"
    }
]
```

---

## 2. Get Available Dates for Clinic

Get dates when clinic is open for the next N days.

```
GET https://fammo.ai/api/v1/clinics/{clinic_id}/available-dates/
```

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | string | No | today | Start date (YYYY-MM-DD) |
| `days` | integer | No | 14 | Number of days to check (max 60) |

**Example:**
```
GET https://fammo.ai/api/v1/clinics/2/available-dates/?start_date=2026-01-02&days=14
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "clinic_id": 2,
    "clinic_name": "Ibadoyos klinik",
    "available_dates": [
        {
            "date": "2026-01-02",
            "day_name": "Friday",
            "open_time": "09:00",
            "close_time": "18:00"
        },
        {
            "date": "2026-01-03",
            "day_name": "Saturday",
            "open_time": "09:00",
            "close_time": "14:00"
        },
        {
            "date": "2026-01-06",
            "day_name": "Tuesday",
            "open_time": "09:00",
            "close_time": "18:00"
        }
    ]
}
```

---

## 3. Get Available Time Slots

Get available time slots for a specific date.

```
GET https://fammo.ai/api/v1/clinics/{clinic_id}/available-slots/
```

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `date` | string | **Yes** | - | Date to check (YYYY-MM-DD) |
| `duration` | integer | No | 30 | Appointment duration in minutes |

**Example:**
```
GET https://fammo.ai/api/v1/clinics/2/available-slots/?date=2026-01-02&duration=30
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "date": "2026-01-02",
    "is_open": true,
    "slots": [
        "09:00",
        "09:30",
        "10:00",
        "10:30",
        "11:00",
        "11:30",
        "12:00",
        "12:30",
        "14:00",
        "14:30",
        "15:00",
        "15:30",
        "16:00",
        "16:30",
        "17:00",
        "17:30"
    ],
    "working_hours": {
        "open_time": "09:00",
        "close_time": "18:00"
    }
}
```

**Response if clinic is closed (200 OK):**
```json
{
    "date": "2026-01-05",
    "is_open": false,
    "slots": [],
    "working_hours": null
}
```

---

## 4. Create Appointment

Book a new appointment at a clinic.

```
POST https://fammo.ai/api/v1/appointments/create/
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "clinic": 2,
    "pet": 1,
    "appointment_date": "2026-01-02",
    "appointment_time": "10:00",
    "reason": 1,
    "reason_text": "Annual checkup for my cat",
    "notes": "Please check the ears, they seem itchy"
}
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `clinic` | integer | **Yes** | Clinic ID |
| `pet` | integer | **Yes** | Pet ID (must belong to user) |
| `appointment_date` | string | **Yes** | Date (YYYY-MM-DD) |
| `appointment_time` | string | **Yes** | Time (HH:MM) |
| `reason` | integer | No | AppointmentReason ID |
| `reason_text` | string | No | Custom reason description |
| `notes` | string | No | Additional notes for the clinic |

**Response (201 Created):**
```json
{
    "id": 5,
    "reference_code": "APT-X7K2MNPQ",
    "clinic": 2,
    "pet": 1,
    "appointment_date": "2026-01-02",
    "appointment_time": "10:00:00",
    "duration_minutes": 30,
    "reason": 1,
    "reason_text": "Annual checkup for my cat",
    "notes": "Please check the ears, they seem itchy",
    "status": "PENDING",
    "created_at": "2026-01-01T15:30:00.000000Z"
}
```

**Error Response (400 Bad Request):**
```json
{
    "appointment_time": [
        "This time slot is already booked. Please choose another time."
    ]
}
```

---

## 5. List My Appointments

Get list of user's appointments.

```
GET https://fammo.ai/api/v1/appointments/
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status (PENDING, CONFIRMED, CANCELLED_USER, CANCELLED_CLINIC, COMPLETED, NO_SHOW) |
| `upcoming` | boolean | No | Set `true` to show only upcoming appointments |
| `pet` | integer | No | Filter by pet ID |

**Examples:**
```
GET https://fammo.ai/api/v1/appointments/
GET https://fammo.ai/api/v1/appointments/?status=PENDING
GET https://fammo.ai/api/v1/appointments/?upcoming=true
GET https://fammo.ai/api/v1/appointments/?pet=1
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "reference_code": "APT-4DMFFGPN",
        "pet_name": "Nani",
        "pet_type": "Cat",
        "clinic_name": "Ibadoyos klinik",
        "clinic_address": "62, Merkez, Kemerburgaz Cd. No:25, 34403 Kağıthane/İstanbul",
        "appointment_date": "2026-01-01",
        "appointment_time": "13:30:00",
        "duration_minutes": 30,
        "reason_name": "Annual Wellness Exam",
        "reason_text": "Nani don't drink more water",
        "status": "CONFIRMED",
        "status_display": "Confirmed",
        "is_upcoming": false,
        "can_cancel": false,
        "created_at": "2025-12-31T17:12:51.825753Z"
    },
    {
        "id": 2,
        "reference_code": "APT-K9MN2XPQ",
        "pet_name": "Buddy",
        "pet_type": "Dog",
        "clinic_name": "Happy Paws Clinic",
        "clinic_address": "123 Main Street, Istanbul",
        "appointment_date": "2026-01-05",
        "appointment_time": "14:00:00",
        "duration_minutes": 30,
        "reason_name": "Vaccination",
        "reason_text": "Annual vaccination",
        "status": "PENDING",
        "status_display": "Pending",
        "is_upcoming": true,
        "can_cancel": true,
        "created_at": "2026-01-01T10:00:00.000000Z"
    }
]
```

---

## 6. Get Appointment Details

Get detailed information about a specific appointment.

```
GET https://fammo.ai/api/v1/appointments/{id}/
```

**Example:**
```
GET https://fammo.ai/api/v1/appointments/1/
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "reference_code": "APT-4DMFFGPN",
    "pet": {
        "id": 1,
        "name": "Nani",
        "pet_type": "Cat",
        "breed": "British Shorthair",
        "image": "https://fammo.ai/fammo/media/pet_images/scaled_1000051104.jpg"
    },
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "00905522340731"
    },
    "clinic": {
        "id": 2,
        "name": "Ibadoyos klinik",
        "slug": "ibadoyos-klinik",
        "city": "Istanbul",
        "address": "62, Merkez, Kemerburgaz Cd. No:25, 34403 Kağıthane/İstanbul",
        "latitude": "41.094900",
        "longitude": "28.948780",
        "phone": "+905522340731",
        "email": "clinic@example.com",
        "website": "https://www.example.com",
        "instagram": "clinic_instagram",
        "specializations": "Dogs and Cats",
        "logo": "https://fammo.ai/fammo/media/clinic_logos/logo.jpg",
        "is_verified": false,
        "email_confirmed": true,
        "admin_approved": false,
        "is_active_clinic": false,
        "referral_code": "vet-ibadoyoskl"
    },
    "appointment_date": "2026-01-01",
    "appointment_time": "13:30:00",
    "duration_minutes": 30,
    "reason": {
        "id": 1,
        "name": "Annual Wellness Exam",
        "description": "Routine yearly checkup"
    },
    "reason_text": "Nani don't drink more water",
    "notes": "Don't drink more water",
    "status": "CONFIRMED",
    "status_display": "Confirmed",
    "is_upcoming": false,
    "can_cancel": false,
    "confirmed_at": "2025-12-31T17:14:15.184310Z",
    "cancelled_at": null,
    "cancellation_reason": "",
    "created_at": "2025-12-31T17:12:51.825753Z",
    "updated_at": "2025-12-31T17:14:15.184710Z"
}
```

---

## 7. Cancel Appointment

Cancel a user's appointment.

```
POST https://fammo.ai/api/v1/appointments/{id}/cancel/
```

**Example:**
```
POST https://fammo.ai/api/v1/appointments/2/cancel/
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "cancellation_reason": "Change of plans"
}
```

**Response (200 OK):**
```json
{
    "message": "Appointment cancelled successfully."
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "This appointment cannot be cancelled."
}
```

---

# 🏥 CLINIC SIDE ENDPOINTS

## 1. List Clinic Appointments

Get list of appointments for the clinic owner.

```
GET https://fammo.ai/api/v1/clinics/my/appointments/
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status (PENDING, CONFIRMED, CANCELLED_USER, CANCELLED_CLINIC, COMPLETED, NO_SHOW) |
| `date` | string | No | Filter by specific date (YYYY-MM-DD) |
| `upcoming` | boolean | No | Set `true` to show only upcoming appointments |

**Examples:**
```
GET https://fammo.ai/api/v1/clinics/my/appointments/
GET https://fammo.ai/api/v1/clinics/my/appointments/?status=PENDING
GET https://fammo.ai/api/v1/clinics/my/appointments/?date=2026-01-02
GET https://fammo.ai/api/v1/clinics/my/appointments/?upcoming=true
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "reference_code": "APT-4DMFFGPN",
        "pet": {
            "id": 1,
            "name": "Nani",
            "pet_type": "Cat",
            "breed": "British Shorthair",
            "image": "https://fammo.ai/fammo/media/pet_images/scaled_1000051104.jpg"
        },
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "00905522340731"
        },
        "appointment_date": "2026-01-01",
        "appointment_time": "13:30:00",
        "duration_minutes": 30,
        "reason": {
            "id": 1,
            "name": "Annual Wellness Exam",
            "description": "Routine yearly checkup"
        },
        "reason_text": "Nani don't drink more water",
        "notes": "Don't drink more water",
        "status": "PENDING",
        "status_display": "Pending",
        "confirmed_at": null,
        "created_at": "2025-12-31T17:12:51.825753Z"
    },
    {
        "id": 2,
        "reference_code": "APT-K9MN2XPQ",
        "pet": {
            "id": 2,
            "name": "Buddy",
            "pet_type": "Dog",
            "breed": "Golden Retriever",
            "image": "https://fammo.ai/fammo/media/pet_images/buddy.jpg"
        },
        "user": {
            "id": 3,
            "email": "owner@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "00905551234567"
        },
        "appointment_date": "2026-01-02",
        "appointment_time": "10:00:00",
        "duration_minutes": 30,
        "reason": {
            "id": 29,
            "name": "Vaccination",
            "description": "Core vaccines such as rabies, distemper, and parvovirus"
        },
        "reason_text": "Annual vaccination",
        "notes": "",
        "status": "CONFIRMED",
        "status_display": "Confirmed",
        "confirmed_at": "2026-01-01T08:00:00.000000Z",
        "created_at": "2025-12-30T10:00:00.000000Z"
    }
]
```

---

## 2. Get Clinic Appointment Details

Get detailed information about a specific appointment for clinic.

```
GET https://fammo.ai/api/v1/clinics/my/appointments/{id}/
```

**Example:**
```
GET https://fammo.ai/api/v1/clinics/my/appointments/1/
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "reference_code": "APT-4DMFFGPN",
    "pet": {
        "id": 1,
        "name": "Nani",
        "pet_type": "Cat",
        "breed": "British Shorthair",
        "image": "https://fammo.ai/fammo/media/pet_images/scaled_1000051104.jpg"
    },
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "00905522340731"
    },
    "appointment_date": "2026-01-01",
    "appointment_time": "13:30:00",
    "duration_minutes": 30,
    "reason": {
        "id": 1,
        "name": "Annual Wellness Exam",
        "description": "Routine yearly checkup"
    },
    "reason_text": "Nani don't drink more water",
    "notes": "Don't drink more water",
    "status": "PENDING",
    "status_display": "Pending",
    "confirmed_at": null,
    "created_at": "2025-12-31T17:12:51.825753Z"
}
```

---

## 3. Confirm Appointment

Confirm a pending appointment.

```
PATCH https://fammo.ai/api/v1/clinics/my/appointments/{id}/update/
```

**Example:**
```
PATCH https://fammo.ai/api/v1/clinics/my/appointments/1/update/
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "status": "CONFIRMED"
}
```

**Response (200 OK):**
```json
{
    "message": "Appointment status updated to Confirmed",
    "appointment": {
        "id": 1,
        "reference_code": "APT-4DMFFGPN",
        "pet": {
            "id": 1,
            "name": "Nani",
            "pet_type": "Cat",
            "breed": "British Shorthair",
            "image": "https://fammo.ai/fammo/media/pet_images/scaled_1000051104.jpg"
        },
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "00905522340731"
        },
        "appointment_date": "2026-01-01",
        "appointment_time": "13:30:00",
        "duration_minutes": 30,
        "reason": {
            "id": 1,
            "name": "Annual Wellness Exam",
            "description": "Routine yearly checkup"
        },
        "reason_text": "Nani don't drink more water",
        "notes": "Don't drink more water",
        "status": "CONFIRMED",
        "status_display": "Confirmed",
        "confirmed_at": "2026-01-01T12:00:00.000000Z",
        "created_at": "2025-12-31T17:12:51.825753Z"
    }
}
```

---

## 4. Cancel Appointment (by Clinic)

Cancel an appointment as clinic owner.

```
PATCH https://fammo.ai/api/v1/clinics/my/appointments/{id}/update/
```

**Example:**
```
PATCH https://fammo.ai/api/v1/clinics/my/appointments/1/update/
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "status": "CANCELLED_CLINIC",
    "cancellation_reason": "Clinic closed due to emergency"
}
```

**Response (200 OK):**
```json
{
    "message": "Appointment status updated to Cancelled by Clinic",
    "appointment": {
        "id": 1,
        "reference_code": "APT-4DMFFGPN",
        "pet": {
            "id": 1,
            "name": "Nani",
            "pet_type": "Cat",
            "breed": "British Shorthair",
            "image": "https://fammo.ai/fammo/media/pet_images/scaled_1000051104.jpg"
        },
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "00905522340731"
        },
        "appointment_date": "2026-01-01",
        "appointment_time": "13:30:00",
        "duration_minutes": 30,
        "reason": {
            "id": 1,
            "name": "Annual Wellness Exam",
            "description": "Routine yearly checkup"
        },
        "reason_text": "Nani don't drink more water",
        "notes": "Don't drink more water",
        "status": "CANCELLED_CLINIC",
        "status_display": "Cancelled by Clinic",
        "confirmed_at": null,
        "created_at": "2025-12-31T17:12:51.825753Z"
    }
}
```

---

## 5. Mark Appointment as Completed

Mark an appointment as completed after the visit.

```
PATCH https://fammo.ai/api/v1/clinics/my/appointments/{id}/update/
```

**Example:**
```
PATCH https://fammo.ai/api/v1/clinics/my/appointments/1/update/
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "status": "COMPLETED"
}
```

**Response (200 OK):**
```json
{
    "message": "Appointment status updated to Completed",
    "appointment": {
        "id": 1,
        "reference_code": "APT-4DMFFGPN",
        "pet": {
            "id": 1,
            "name": "Nani",
            "pet_type": "Cat",
            "breed": "British Shorthair",
            "image": "https://fammo.ai/fammo/media/pet_images/scaled_1000051104.jpg"
        },
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "00905522340731"
        },
        "appointment_date": "2026-01-01",
        "appointment_time": "13:30:00",
        "duration_minutes": 30,
        "reason": {
            "id": 1,
            "name": "Annual Wellness Exam",
            "description": "Routine yearly checkup"
        },
        "reason_text": "Nani don't drink more water",
        "notes": "Don't drink more water",
        "status": "COMPLETED",
        "status_display": "Completed",
        "confirmed_at": "2025-12-31T17:14:15.184310Z",
        "created_at": "2025-12-31T17:12:51.825753Z"
    }
}
```

---

## 6. Mark Appointment as No-Show

Mark an appointment when the user didn't show up.

```
PATCH https://fammo.ai/api/v1/clinics/my/appointments/{id}/update/
```

**Example:**
```
PATCH https://fammo.ai/api/v1/clinics/my/appointments/1/update/
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "status": "NO_SHOW"
}
```

**Response (200 OK):**
```json
{
    "message": "Appointment status updated to No Show",
    "appointment": {
        "id": 1,
        "reference_code": "APT-4DMFFGPN",
        "pet": {
            "id": 1,
            "name": "Nani",
            "pet_type": "Cat",
            "breed": "British Shorthair",
            "image": "https://fammo.ai/fammo/media/pet_images/scaled_1000051104.jpg"
        },
        "user": {
            "id": 1,
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "00905522340731"
        },
        "appointment_date": "2026-01-01",
        "appointment_time": "13:30:00",
        "duration_minutes": 30,
        "reason": {
            "id": 1,
            "name": "Annual Wellness Exam",
            "description": "Routine yearly checkup"
        },
        "reason_text": "Nani don't drink more water",
        "notes": "Don't drink more water",
        "status": "NO_SHOW",
        "status_display": "No Show",
        "confirmed_at": "2025-12-31T17:14:15.184310Z",
        "created_at": "2025-12-31T17:12:51.825753Z"
    }
}
```

---

# 📊 Reference Tables

## Appointment Status Values

| Status | Value | Description |
|--------|-------|-------------|
| Pending | `PENDING` | New appointment waiting for clinic confirmation |
| Confirmed | `CONFIRMED` | Clinic has confirmed the appointment |
| Cancelled by User | `CANCELLED_USER` | Pet owner cancelled the appointment |
| Cancelled by Clinic | `CANCELLED_CLINIC` | Clinic cancelled the appointment |
| Completed | `COMPLETED` | Appointment visit is completed |
| No Show | `NO_SHOW` | Pet owner didn't show up for the appointment |

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created (for new appointments) |
| 400 | Bad Request (validation errors) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (not allowed) |
| 404 | Not Found |

---

## Flutter Data Models

### AppointmentReason
```dart
class AppointmentReason {
  final int id;
  final String name;
  final String description;
}
```

### AppointmentListItem
```dart
class AppointmentListItem {
  final int id;
  final String referenceCode;
  final String petName;
  final String petType;
  final String clinicName;
  final String clinicAddress;
  final String appointmentDate;
  final String appointmentTime;
  final int durationMinutes;
  final String? reasonName;
  final String? reasonText;
  final String status;
  final String statusDisplay;
  final bool isUpcoming;
  final bool canCancel;
  final DateTime createdAt;
}
```

### AppointmentDetail
```dart
class AppointmentDetail {
  final int id;
  final String referenceCode;
  final Pet pet;
  final User user;
  final Clinic clinic;
  final String appointmentDate;
  final String appointmentTime;
  final int durationMinutes;
  final AppointmentReason? reason;
  final String? reasonText;
  final String? notes;
  final String status;
  final String statusDisplay;
  final bool isUpcoming;
  final bool canCancel;
  final DateTime? confirmedAt;
  final DateTime? cancelledAt;
  final String cancellationReason;
  final DateTime createdAt;
  final DateTime updatedAt;
}
```

### Pet
```dart
class Pet {
  final int id;
  final String name;
  final String? petType;
  final String? breed;
  final String? image;
}
```

### User
```dart
class User {
  final int id;
  final String email;
  final String firstName;
  final String lastName;
  final String phone;
}
```

### Clinic
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
  final String website;
  final String instagram;
  final String specializations;
  final String? logo;
  final bool isVerified;
  final bool emailConfirmed;
  final bool adminApproved;
  final bool isActiveClinic;
  final String? referralCode;
}
```

---

## Quick Endpoint Summary

### User Endpoints
| Action | Method | Endpoint |
|--------|--------|----------|
| Get Reasons | GET | `/appointments/reasons/` |
| Get Available Dates | GET | `/clinics/{id}/available-dates/` |
| Get Available Slots | GET | `/clinics/{id}/available-slots/?date=YYYY-MM-DD` |
| Create Appointment | POST | `/appointments/create/` |
| List My Appointments | GET | `/appointments/` |
| Get Appointment Detail | GET | `/appointments/{id}/` |
| Cancel Appointment | POST | `/appointments/{id}/cancel/` |

### Clinic Endpoints
| Action | Method | Endpoint |
|--------|--------|----------|
| List Clinic Appointments | GET | `/clinics/my/appointments/` |
| Get Appointment Detail | GET | `/clinics/my/appointments/{id}/` |
| Update Status | PATCH | `/clinics/my/appointments/{id}/update/` |
