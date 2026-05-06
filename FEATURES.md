# FAMMO – Complete Feature Documentation

> Last updated: May 2026  
> Platform: Django web + REST API (mobile-first)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Authentication & Accounts](#2-authentication--accounts)
3. [Pet Management](#3-pet-management)
4. [AI Features](#4-ai-features)
5. [AI Chat Assistant](#5-ai-chat-assistant)
6. [Veterinary Clinics](#6-veterinary-clinics)
7. [Appointment Booking](#7-appointment-booking)
8. [Blog](#8-blog)
9. [Forum (Q&A Community)](#9-forum-qa-community)
10. [Subscription Plans](#10-subscription-plans)
11. [Notifications](#11-notifications)
12. [Legal & Compliance](#12-legal--compliance)
13. [Admin Features](#13-admin-features)
14. [Mobile API](#14-mobile-api)
15. [Multi-language Support](#15-multi-language-support)

---

## 1. Project Overview

FAMMO is a comprehensive pet health and wellness platform serving two primary user types:

| Role | Description |
|---|---|
| **Pet Owner (User)** | Registers pets, gets AI-powered health and nutrition advice, books vet appointments, joins the community |
| **Vet / Clinic Owner** | Registers a clinic, manages appointments, tracks referrals, receives notifications |

**Core stack:** Django · Django REST Framework · OpenAI GPT-4o · Firebase FCM · Celery · MySQL (production)

---

## 2. Authentication & Accounts

### Registration & Login

| Action | How |
|---|---|
| Sign up with email & password | `POST /api/v1/auth/signup/` or `/register/` |
| Sign up / log in with Google | `POST /api/v1/auth/google/` (OAuth 2.0 via django-allauth) |
| Activate account | Click email link → `/activate/<token>/` |
| Resend activation email | `POST /api/v1/auth/resend-activation/` |
| Forgot password | `POST /api/v1/auth/forgot-password/` |
| Reset password | `POST /api/v1/auth/reset-password/` (token expires in 24 hours) |
| Change password | `POST /api/v1/auth/change-password/` (authenticated) |

**Notes:**
- Email confirmation is required before the account is active.
- JWT access tokens last 30 days; refresh tokens last 365 days.

### User Profile

| Action | How |
|---|---|
| View / edit profile | `GET/PUT/PATCH /api/v1/profile/me/` or `/profile/` |
| Fields | First name, last name, phone, address, city, zip code, country, preferred language |
| Save location for nearby clinics | `POST /api/v1/users/api/save-location/` |

### Account Deletion (GDPR)

- User initiates deletion request from `/delete-account/`.
- A 30-day grace period begins — the user can cancel during this window.
- After 30 days the account and all associated data are deleted.
- Deletion requests track: reason, reviewer, scheduled deletion date, status (`pending / approved / cancelled / completed`).

---

## 3. Pet Management

### Creating & Editing Pets

| Action | How |
|---|---|
| Create pet (multi-step wizard) | `/pet/wizard/` |
| Edit pet | `/pet/edit/<id>/` |
| View all pets | `/pet/my-pets/` |
| Pet detail | `/pet/detail/<id>/` |
| Delete pet | `/pet/delete/<id>/` |
| API create/list | `GET/POST /api/v1/pets/` |
| API retrieve/update/delete | `GET/PUT/DELETE /api/v1/pets/<id>/` |

**Pet profile fields (20+):**

| Category | Fields |
|---|---|
| Identity | Name, image, pet type, gender, breed, neutered |
| Age | Age at registration, calculated birth date, current age (years/months/weeks/days) |
| Health | Weight, body type, activity level, health issues (diabetes, arthritis, …) |
| Nutrition | Food type(s), food feeling, food importance, treat frequency, food allergies |
| Subscription limit | 1 pet (Essentials), 2 (Wellness), 5 (Optimal) |

### Age Tracking

- **Age categories**: Puppy → Adult → Senior (species-specific thresholds).
- Age transitions are stored in `PetAgeHistory` with the reason for the change.
- `AgeTransitionRule` defines at how many months each transition happens per pet type.

### Weight Tracking

| Action | How |
|---|---|
| Add weight record | `/pet/<id>/weight/add/` |
| View weight history | Pet detail page |

- Every new record auto-updates the current weight on the pet profile.
- The first registration weight is preserved as the initial record.
- **Reminder intervals** (species/age based): every 7–30 days.

### Audit Trail

Every change to important pet fields (weight, body type, activity level, health conditions) is saved in `PetDataChangeLog` with: old value, new value, who changed it, when, and why.

### Reference Data (dropdowns / lookup lists)

All accessible via API:

```
GET /api/v1/pet-types/          → Dog, Cat, …
GET /api/v1/breeds/             → filtered by ?pet_type=
GET /api/v1/genders/
GET /api/v1/age-categories/     → filtered by ?pet_type=
GET /api/v1/food-types/
GET /api/v1/food-feelings/
GET /api/v1/food-importance/
GET /api/v1/body-types/
GET /api/v1/activity-levels/
GET /api/v1/food-allergies/
GET /api/v1/health-issues/
GET /api/v1/treat-frequencies/
```

---

## 4. AI Features

All AI features use **OpenAI GPT-4o with structured (Pydantic) output**.

### Meal Recommendations

| Tier | Monthly limit |
|---|---|
| Essentials | 3 |
| Wellness | 5 |
| Optimal | Unlimited |

- Accessed from the pet detail page or `/pet/<id>/calories/calculator/`.
- Output includes: DER calories, nutrient targets, meal options, feeding schedule, safety notes.
- Results are saved and can be viewed again.

### Health Reports

| Tier | Monthly limit |
|---|---|
| Essentials | 1 |
| Wellness | 3 |
| Optimal | Unlimited |

- Output includes: health summary, breed-specific risk factors, weight/diet advice, activity recommendations, alerts.

### Calorie Calculator

- Available at `/pet/<id>/calories/calculate/`.
- AI-powered personalized daily calorie estimate based on pet's full profile.

### Usage Limits

- Counters reset on the 1st of every month.
- Admins/superusers have unlimited access regardless of plan.
- When limit is reached, a "limit reached" page is shown with an upgrade prompt.

### ML Training Data Collection (`ai_core`)

- Every AI prediction is logged to `NutritionPredictionLog` with:
  - Full pet profile snapshot (species, breed size, health goal, weight, age, BCS, …)
  - Full input payload & output payload
  - Backend used (`openai` or `proprietary`), model version, source (`mobile/web/api`)
- Collected data is used to train and improve a proprietary in-house model.

---

## 5. AI Chat Assistant

An AI pet-care assistant aware of the user's own pets.

| Action | API |
|---|---|
| List chat sessions | `GET /api/v1/chat/sessions/` |
| Start new session | `POST /api/v1/chat/sessions/new/` |
| Get active session | `GET /api/v1/chat/active/` |
| Send message (text or image) | `POST /api/v1/chat/send/` |
| View message history | `GET /api/v1/chat/sessions/<id>/messages/` |
| Clear session messages | `POST /api/v1/chat/sessions/<id>/clear/` |
| Delete session | `DELETE /api/v1/chat/sessions/<id>/` |
| Delete single message | `DELETE /api/v1/chat/messages/<id>/` |

**Key details:**

- **Multimodal**: Supports text and image messages.
- **Pet context**: User's pet profiles are included automatically in the AI prompt.
- **Session management**: Only one active session per user at a time.
- **Image lifecycle**: Images are stored for 7 days then auto-cleaned.
- Web interface available at `/chat/`.

---

## 6. Veterinary Clinics

### Clinic Registration (Vet owner)

| Step | Action |
|---|---|
| 1 | Fill in registration form at `/vets/register/` (or `POST /api/v1/clinics/register/`) |
| 2 | Confirm email via link sent to clinic email |
| 3 | Wait for admin approval |
| 4 | Once approved, clinic appears in the public directory |

**Clinic profile fields:**

| Category | Fields |
|---|---|
| Identity | Name, slug, logo, bio |
| Contact | Phone, email, website, Instagram |
| Location | City, address, latitude/longitude (auto-geocoded) |
| Schedule | Working hours per day (open time, close time, closed flag) |
| Specializations | Free-text comma-separated list |
| Vet details | Vet name, degrees, certifications (`VetProfile`) |

### Clinic Dashboard (Vet owner)

| Page | URL |
|---|---|
| Overview / analytics | `/vets/dashboard/` |
| Edit clinic profile | `/vets/dashboard/profile/` |
| Manage appointments | `/vets/dashboard/appointments/` |
| View / update single appointment | `/vets/dashboard/appointments/<id>/update/` |
| View referral signups | `/vets/dashboard/referrals/` |
| Detailed analytics | `/vets/dashboard/analytics/` |
| Notifications | `/vets/dashboard/notifications/` |
| Mark notification(s) read | `/vets/dashboard/notifications/<id>/read/` |

### Referral Program

- Each clinic gets a unique referral code (e.g., `vet-dogfriendly`).
- Share link: `/vets/ref/<code>/` — pre-fills the user registration form.
- `ReferredUser` tracks: which user signed up, via which code, current status (`NEW / ACTIVE / INACTIVE`).
- Clinic can see referral performance in the dashboard.

### Clinic Finder (public)

| Action | How |
|---|---|
| Browse clinic directory | `/vets/clinics/` |
| View clinic profile | `/vets/clinic/<slug>/` |
| Find nearby clinics (map) | `/vets/find/` |
| API: nearby by location | `GET /api/v1/vets/api/nearby-clinics/` |
| API: search by city | `GET /api/v1/vets/api/clinics-by-city/` |
| API: IP-based location | `GET /api/v1/vets/api/location/ip/` |

---

## 7. Appointment Booking

### User: booking a vet appointment

| Step | Action |
|---|---|
| 1 | Browse to clinic page or find via map |
| 2 | Select appointment reason (annual checkup, vaccination, emergency, dental, …) |
| 3 | Pick date from available dates (next 90 days) |
| 4 | Pick time slot (generated from clinic working hours, 30 min default) |
| 5 | Select pet, add notes, submit |
| 6 | Receive confirmation |

| Action | URL / API |
|---|---|
| Book appointment | `/vets/clinic/<slug>/book/` or `POST /api/v1/appointments/` |
| Get available dates | `GET /api/v1/clinics/<id>/available-dates/` |
| Get available slots | `GET /api/v1/clinics/<id>/available-slots/` or `/vets/clinic/<slug>/available-slots/` |
| View my appointments | `/vets/my-appointments/` or `GET /api/v1/appointments/my/` |
| View appointment detail | `/vets/appointment/<id>/` or `GET /api/v1/appointments/<id>/` |
| Cancel appointment | `/vets/appointment/<id>/cancel/` or `POST /api/v1/appointments/<id>/cancel/` |

**Appointment statuses:**

`PENDING` → `CONFIRMED` → `COMPLETED` / `NO_SHOW`  
Any side can move to `CANCELLED_USER` or `CANCELLED_CLINIC`

### Vet: managing appointments

| Action | URL / API |
|---|---|
| View all clinic appointments | `/vets/dashboard/appointments/` or `GET /api/v1/clinics/<id>/appointments/` |
| Update appointment status | `/vets/dashboard/appointments/<id>/update/` or `PUT /api/v1/clinics/<id>/appointments/<appt_id>/` |
| Confirm appointment | `confirm()` method via API |
| Cancel appointment | `cancel()` method via API |
| Add clinic notes | Via update endpoint (clinic_notes field, private) |

---

## 8. Blog

### Public readers

| Action | URL |
|---|---|
| Browse all posts | `/blog/` |
| Filter by category | `/blog/?category=<slug>` |
| Search posts | `/blog/?search=<query>` (searches title, content, author) |
| Sort posts | `/blog/?sort=newest\|oldest\|views\|comments\|rating` |
| Read a post | `/blog/<slug>/` |
| Rate a post (1–5 stars) | `/blog/<slug>/rate/` |
| Leave a comment | `/blog/<slug>/comment/` |

Features:
- Pagination: 9 posts per page
- View counter on each post
- Star rating with average shown in list
- Category badges

### Blog management (staff only)

| Action | URL |
|---|---|
| Dashboard overview | `/blog/dashboard/` |
| Create topic for AI generation | `/blog/dashboard/topics/create/` |
| Edit / delete topics | `/blog/dashboard/topics/<id>/edit|delete/` |
| Trigger AI generation for a topic | `/blog/dashboard/topics/<id>/generate/` |
| Manual blog generation | `/blog/dashboard/generate/` |
| View generation requests | `/blog/dashboard/requests/` |
| Publish / unpublish post | `/blog/dashboard/posts/<id>/publish|unpublish/` |
| Delete post | `/blog/dashboard/posts/<id>/delete/` |
| Upload inline images (for Markdown editor) | `/blog/dashboard/uploads/inline-image/` |

**AI generation workflow:**

1. Admin creates a `BlogTopic` with: title, primary keyword, secondary keywords, target audience, notes, priority, language.
2. Trigger generation → AI writes a full blog post (GPT-4o, structured Pydantic output).
3. AI also drafts a **LinkedIn post** (600–1200 chars) and an **X/Twitter post** (≤280 chars).
4. Staff reviews and publishes.

---

## 9. Forum (Q&A Community)

### Actions available to all users

| Action | URL |
|---|---|
| Browse questions | `/forum/` |
| Filter by category | `/forum/?category=<cat>` |
| Sort | Newest / most votes / unanswered |
| View question + answers | `/forum/question/<id>/` |
| Ask a question (login required) | `/forum/ask/` |
| Answer a question (login required) | (from question detail page) |
| Vote on question or answer | `/forum/vote/<type>/<id>/<up|down>/` (AJAX) |
| Accept best answer (question author only) | `/forum/answer/<id>/accept/` |

**Question categories:**

`dog_health` · `cat_health` · `dog_behavior` · `cat_behavior` · `nutrition` · `training` · `grooming` · `veterinary` · `adoption` · `general`

**Features:**

- Questions can include an image (auto-compressed to <1 MB, converted to JPEG).
- Vote counts act as a reputation system.
- One accepted answer per question (marked by the author).
- View counter on each question.

---

## 10. Subscription Plans

| Feature | Essentials (free) | Wellness | Optimal |
|---|---|---|---|
| Pets | 1 | 2 | 5 |
| AI meal recommendations / month | 3 | 5 | Unlimited |
| AI health reports / month | 1 | 3 | Unlimited |
| Price | Free | — | — |

- Counters reset on the 1st of every month.
- Browse plans at `/subscription/plans/`.
- Plan is linked to the user profile (`Profile.subscription_plan`).
- Admins/superusers are always unlimited.

---

## 11. Notifications

### User notifications

| Type | Trigger |
|---|---|
| `APPOINTMENT_CONFIRMED` | Clinic confirms appointment |
| `APPOINTMENT_CANCELLED` | Appointment cancelled by either side |
| `APPOINTMENT_REMINDER` | Upcoming appointment reminder |
| `EMAIL_CONFIRMATION` | New account email confirmation |
| `PET_REMINDER` | Weight update reminder |
| `NEW_REFERRAL` | Someone used clinic referral link |
| `ADMIN_MESSAGE` | Manual admin message |
| `SYSTEM` | System-level events |

| Action | URL / API |
|---|---|
| View all notifications | `/notifications/` or `GET /api/v1/notifications/` |
| Mark single as read | `/notifications/<id>/read/` or `POST /api/v1/notifications/<id>/read/` |
| Mark all as read | `/notifications/mark-all-read/` or `POST /api/v1/notifications/mark-all-read/` |
| Delete notification | `/notifications/<id>/delete/` or `DELETE /api/v1/notifications/<id>/` |
| Unread count (badge) | `GET /api/v1/notifications/unread-count/` |

### Clinic notifications

Separate system for clinic owners. Accessible via:
- `/vets/dashboard/notifications/`
- `GET /api/v1/clinics/notifications/`
- `GET /api/v1/clinics/notifications/unread-count/`

### Push notifications (mobile)

- FCM (Firebase Cloud Messaging) integration.
- Register device: `POST /api/v1/users/register-device/`
- Unregister: `POST /api/v1/users/unregister-device/`
- Supports Android, iOS, and web.
- Multiple devices per user.

---

## 12. Legal & Compliance

| Feature | Details |
|---|---|
| GDPR account deletion | 30-day grace period, full audit trail |
| Legal documents | Terms of Service, Privacy Policy, Cookie Policy — versioned per language |
| User consent tracking | IP address, user-agent, timestamp recorded per document acceptance |
| Clinic consent tracking | Same, but linked to clinic entity |
| Consent audit log | Every consent change is appended to `ConsentLog` |
| Location consent | Users explicitly opt in before location is stored |

API:
```
GET  /api/v1/legal/documents/
GET  /api/v1/legal/consent/user/
GET  /api/v1/legal/consent/clinic/
GET  /api/v1/legal/logs/
```

Web pages:
- `/privacy-policy/`
- `/terms/`
- `/vets/clinic-terms/`
- `/vets/clinic-partnership/`
- `/vets/eoi-terms/`

---

## 13. Admin Features

Available to staff/superuser accounts via the Django admin and custom admin dashboard (`/admin-dashboard/`):

| Feature | Description |
|---|---|
| Admin dashboard | KPI overview with charts (users, pets, appointments, blog) |
| Clinic approval | Review and approve/reject clinic registrations |
| Blog management | AI topic queue, post generation, publish/unpublish, delete |
| User management | View users, export data as CSV |
| Pet data export | Export all pets as CSV |
| Translation management | Manage multilingual string translations at `/translations/` |
| Email template previews | Preview transactional emails in browser |
| Send admin messages | Push `ADMIN_MESSAGE` notifications to any user |
| Legal document versioning | Create and activate new versions of legal documents |
| Consent audit | View full consent log for any user or clinic |

---

## 14. Mobile API

All user-facing functionality is exposed via a versioned REST API under `/api/v1/`.

### Authentication
```
POST /api/v1/auth/signup/
POST /api/v1/auth/google/
POST /api/v1/auth/forgot-password/
POST /api/v1/auth/reset-password/
POST /api/v1/auth/change-password/
POST /api/v1/auth/resend-activation/
```

### User & Profile
```
GET|PUT|PATCH  /api/v1/profile/me/
POST           /api/v1/users/api/save-location/
POST           /api/v1/users/register-device/
POST           /api/v1/users/unregister-device/
POST           /api/v1/languages/set/
```

### Pets
```
GET|POST        /api/v1/pets/
GET|PUT|DELETE  /api/v1/pets/<id>/
```

### Clinics & Vets
```
GET|POST    /api/v1/clinics/
GET         /api/v1/clinics/my/
GET|PUT|DEL /api/v1/clinics/<id>/
POST        /api/v1/clinics/register/           # combined user + clinic
POST        /api/v1/clinics/search/
GET         /api/v1/clinics/<id>/working-hours/
GET|PUT     /api/v1/clinics/<id>/vet-profile/
POST        /api/v1/clinics/send-confirmation-email/
GET         /api/v1/clinics/confirm-email/<token>/
```

### Appointments
```
GET|POST    /api/v1/appointments/
GET         /api/v1/appointments/my/
GET         /api/v1/appointments/<id>/
POST        /api/v1/appointments/<id>/cancel/
GET         /api/v1/appointments/reasons/
GET         /api/v1/clinics/<id>/available-dates/
GET         /api/v1/clinics/<id>/available-slots/
GET         /api/v1/clinics/<id>/appointments/
PUT         /api/v1/clinics/<id>/appointments/<appt_id>/
```

### AI
```
POST  /api/v1/ai/recommendations/       # meal plan
POST  /api/v1/ai/health-reports/        # health report
```

### Chat
```
GET|POST  /api/v1/chat/sessions/
POST      /api/v1/chat/sessions/new/
GET|DEL   /api/v1/chat/sessions/<id>/
GET       /api/v1/chat/sessions/<id>/messages/
POST      /api/v1/chat/sessions/<id>/clear/
POST      /api/v1/chat/send/
GET       /api/v1/chat/active/
DELETE    /api/v1/chat/messages/<id>/
```

### Notifications
```
GET   /api/v1/notifications/
POST  /api/v1/notifications/<id>/read/
POST  /api/v1/notifications/mark-all-read/
GET   /api/v1/notifications/unread-count/
DEL   /api/v1/notifications/<id>/
```

### Blog
```
GET      /api/v1/blog/categories/
GET|POST /api/v1/blog/posts/
GET|PUT|DEL /api/v1/blog/posts/<id>/
```

### App Config & Onboarding
```
GET  /api/v1/config/          # base URLs, logos, assets
GET  /api/v1/onboarding/      # onboarding slides
GET  /api/v1/languages/
```

---

## 15. Multi-language Support

| Language | Code | URL prefix |
|---|---|---|
| English | `en` | `/en/` |
| Turkish | `tr` | `/tr/` |
| Dutch | `nl` | `/nl/` |
| Finnish | `fi` | `/fi/` |

- User can set preferred language via profile or `POST /api/v1/languages/set/`.
- Blog posts can be authored in any of the 4 languages.
- Django model translation (`django-modeltranslation`) is used for translatable model fields.
- All UI strings use Django's `{% trans %}` / `gettext` system.

---

## Data Model Overview

```
CustomUser ──(1:1)── Profile
    │
    ├──(1:M)── Pet
    │              ├── PetWeightRecord
    │              ├── PetAgeHistory
    │              ├── PetDataChangeLog
    │              └── PetConditionSnapshot
    │
    ├──(1:M)── ChatSession ── ChatMessage
    │
    ├──(1:M)── Question (forum)
    ├──(1:M)── Answer (forum)
    ├──(1:M)── Vote (forum)
    │
    ├──(1:M)── BlogPost
    ├──(1:M)── BlogComment
    ├──(1:M)── BlogRating
    │
    ├──(1:1)── Clinic (as owner)
    │              ├── WorkingHours
    │              ├── VetProfile
    │              ├── ReferralCode ── ReferredUser
    │              ├── Appointment ← (also linked to User + Pet)
    │              └── ClinicNotification
    │
    ├──(1:M)── Appointment (as patient)
    ├──(1:M)── DeviceToken (FCM)
    ├──(1:M)── UserNotification
    ├──(1:M)── AIUsage (monthly counters)
    ├──(1:M)── AIRecommendation
    ├──(1:M)── AIHealthReport
    └──(1:1)── SubscriptionPlan
```
