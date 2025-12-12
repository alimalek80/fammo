# Backend API Architecture & Data Flow Documentation

## Executive Summary

This document provides a comprehensive overview of the RESTful API backend architecture designed for a multi-platform pet care and veterinary services application. The system is built using Django REST Framework and follows industry best practices for scalability, security, and maintainability.

**Technology Stack:**
- Framework: Django 4.x with Django REST Framework
- Database: PostgreSQL/SQLite
- Authentication: JWT (JSON Web Tokens)
- AI Integration: OpenAI API with structured outputs
- Multi-language Support: Django Modeltranslation
- Geolocation: Integrated geocoding services

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Applications                         │
│  (Flutter Mobile App, Web Dashboard, Future Platforms)          │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTPS/REST API
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                             │
│  - JWT Authentication                                            │
│  - Request Validation                                            │
│  - Rate Limiting                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ User Module  │  │  Pet Module  │  │ Clinic Module│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  AI Module   │  │ Auth Module  │  │ Legal Module │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                    │
│  - Relational Database (PostgreSQL)                              │
│  - Media Storage (Files/Images)                                  │
│  - Caching Layer (Future)                                        │
└─────────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 External Services                                │
│  - OpenAI API (AI Recommendations)                               │
│  - Email Service (SMTP)                                          │
│  - Geocoding Service                                             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Architectural Principles

1. **RESTful Design**: All endpoints follow REST conventions with proper HTTP methods
2. **Stateless Communication**: JWT tokens for authentication without server-side sessions
3. **Separation of Concerns**: Modular architecture with distinct apps for different domains
4. **Security First**: Authentication, authorization, and data validation at every layer
5. **Scalability**: Designed for horizontal scaling with minimal state dependency
6. **API Versioning**: Prepared for future version management

---

## 2. Core Modules & Functionality

### 2.1 User Management Module

**Purpose**: Handle user registration, authentication, profile management, and language preferences.

**Data Models:**

```python
CustomUser (Authentication)
├── email (unique identifier)
├── password (hashed)
├── is_active (email verification status)
├── is_staff (admin access)
└── date_joined

Profile (User Details)
├── user (OneToOne → CustomUser)
├── first_name, last_name
├── phone, address, city, zip_code, country
├── latitude, longitude (location data)
├── location_consent (privacy compliance)
├── preferred_language (en, fi, nl, tr)
├── subscription_plan (→ SubscriptionPlan)
└── is_writer (content creator flag)
```

**Key API Endpoints:**

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/api/auth/signup/` | POST | None | Register new user account |
| `/api/auth/token/` | POST | None | Obtain JWT access/refresh tokens |
| `/api/auth/token/refresh/` | POST | None | Refresh expired access token |
| `/api/auth/forgot-password/` | POST | None | Request password reset email |
| `/api/auth/reset-password/` | POST | None | Reset password with token |
| `/api/auth/change-password/` | POST | Required | Change password (authenticated) |
| `/api/me/` | GET/PATCH | Required | Retrieve/update user profile |
| `/api/me/language/` | GET/POST | Required | Get/set language preference |

**Authentication Flow:**

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │         │   API    │         │ Database │
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                     │
     │ 1. POST /signup    │                     │
     ├───────────────────>│                     │
     │                    │ 2. Validate data    │
     │                    ├────────────────────>│
     │                    │ 3. Create user      │
     │                    │    (is_active=False)│
     │                    │<────────────────────┤
     │                    │ 4. Send email       │
     │                    │    verification     │
     │ 5. Response        │                     │
     │<───────────────────┤                     │
     │                    │                     │
     │ 6. User clicks     │                     │
     │    email link      │                     │
     │                    │                     │
     │ 7. POST /token     │                     │
     ├───────────────────>│ 8. Verify creds    │
     │                    ├────────────────────>│
     │                    │ 9. Return user      │
     │                    │<────────────────────┤
     │ 10. JWT tokens     │                     │
     │<───────────────────┤                     │
     │                    │                     │
```

**Sample Request/Response:**

```json
// POST /api/auth/signup/
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}

Response: 201 Created
{
  "success": true,
  "message": "Registration successful. Please check your email to activate your account.",
  "user": {
    "id": 42,
    "email": "user@example.com"
  }
}

// POST /api/auth/token/
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2.2 Pet Management Module

**Purpose**: Comprehensive pet profile management with detailed health, nutrition, and behavioral data.

**Data Models:**

```python
Pet (Core Entity)
├── user (ForeignKey → CustomUser)
├── name, image
├── pet_type (→ PetType: Dog, Cat)
├── breed (→ Breed)
├── gender (→ Gender)
├── birth_date, age_years, age_months, age_weeks
├── age_category (→ AgeCategory: Puppy, Adult, Senior)
├── neutered (boolean)
├── weight (decimal)
├── body_type (→ BodyType)
├── activity_level (→ ActivityLevel)
├── food_types (ManyToMany → FoodType)
├── food_feeling (→ FoodFeeling)
├── food_importance (→ FoodImportance)
├── food_allergies (ManyToMany → FoodAllergy)
├── food_allergy_other (text)
├── health_issues (ManyToMany → HealthIssue)
└── treat_frequency (→ TreatFrequency)

Supporting Models (Reference Data):
- PetType, Gender, Breed
- AgeCategory, BodyType, ActivityLevel
- FoodType, FoodFeeling, FoodImportance
- FoodAllergy, HealthIssue, TreatFrequency
```

**Key API Endpoints:**

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/api/pets/` | GET | Required | List all user's pets |
| `/api/pets/` | POST | Required | Create new pet profile |
| `/api/pets/{id}/` | GET | Required | Retrieve specific pet details |
| `/api/pets/{id}/` | PATCH/PUT | Required | Update pet information |
| `/api/pets/{id}/` | DELETE | Required | Delete pet profile |
| `/api/pet-types/` | GET | Required | List available pet types |
| `/api/genders/` | GET | Required | List available genders |
| `/api/breeds/?pet_type={id}` | GET | Required | List breeds (filtered by type) |
| `/api/age-categories/?pet_type={id}` | GET | Required | List age categories |
| `/api/food-types/` | GET | Required | List food types |
| `/api/food-allergies/` | GET | Required | List food allergies |
| `/api/health-issues/` | GET | Required | List health issues |
| `/api/body-types/` | GET | Required | List body types |
| `/api/activity-levels/` | GET | Required | List activity levels |

**Data Flow: Creating a Pet Profile**

```
┌────────────┐       ┌────────────┐       ┌────────────┐
│   Client   │       │  API Layer │       │  Database  │
└──────┬─────┘       └──────┬─────┘       └──────┬─────┘
       │                    │                     │
       │ 1. GET reference   │                     │
       │    data endpoints  │                     │
       ├───────────────────>│                     │
       │                    │ 2. Query options    │
       │                    ├────────────────────>│
       │ 3. Form options    │                     │
       │<───────────────────┤                     │
       │                    │                     │
       │ 4. POST /pets/     │                     │
       │    with pet data   │                     │
       ├───────────────────>│                     │
       │                    │ 5. Validate data    │
       │                    │ 6. Create pet       │
       │                    ├────────────────────>│
       │                    │ 7. Pet created      │
       │                    │<────────────────────┤
       │ 8. Pet details     │                     │
       │    with nested     │                     │
       │    objects         │                     │
       │<───────────────────┤                     │
       │                    │                     │
```

**Sample Request/Response:**

```json
// POST /api/pets/
Request:
{
  "name": "Max",
  "pet_type": 1,
  "breed": 15,
  "gender": 1,
  "birth_date": "2020-05-15",
  "neutered": true,
  "weight": 25.5,
  "body_type": 2,
  "activity_level": 3,
  "food_types": [1, 2],
  "food_allergies": [3, 5],
  "health_issues": []
}

Response: 201 Created
{
  "id": 123,
  "name": "Max",
  "image": null,
  "neutered": true,
  "birth_date": "2020-05-15",
  "age_years": 4,
  "age_months": 6,
  "age_weeks": null,
  "age_display": "4 years",
  "weight": "25.50",
  "pet_type": 1,
  "pet_type_detail": {
    "id": 1,
    "name": "Dog"
  },
  "breed": 15,
  "breed_detail": {
    "id": 15,
    "name": "Golden Retriever",
    "pet_type": {
      "id": 1,
      "name": "Dog"
    }
  },
  "gender": 1,
  "gender_detail": {
    "id": 1,
    "name": "Male"
  },
  "body_type": 2,
  "body_type_detail": {
    "id": 2,
    "name": "Ideal",
    "description": "Well-proportioned body shape"
  },
  "activity_level": 3,
  "activity_level_detail": {
    "id": 3,
    "name": "High",
    "description": "Very active, needs lots of exercise"
  },
  "food_types": [1, 2],
  "food_types_detail": [
    {"id": 1, "name": "Dry Food"},
    {"id": 2, "name": "Wet Food"}
  ],
  "food_allergies": [3, 5],
  "food_allergies_detail": [
    {"id": 3, "name": "Chicken"},
    {"id": 5, "name": "Wheat"}
  ],
  "health_issues": [],
  "health_issues_detail": [],
  "user": 42
}
```

**Multi-language Support:**

All reference data (PetType, Breed, AgeCategory, etc.) supports multiple languages through Django Modeltranslation:

```json
// GET /api/breeds/5/
// With Accept-Language: fi header
{
  "id": 5,
  "name": "Kultainennoutaja",  // Finnish translation
  "name_en": "Golden Retriever",
  "name_fi": "Kultainennoutaja",
  "name_nl": "Gouden Retriever",
  "name_tr": "Golden Retriever",
  "pet_type": {
    "id": 1,
    "name": "Koira"
  }
}
```

---

### 2.3 Veterinary Clinic Module

**Purpose**: Manage veterinary clinic profiles, enable service discovery, and facilitate clinic-user connections.

**Data Models:**

```python
Clinic
├── owner (ForeignKey → CustomUser)
├── name, slug (unique identifiers)
├── address, city
├── latitude, longitude (geocoded location)
├── phone, email, website, instagram
├── specializations (comma-separated)
├── bio (clinic description)
├── logo (image)
├── is_verified (admin verification)
├── email_confirmed (email verification)
├── admin_approved (public listing approval)
├── email_confirmation_token
└── clinic_eoi (pilot program interest)

WorkingHours
├── clinic (ForeignKey → Clinic)
├── day_of_week (0-6: Monday-Sunday)
├── open_time, close_time
└── is_closed (boolean)

VetProfile
├── clinic (OneToOne → Clinic)
├── vet_name
├── degrees (education)
└── certifications
```

**Key API Endpoints:**

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/api/clinics/` | GET | None | List approved clinics |
| `/api/clinics/register/` | POST | None | Register clinic + user account |
| `/api/clinics/my/` | GET | Required | Get authenticated user's clinic |
| `/api/clinics/{id}/` | GET | None/Required | Get clinic details |
| `/api/clinics/{id}/` | PATCH/PUT | Required | Update clinic (owner only) |
| `/api/clinics/search/?city={city}&lat={lat}&lng={lng}` | GET | None | Search clinics by location |
| `/api/clinics/send-confirmation-email/` | POST | None | Resend confirmation email |
| `/api/clinics/confirm-email/{token}/` | GET | None | Verify clinic email |
| `/api/clinics/{id}/working-hours/` | GET | None | Get clinic working hours |
| `/api/clinics/{id}/working-hours/` | POST | Required | Set working hours (owner) |
| `/api/clinics/{id}/vet-profile/` | GET | None | Get veterinarian profile |
| `/api/clinics/{id}/vet-profile/` | POST/PATCH | Required | Update vet profile (owner) |

**Clinic Registration Flow:**

```
┌──────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │         │   API    │         │ Database │         │  Email   │
└────┬─────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                     │                     │
     │ 1. POST /clinics/  │                     │                     │
     │    register/       │                     │                     │
     ├───────────────────>│                     │                     │
     │                    │ 2. Validate data    │                     │
     │                    │ 3. Create user      │                     │
     │                    │    (is_active=False)│                     │
     │                    ├────────────────────>│                     │
     │                    │ 4. Create clinic    │                     │
     │                    │    (unverified)     │                     │
     │                    ├────────────────────>│                     │
     │                    │ 5. Generate token   │                     │
     │                    │<────────────────────┤                     │
     │                    │ 6. Send confirmation│                     │
     │                    │    email            │                     │
     │                    ├────────────────────────────────────────>│
     │ 7. Success response│                     │                     │
     │<───────────────────┤                     │                     │
     │                    │                     │                     │
     │ 8. User clicks     │                     │                     │
     │    email link      │                     │                     │
     │                    │                     │                     │
     │ 9. GET confirm/    │                     │                     │
     │    {token}         │                     │                     │
     ├───────────────────>│ 10. Verify token    │                     │
     │                    ├────────────────────>│                     │
     │                    │ 11. Activate user   │                     │
     │                    │     Confirm clinic  │                     │
     │                    │<────────────────────┤                     │
     │ 12. Confirmation   │                     │                     │
     │     page           │                     │                     │
     │<───────────────────┤                     │                     │
     │                    │                     │                     │
     │ [Admin approves clinic in admin panel]   │                     │
     │                    │                     │                     │
     │ 13. Clinic now     │                     │                     │
     │     visible in     │                     │                     │
     │     public listings│                     │                     │
     │                    │                     │                     │
```

**Sample Request/Response:**

```json
// POST /api/clinics/register/
Request:
{
  "email": "clinic@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "clinic_name": "Happy Paws Veterinary Clinic",
  "address": "123 Main Street",
  "city": "Helsinki",
  "phone": "+358 9 1234567",
  "email_clinic": "info@happypaws.fi",
  "website": "https://happypaws.fi",
  "specializations": "Dogs, Cats, Emergency Care",
  "bio": "Full-service veterinary clinic...",
  "vet_name": "Dr. Jane Smith",
  "degrees": "DVM, University of Helsinki",
  "latitude": 60.1699,
  "longitude": 24.9384,
  "clinic_eoi": true
}

Response: 201 Created
{
  "success": true,
  "message": "Clinic registered successfully. Please check your email to confirm.",
  "user_id": 45,
  "clinic_id": 12,
  "user_email": "clinic@example.com"
}

// GET /api/clinics/search/?city=Helsinki&lat=60.1699&lng=24.9384
Response: 200 OK
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 12,
      "name": "Happy Paws Veterinary Clinic",
      "slug": "happy-paws-veterinary-clinic",
      "city": "Helsinki",
      "address": "123 Main Street",
      "latitude": "60.169900",
      "longitude": "24.938400",
      "phone": "+358 9 1234567",
      "email": "info@happypaws.fi",
      "website": "https://happypaws.fi",
      "specializations": "Dogs, Cats, Emergency Care",
      "bio": "Full-service veterinary clinic...",
      "is_verified": true,
      "is_active_clinic": true,
      "distance_km": 2.5,
      "working_hours_formatted": [
        "Monday: 09:00 - 18:00",
        "Tuesday: 09:00 - 18:00",
        "Wednesday: 09:00 - 18:00",
        "Thursday: 09:00 - 18:00",
        "Friday: 09:00 - 16:00",
        "Saturday: 10:00 - 14:00",
        "Sunday: Closed"
      ]
    }
  ]
}
```

**Geolocation Integration:**

The system automatically geocodes clinic addresses to enable proximity-based search:

1. When clinic address/city changes, geocoding is triggered
2. Coordinates are stored in `latitude` and `longitude` fields
3. Search endpoint calculates distance from user's location
4. Results sorted by proximity

---

### 2.4 AI-Powered Recommendations Module

**Purpose**: Provide intelligent, personalized pet care recommendations using OpenAI's API with structured outputs.

**Data Models:**

```python
AIRecommendation
├── pet (ForeignKey → Pet)
├── type (MEAL or HEALTH)
├── content (plain text)
├── content_json (structured data)
├── created_at
└── ip_address

AIHealthReport
├── pet (ForeignKey → Pet)
├── summary (text)
├── suggestions (text)
├── summary_json (structured data)
├── created_at
└── ip_address
```

**Key API Endpoints:**

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/api/ai/recommendations/` | GET | Required | List user's AI recommendations |
| `/api/ai/recommendations/` | POST | Required | Generate new meal recommendation |
| `/api/ai/recommendations/{id}/` | GET | Required | Retrieve specific recommendation |
| `/api/ai/health-reports/` | GET | Required | List user's health reports |
| `/api/ai/health-reports/` | POST | Required | Generate new health report |
| `/api/ai/health-reports/{id}/` | GET | Required | Retrieve specific report |

**AI Recommendation Generation Flow:**

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Client  │    │   API    │    │ Database │    │Subscription│   │ OpenAI   │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │               │
     │ 1. POST /ai/  │               │               │               │
     │  recommendations/             │               │               │
     ├──────────────>│               │               │               │
     │               │ 2. Check quota│               │               │
     │               ├──────────────>│               │               │
     │               │ 3. Get pet    │               │               │
     │               │   profile     │               │               │
     │               │<──────────────┤               │               │
     │               │ 4. Check plan │               │               │
     │               │   limits      │               │               │
     │               ├───────────────────────────────>│               │
     │               │ 5. Limit OK   │               │               │
     │               │<───────────────────────────────┤               │
     │               │ 6. Build      │               │               │
     │               │   prompt with │               │               │
     │               │   pet data    │               │               │
     │               │ 7. Request AI │               │               │
     │               │   generation  │               │               │
     │               ├───────────────────────────────────────────────>│
     │               │               │               │ 8. Generate   │
     │               │               │               │   structured  │
     │               │               │               │   output      │
     │               │ 9. AI response│               │               │
     │               │<───────────────────────────────────────────────┤
     │               │ 10. Save      │               │               │
     │               │    recommendation             │               │
     │               ├──────────────>│               │               │
     │               │ 11. Update    │               │               │
     │               │     usage     │               │               │
     │               ├───────────────────────────────>│               │
     │ 12. Structured│               │               │               │
     │     response  │               │               │               │
     │<──────────────┤               │               │               │
     │               │               │               │               │
```

**AI Prompt Construction:**

The system builds comprehensive prompts from pet profile data:

```python
# Example pet profile sent to AI
{
  "pet_type": "Dog",
  "breed": "Golden Retriever",
  "age": "4 years",
  "weight": "25.5 kg",
  "activity_level": "High",
  "body_type": "Ideal",
  "neutered": true,
  "food_types": ["Dry Food", "Wet Food"],
  "food_allergies": ["Chicken", "Wheat"],
  "health_issues": [],
  "current_diet_feeling": "Enjoys meals",
  "treat_frequency": "Once a day"
}
```

**Structured Output (Pydantic Models):**

```python
# Meal Plan Structure
{
  "der_kcal": 1500,
  "nutrient_targets": {
    "protein_percent": "25-30%",
    "fat_percent": "12-15%",
    "carbs_percent": "40-45%"
  },
  "options": [
    {
      "name": "Balanced Home-Cooked Meal",
      "overview": "A nutritious home-prepared meal...",
      "sections": [
        {
          "title": "Protein Source",
          "items": ["200g lean beef", "150g turkey breast"]
        },
        {
          "title": "Carbohydrates",
          "items": ["300g sweet potato", "100g rice"]
        }
      ]
    }
  ],
  "feeding_schedule": [
    {
      "time": "8:00 AM",
      "note": "Morning meal - 50% of daily calories"
    },
    {
      "time": "6:00 PM",
      "note": "Evening meal - 50% of daily calories"
    }
  ],
  "safety_notes": [
    "Avoid chicken and wheat due to allergies",
    "Always provide fresh water"
  ]
}
```

**Sample Response:**

```json
// POST /api/ai/recommendations/
Request:
{
  "pet_id": 123,
  "type": "meal"
}

Response: 201 Created
{
  "id": 456,
  "pet": 123,
  "pet_name": "Max",
  "type": "meal",
  "created_at": "2024-12-12T10:30:00Z",
  "content_json": {
    "der_kcal": 1500,
    "nutrient_targets": { /* ... */ },
    "options": [ /* ... */ ],
    "feeding_schedule": [ /* ... */ ],
    "safety_notes": [ /* ... */ ]
  },
  "usage_count": 1,
  "monthly_limit": 3
}
```

**Subscription-Based Usage Limits:**

- Free tier: 3 AI generations per month
- Premium tier: Unlimited or higher limits
- Usage tracked per user per month
- Graceful error handling when limits reached

---

### 2.5 Legal & Compliance Module

**Purpose**: Manage privacy policies, terms of service, and user consent tracking for GDPR compliance.

**Data Models:**

```python
LegalDocument
├── title (multilingual)
├── content (multilingual)
├── document_type (PRIVACY_POLICY, TERMS_OF_SERVICE, etc.)
├── version
├── effective_date
├── is_active
└── requires_acceptance

UserConsent
├── user (ForeignKey → CustomUser)
├── document (ForeignKey → LegalDocument)
├── accepted (boolean)
├── accepted_at
└── ip_address

ConsentLog
├── user (nullable)
├── document
├── action (ACCEPTED, REJECTED, VIEWED)
├── ip_address
└── timestamp
```

**Key API Endpoints:**

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/api/legal/documents/` | GET | None | List active legal documents |
| `/api/legal/documents/{id}/` | GET | None | Get document by ID |
| `/api/legal/consent/user/` | GET | Required | Get user's consent records |
| `/api/legal/consent/user/` | POST | Required | Record user consent |
| `/api/legal/logs/` | GET | Required (Admin) | View consent audit logs |

**Consent Flow:**

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │         │   API    │         │ Database │
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                     │
     │ 1. App launch      │                     │
     │                    │                     │
     │ 2. GET /legal/     │                     │
     │    documents/      │                     │
     ├───────────────────>│                     │
     │                    │ 3. Query active docs│
     │                    ├────────────────────>│
     │ 4. Legal documents │                     │
     │<───────────────────┤                     │
     │                    │                     │
     │ 5. User reviews    │                     │
     │    and accepts     │                     │
     │                    │                     │
     │ 6. POST consent    │                     │
     ├───────────────────>│                     │
     │                    │ 7. Record consent   │
     │                    │    + create log     │
     │                    ├────────────────────>│
     │ 8. Confirmation    │                     │
     │<───────────────────┤                     │
     │                    │                     │
```

---

## 3. Authentication & Security

### 3.1 JWT Authentication

**Token Structure:**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  // Short-lived (5-15 min)
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  // Long-lived (1-7 days)
}
```

**Access Token Payload:**

```json
{
  "user_id": 42,
  "email": "user@example.com",
  "exp": 1702300800,  // Expiration timestamp
  "iat": 1702297200,  // Issued at timestamp
  "jti": "unique-token-id"
}
```

**Authentication Header:**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3.2 Security Measures

**Input Validation:**
- All serializers validate data before processing
- Type checking, length limits, format validation
- XSS prevention through automatic escaping

**Password Security:**
- Django's PBKDF2 password hashing
- Minimum length requirements
- Complexity validation
- Password confirmation on critical actions

**Email Verification:**
- Time-limited activation tokens
- Unique token generation for each request
- Prevents unauthorized account activation

**Authorization:**
- Resource ownership validation
- Permission classes on all endpoints
- Admin-only access to sensitive operations

**Rate Limiting:**
- Prevents brute force attacks
- API abuse prevention
- Configurable per endpoint

**HTTPS Enforcement:**
- SSL/TLS for all communication
- Secure cookie settings
- HSTS headers in production

---

## 4. Data Flow Examples

### 4.1 Complete User Journey: Registration to AI Recommendation

```
Step 1: User Registration
Client → POST /api/auth/signup/
     ← 201 Created {user_id, email}

Step 2: Email Verification
User clicks email link → Web/API verifies token → User activated

Step 3: Login
Client → POST /api/auth/token/ {email, password}
     ← 200 OK {access_token, refresh_token}

Step 4: Set Language Preference
Client → POST /api/me/language/ {language: "fi"}
       → Header: Authorization: Bearer {access_token}
     ← 200 OK {language: "fi"}

Step 5: Get Form Options
Client → GET /api/pet-types/
     ← 200 OK [{id:1, name:"Dog"}, {id:2, name:"Cat"}]
       → GET /api/breeds/?pet_type=1
     ← 200 OK [{id:1, name:"Golden Retriever"}, ...]

Step 6: Create Pet Profile
Client → POST /api/pets/ {name, pet_type, breed, ...}
     ← 201 Created {pet object with nested details}

Step 7: Update Pet Profile with Photo
Client → PATCH /api/pets/123/ {image: <file>}
     ← 200 OK {updated pet object}

Step 8: Generate AI Meal Recommendation
Client → POST /api/ai/recommendations/ {pet_id: 123, type: "meal"}
     ← 201 Created {structured meal plan}

Step 9: Retrieve Past Recommendations
Client → GET /api/ai/recommendations/?pet=123
     ← 200 OK [{recommendation1}, {recommendation2}, ...]
```

### 4.2 Clinic Discovery Flow

```
Step 1: Search Nearby Clinics
Client → GET /api/clinics/search/?lat=60.1699&lng=24.9384&radius=10
     ← 200 OK {results: [clinic1, clinic2, ...], count: 15}

Step 2: Get Clinic Details
Client → GET /api/clinics/12/
     ← 200 OK {clinic details, working_hours, vet_profile}

Step 3: View Working Hours
Client → GET /api/clinics/12/working-hours/
     ← 200 OK [{day: "Monday", open: "09:00", close: "18:00"}, ...]

Step 4: View Vet Profile
Client → GET /api/clinics/12/vet-profile/
     ← 200 OK {vet_name, degrees, certifications, bio}
```

---

## 5. Error Handling

### 5.1 Standard Error Responses

**Validation Error (400):**
```json
{
  "error": "Validation failed",
  "details": {
    "email": ["This field is required."],
    "password": ["Password must be at least 8 characters."]
  }
}
```

**Authentication Error (401):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Authorization Error (403):**
```json
{
  "error": "You don't have permission to edit this clinic."
}
```

**Not Found (404):**
```json
{
  "error": "Pet not found or you don't have access."
}
```

**Rate Limit (429):**
```json
{
  "error": "You've reached your monthly limit of 3 AI meal suggestions.",
  "limit": 3,
  "used": 3,
  "reset_date": "2025-01-01"
}
```

**Server Error (500):**
```json
{
  "error": "An unexpected error occurred. Please try again later.",
  "error_id": "ERR-2024-12-12-12345"
}
```

---

## 6. Database Schema

### 6.1 Entity Relationship Diagram

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ CustomUser  │1      1│   Profile   │1      * │     Pet     │
│─────────────│◄────────│─────────────│◄────────│─────────────│
│ id          │         │ user_id FK  │         │ user_id FK  │
│ email       │         │ first_name  │         │ name        │
│ password    │         │ last_name   │         │ pet_type_id │
│ is_active   │         │ phone       │         │ breed_id    │
└─────────────┘         │ address     │         │ weight      │
       │                │ city        │         └─────────────┘
       │                │ preferred_  │                │
       │                │  language   │                │
       │                │ subscription│                │
       │                │  _plan_id   │                │
       │                └─────────────┘                │
       │1                                              │
       │                                               │1
       │*                                              │
┌─────────────┐                               ┌─────────────┐
│   Clinic    │                               │AIRecommendat│
│─────────────│                               │─────────────│
│ owner_id FK │                               │ pet_id FK   │
│ name        │                               │ type        │
│ address     │                               │ content     │
│ city        │                               │ content_json│
│ latitude    │                               │ created_at  │
│ longitude   │                               └─────────────┘
│ email       │
│ phone       │                               ┌─────────────┐
│ is_verified │                               │LegalDocument│
│ email_      │                               │─────────────│
│  confirmed  │                               │ title       │
│ admin_      │                               │ content     │
│  approved   │                               │ type        │
└─────────────┘                               │ version     │
       │1                                     │ is_active   │
       │                                      └─────────────┘
       │*                                            │1
┌─────────────┐                                     │
│WorkingHours │                                     │*
│─────────────│                               ┌─────────────┐
│ clinic_id FK│                               │ UserConsent │
│ day_of_week │                               │─────────────│
│ open_time   │                               │ user_id FK  │
│ close_time  │                               │ document_id │
│ is_closed   │                               │ accepted    │
└─────────────┘                               │ accepted_at │
                                              └─────────────┘
```

### 6.2 Key Database Optimizations

**Indexes:**
- Foreign keys automatically indexed
- Email fields (unique + indexed)
- Date fields for time-based queries
- Geocoding fields (latitude, longitude) for spatial queries

**Query Optimization:**
- Select_related() for ForeignKey relationships
- Prefetch_related() for ManyToMany relationships
- Pagination on list endpoints
- Filtered querysets to reduce data transfer

---

## 7. Scalability Considerations

### 7.1 Current Architecture Strengths

✅ **Stateless API**: JWT authentication eliminates session state
✅ **Modular Design**: Independent apps can scale separately
✅ **Database Optimization**: Proper indexing and query optimization
✅ **Caching Ready**: Structure supports Redis/Memcached integration
✅ **Async Ready**: Django supports async views for I/O operations

### 7.2 Future Scaling Strategies

**Horizontal Scaling:**
- Load balancer → Multiple API servers
- Stateless design enables easy replication
- Database read replicas for query distribution

**Caching Layer:**
- Redis for frequently accessed data
- Cache reference data (breeds, pet types)
- Cache AI recommendations

**Background Tasks:**
- Celery for async processing
- Email sending
- AI generation queue
- Geocoding operations

**CDN Integration:**
- Static assets (images, CSS, JS)
- Pet images and clinic logos
- Reduced server load

**Microservices Evolution:**
- AI module as independent service
- Clinic search as geolocation service
- Email service extraction

---

## 8. API Versioning Strategy

### 8.1 Current Implementation

All endpoints prefixed with implicit version:
```
/api/v1/pets/
/api/v1/clinics/
/api/v1/auth/token/
```

### 8.2 Future Version Management

**URL Versioning:**
```
/api/v1/pets/  → Current version
/api/v2/pets/  → New version with breaking changes
```

**Header Versioning:**
```
Accept: application/vnd.fammo.v2+json
```

**Deprecation Policy:**
- Announce deprecation 6 months in advance
- Maintain old version for 12 months minimum
- Clear migration documentation

---

## 9. Monitoring & Logging

### 9.1 Request Logging

All API requests logged with:
- Timestamp
- User ID (if authenticated)
- Endpoint
- HTTP method
- Response status
- Response time
- IP address

### 9.2 Error Tracking

Errors logged with:
- Stack trace
- User context
- Request payload (sanitized)
- Error ID for user reference
- Timestamp

### 9.3 Performance Metrics

Track:
- Response times per endpoint
- Database query counts
- AI API response times
- Error rates
- Usage patterns

---

## 10. Testing Strategy

### 10.1 Unit Tests

- Serializer validation
- Model methods
- Business logic
- Permission classes

### 10.2 Integration Tests

- Complete API workflows
- Authentication flows
- Database transactions
- External API integration

### 10.3 Load Testing

- Concurrent user simulation
- Peak load handling
- Database connection pooling
- Memory leak detection

---

## 11. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                          │
│                    (HTTPS/SSL Termination)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼────────┐             ┌────────▼────────┐
│  API Server 1   │             │  API Server 2   │
│  (Django/Gunicorn)            │  (Django/Gunicorn)
└────────┬────────┘             └────────┬────────┘
         │                               │
         └───────────────┬───────────────┘
                         │
                ┌────────▼────────┐
                │   PostgreSQL    │
                │   (Primary DB)  │
                └─────────────────┘
                         │
                ┌────────▼────────┐
                │  Media Storage  │
                │ (S3/Local Files)│
                └─────────────────┘
```

---

## 12. Conclusion

This RESTful API backend provides a robust, scalable foundation for a multi-platform pet care application. Key strengths include:

✅ **Comprehensive Coverage**: User management, pet profiles, clinic discovery, and AI recommendations
✅ **Security First**: JWT authentication, email verification, permission-based access control
✅ **Developer Friendly**: Clear documentation, consistent patterns, comprehensive error handling
✅ **Multi-language Support**: Internationalization built into core data models
✅ **AI Integration**: Structured outputs for reliable, parseable AI recommendations
✅ **Scalable Design**: Stateless architecture ready for horizontal scaling
✅ **Compliance Ready**: GDPR-compliant consent tracking and audit logs
✅ **Production Ready**: Error handling, logging, monitoring capabilities

The architecture supports current mobile application requirements while providing a flexible foundation for future platform expansion and feature enhancements.

---

## Appendix A: Complete Endpoint Reference

### Authentication Endpoints
- `POST /api/auth/signup/` - Register new user
- `POST /api/auth/token/` - Obtain JWT tokens
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password with token
- `POST /api/auth/change-password/` - Change password (authenticated)
- `POST /api/auth/resend-activation/` - Resend activation email

### User Endpoints
- `GET /api/me/` - Get current user profile
- `PATCH /api/me/` - Update user profile
- `GET /api/me/language/` - Get language preference
- `POST /api/me/language/` - Set language preference

### Pet Endpoints
- `GET /api/pets/` - List user's pets
- `POST /api/pets/` - Create new pet
- `GET /api/pets/{id}/` - Get pet details
- `PATCH /api/pets/{id}/` - Update pet
- `DELETE /api/pets/{id}/` - Delete pet

### Pet Reference Data Endpoints
- `GET /api/pet-types/` - List pet types
- `GET /api/genders/` - List genders
- `GET /api/breeds/?pet_type={id}` - List breeds
- `GET /api/age-categories/?pet_type={id}` - List age categories
- `GET /api/food-types/` - List food types
- `GET /api/food-feelings/` - List food feelings
- `GET /api/food-importance/` - List food importance levels
- `GET /api/body-types/` - List body types
- `GET /api/activity-levels/` - List activity levels
- `GET /api/food-allergies/` - List food allergies
- `GET /api/health-issues/` - List health issues
- `GET /api/treat-frequencies/` - List treat frequencies

### Clinic Endpoints
- `GET /api/clinics/` - List approved clinics
- `POST /api/clinics/register/` - Register clinic + user
- `GET /api/clinics/my/` - Get user's clinic
- `GET /api/clinics/{id}/` - Get clinic details
- `PATCH /api/clinics/{id}/` - Update clinic
- `GET /api/clinics/search/` - Search clinics by location
- `POST /api/clinics/send-confirmation-email/` - Resend confirmation
- `GET /api/clinics/confirm-email/{token}/` - Confirm clinic email
- `GET /api/clinics/{id}/working-hours/` - Get working hours
- `POST /api/clinics/{id}/working-hours/` - Set working hours
- `GET /api/clinics/{id}/vet-profile/` - Get vet profile
- `POST /api/clinics/{id}/vet-profile/` - Create/update vet profile

### AI Endpoints
- `GET /api/ai/recommendations/` - List recommendations
- `POST /api/ai/recommendations/` - Generate meal recommendation
- `GET /api/ai/recommendations/{id}/` - Get specific recommendation
- `GET /api/ai/health-reports/` - List health reports
- `POST /api/ai/health-reports/` - Generate health report
- `GET /api/ai/health-reports/{id}/` - Get specific report

### Legal Endpoints
- `GET /api/legal/documents/` - List legal documents
- `GET /api/legal/documents/{id}/` - Get document details
- `GET /api/legal/consent/user/` - Get user consents
- `POST /api/legal/consent/user/` - Record consent
- `GET /api/legal/logs/` - View consent logs (admin)

### Configuration Endpoints
- `GET /api/config/` - App configuration
- `GET /api/languages/` - Available languages
- `GET /api/onboarding/` - Onboarding slides
- `GET /api/ping/` - Health check

---

**Document Version:** 1.0  
**Last Updated:** December 12, 2024  
**API Version:** v1.0.0
