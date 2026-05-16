# FAMMO — Complete Platform Documentation

> **Version:** May 2026  
> **Stack:** Django 5.2 · Django REST Framework · OpenAI GPT-4o · Firebase FCM · Celery · MySQL (production) / SQLite (development)  
> **Live domain:** [fammo.ai](https://fammo.ai)

---

## Table of Contents

1. [What is FAMMO?](#1-what-is-fammo)
2. [Who Can Use FAMMO?](#2-who-can-use-fammo)
3. [Technology Stack](#3-technology-stack)
4. [Project Structure — Django Apps](#4-project-structure--django-apps)
5. [Authentication & Accounts](#5-authentication--accounts)
6. [Pet Management](#6-pet-management)
7. [AI Nutrition & Health Features](#7-ai-nutrition--health-features)
8. [AI Chat Assistant](#8-ai-chat-assistant)
9. [Veterinary Clinics](#9-veterinary-clinics)
10. [Appointment Booking](#10-appointment-booking)
11. [Subscription Plans](#11-subscription-plans)
12. [Blog](#12-blog)
13. [Community Forum (Q&A)](#13-community-forum-qa)
14. [Notifications](#14-notifications)
15. [Legal & Compliance (GDPR)](#15-legal--compliance-gdpr)
16. [Admin Features](#16-admin-features)
17. [Mobile & REST API Reference](#17-mobile--rest-api-reference)
18. [Multi-language Support](#18-multi-language-support)
19. [Data Model Overview](#19-data-model-overview)
20. [Deployment & Infrastructure](#20-deployment--infrastructure)

---

## 1. What is FAMMO?

**FAMMO** (fammo.ai) is a comprehensive **AI-powered pet health and wellness platform**. It helps pet owners take better care of their animals by combining:

- **AI-generated personalised nutrition plans** — daily calorie calculations, meal recommendations, and feeding schedules tailored to each pet's species, breed, age, weight, health conditions, and activity level.
- **AI health reports** — breed-specific risk assessments, diet/weight advice, and activity recommendations powered by OpenAI GPT-4o.
- **An AI chat assistant** — a conversational pet-care advisor that knows the user's own pets and can answer any pet health or nutrition question (text and image support).
- **A vet clinic directory** — pet owners can find verified veterinary clinics on an interactive map, see their full profile, and book appointments directly on the platform.
- **A community forum** — pet owners can ask questions, share advice, and vote on the best answers.
- **A knowledge blog** — AI-generated and staff-reviewed articles on pet health, nutrition, and care.

FAMMO serves two primary user types:

| User Type | What They Do |
|---|---|
| **Pet Owner** | Creates a pet profile, receives AI health & meal advice, books vet appointments, chats with the AI assistant, participates in the community |
| **Vet / Clinic Owner** | Registers a clinic, manages a public clinic page, handles appointment bookings, grows their client base through a referral programme |

---

## 2. Who Can Use FAMMO?

### Pet Owners

Any person who owns or cares for a pet (currently cats and dogs are the primary species supported). A pet owner can:

- Create an account for free (email or Google sign-in).
- Register up to **1 pet** on the free plan, **2** on Wellness, or **5** on the Optimal plan.
- Get AI-generated **personalised meal recommendations** (what to feed, how much, nutrient targets).
- Get AI-generated **health reports** (risk factors, weight advice, alerts).
- Use the **AI chat assistant** to ask any pet-related question.
- **Track weight** over time and receive reminders to update it.
- **Find veterinary clinics** near their location on a map.
- **Book and manage appointments** with any verified clinic.
- Read the **blog** and join the **community forum**.

### Veterinarians / Clinic Owners

Any licensed veterinary practice or individual vet can register a clinic profile on FAMMO. After email confirmation and admin approval, the clinic:

- Gets a public listing page at `/vets/clinic/<slug>/`.
- Can be discovered by pet owners via the map and directory.
- Receives **appointment booking requests** directly through FAMMO.
- Manages appointments (confirm, complete, cancel, add notes) via the vet dashboard.
- Gets a unique **referral link** to invite new users to FAMMO and track sign-ups.
- Receives in-platform and push notifications for new bookings.

### Staff / Admins

Staff members have access to:

- An admin dashboard with platform-wide KPIs.
- Blog content management with AI-assisted article generation.
- Clinic approval/rejection workflow.
- User management and CSV exports.
- Legal document versioning and consent audit logs.

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| **Backend framework** | Django 5.2 |
| **REST API** | Django REST Framework 3.16 + SimpleJWT |
| **AI / LLM** | OpenAI GPT-4o (structured Pydantic output) |
| **Task queue** | Celery 5.6 + Redis |
| **Scheduled tasks** | django-celery-beat |
| **Push notifications** | Firebase Cloud Messaging (FCM) |
| **Database (production)** | MySQL (utf8mb4) |
| **Database (development)** | SQLite |
| **Authentication** | django-allauth (email + Google OAuth 2.0) |
| **Geocoding** | Google Maps Geocoding API + GeoIP2 (MaxMind) |
| **Translations** | django-modeltranslation, gettext |
| **Frontend styling** | Tailwind CSS |
| **Markdown** | django-markdownx + django-markdownify |
| **ML / Data science** | scikit-learn, pandas, numpy, matplotlib |
| **Hosting** | cPanel / Gunicorn |
| **Screenshots** | Playwright |

---

## 4. Project Structure — Django Apps

The project is split into focused Django applications:

| App | Purpose |
|---|---|
| `userapp` | Custom user model, user profiles, account deletion |
| `pet` | Pet profiles, breeds, weight tracking, age categories, audit trail |
| `aihub` | AI recommendation and health report generation & storage |
| `ai_core` | AI engine abstraction (OpenAI / proprietary), prediction logging for ML training |
| `chat` | AI chat sessions and messages |
| `vets` | Veterinary clinics, vet profiles, referral codes, working hours |
| `api` | REST API views, serializers, URL routing — the mobile API layer |
| `core` | Homepage content, FAQs, leads, social links, legal documents, onboarding slides |
| `subscription` | Subscription plans, AI usage tracking, transaction records |
| `blog` | Blog posts, categories, AI generation pipeline |
| `forum` | Community Q&A, answers, voting |
| `notifications` | In-app and push notification system + Telegram admin alerts |
| `evidence` | (Reserved for evidence/research content) |
| `famo` | Django project settings, URL root, WSGI/ASGI |

---

## 5. Authentication & Accounts

### Registration & Login

| Action | Web URL | API Endpoint |
|---|---|---|
| Register with email | `/register/` | `POST /api/v1/auth/signup/` |
| Login with email | `/login/` | `POST /api/v1/auth/login/` |
| Sign in with Google | `/accounts/google/login/` | `POST /api/v1/auth/google/` |
| Activate account | `/activate/<token>/` | — |
| Resend activation email | — | `POST /api/v1/auth/resend-activation/` |
| Forgot password | `/forgot-password/` | `POST /api/v1/auth/forgot-password/` |
| Reset password | `/reset-password/<token>/` | `POST /api/v1/auth/reset-password/` |
| Change password | `/change-password/` | `POST /api/v1/auth/change-password/` |
| Logout | `/logout/` | — |

**Security notes:**
- Email must be confirmed before the account is activated.
- JWT **access tokens** are valid for **30 days**; **refresh tokens** for **365 days**.
- Password reset tokens expire in **24 hours**.
- Authentication uses `Bearer` tokens in the `Authorization` header.

### User Profile

Every registered user has a `Profile` linked one-to-one to their account, containing:

| Field | Description |
|---|---|
| First name, Last name | Display name |
| Phone | Contact number |
| Address, City, ZIP code, Country | Physical location |
| Latitude / Longitude | Optional, used for nearby clinic search |
| `location_consent` | Must be `true` before coordinates are stored (GDPR) |
| `preferred_language` | `en`, `tr`, `nl`, or `fi` — controls the mobile app language |
| `subscription_plan` | FK to the active plan (Essentials / Wellness / Optimal) |
| `is_writer` | Grants blog writing permissions |

| Action | Web | API |
|---|---|---|
| View / update profile | `/profile/` | `GET/PUT/PATCH /api/v1/profile/me/` |
| Save approximate location | — | `POST /api/v1/users/api/save-location/` |
| Set preferred language | — | `POST /api/v1/languages/set/` |

### Account Deletion (GDPR)

Users can request full account deletion at `/delete-account/`. The workflow:

1. User submits a deletion request with an optional reason.
2. A **30-day grace period** begins — user can cancel at any time during this window.
3. After 30 days, the account and all associated data (pets, AI reports, chat history, appointments) are permanently deleted.
4. Every request is tracked with: status (`pending / approved / cancelled / completed`), reviewer, scheduled deletion date, and what data existed (number of pets, had clinic, etc.).

---

## 6. Pet Management

### Creating a Pet Profile

Pet profiles are created through a **multi-step registration wizard** (`/pet/wizard/`). The wizard collects:

**Step 1 — Identity**
- Pet name, type (Dog / Cat / …), gender, breed (or "unknown breed"), whether neutered/spayed

**Step 2 — Age & Weight**
- Current age (years + months + weeks) — FAMMO calculates and stores the birth date
- Current weight (kg)

**Step 3 — Health**
- Body type (body condition score)
- Activity level
- Existing health issues (diabetes, arthritis, kidney disease, allergies, obesity, …)

**Step 4 — Nutrition**
- Food type(s) currently fed (dry, wet, raw, home-cooked, …)
- How the pet feels about food (picky, normal, food-driven)
- Food importance to owner
- Treat frequency
- Food allergies

The pet profile is saved after the final step, and the user is taken to the pet detail page where AI features become available.

### Pet Actions

| Action | Web URL | API |
|---|---|---|
| Create pet (wizard) | `/pet/wizard/` | `POST /api/v1/pets/` |
| List my pets | `/pet/my-pets/` | `GET /api/v1/pets/` |
| View pet detail | `/pet/detail/<id>/` | `GET /api/v1/pets/<id>/` |
| Edit pet | `/pet/edit/<id>/` | `PUT/PATCH /api/v1/pets/<id>/` |
| Delete pet | `/pet/delete/<id>/` | `DELETE /api/v1/pets/<id>/` |
| Add weight record | `/pet/<id>/weight/add/` | — |

### Age Tracking

- FAMMO calculates the pet's **birth date** from the age entered at registration plus the registration date.
- **Current age** (years / months / weeks / days) is automatically recalculated as time passes.
- **Age categories** (e.g., Puppy → Junior → Adult → Senior) are species-specific and update automatically via a daily Celery task (runs at 02:00 UTC).
- Every age category transition is recorded in `PetAgeHistory`.
- `AgeTransitionRule` defines the threshold (in months) per pet type.

### Weight Tracking

- Every new weight entry is saved to a time-series log.
- The most recent weight automatically updates the pet's current weight field.
- The system sends **weight reminder notifications** at intervals tailored by species and age category (every 7–30 days).
- A weekly Celery task (Monday 03:00 UTC) creates condition snapshot records for longitudinal tracking.

### Audit Trail

Every change to key pet fields (weight, body type, activity level, health issues) is logged in `PetDataChangeLog` with: field name, old value, new value, who changed it, when, and the reason.

### Reference Data (Lookup Lists)

All dropdown options are available via API for mobile app use:

```
GET /api/v1/pet-types/
GET /api/v1/breeds/?pet_type=<id>
GET /api/v1/genders/
GET /api/v1/age-categories/?pet_type=<id>
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

## 7. AI Nutrition & Health Features

All AI features are powered by **OpenAI GPT-4o** with structured Pydantic output to ensure reliable, parseable responses.

### AI Meal Recommendations

FAMMO generates a personalised **daily feeding plan** for each pet based on their full profile.

**Output includes:**
- Daily Energy Requirement (DER) in kcal
- Macronutrient targets (protein, fat, carbohydrates, fibre)
- 3–5 specific meal options with ingredients and portions
- Feeding schedule (how many meals per day, timing)
- Safety notes and foods to avoid given the pet's health conditions

**Access:**
- Web: pet detail page → "Get Meal Plan" → `/pet/<id>/calories/calculator/`
- API: `POST /api/v1/ai/recommendations/`

**Monthly limits by plan:**

| Plan | Meal Plans / Month |
|---|---|
| Essentials (free) | 3 |
| Wellness | 5 |
| Optimal | Unlimited |

### AI Health Reports

A comprehensive health assessment covering:
- Overall health summary
- Breed-specific risk factors
- Weight and diet analysis
- Activity level recommendations
- Flags / alerts for concerning combinations (e.g., obesity + low activity + joint issues)
- Personalised next steps

**Access:**
- Web: pet detail page → "Health Report"
- API: `POST /api/v1/ai/health-reports/`

**Monthly limits by plan:**

| Plan | Health Reports / Month |
|---|---|
| Essentials (free) | 1 |
| Wellness | 3 |
| Optimal | Unlimited |

### Usage Tracking

- Counters are stored in `AIUsage` per user per month.
- They **reset automatically on the 1st of every month**.
- Admin and superuser accounts are **always unlimited**, regardless of plan.
- When a limit is reached, the user sees an upgrade prompt.
- All AI predictions are logged to `NutritionPredictionLog` (in the `ai_core` app) for training FAMMO's own proprietary ML models. Logged fields include: species, life stage, breed size, health goal, weight, age, body condition score, full input/output payloads, and which backend was used.

### AI Backend Switching

FAMMO supports two AI backends, switchable via the `FAMMO_AI_BACKEND` environment variable:
- `openai` (default) — uses OpenAI GPT-4o
- `proprietary` — uses FAMMO's own trained in-house models (scikit-learn pipeline in the `ml/` directory)

---

## 8. AI Chat Assistant

An intelligent pet-care advisor available at `/chat/` (web) and `POST /api/v1/chat/send/` (API).

### Key Features

- **Multimodal** — accepts both text messages and image uploads (e.g., photos of skin conditions, food labels).
- **Pet-aware context** — the user's registered pet profiles are automatically included in every AI prompt so the assistant can give personalised, species/breed/health-specific advice.
- **Session management** — each conversation is a `ChatSession`. A user can have multiple sessions but only one is "active" at a time.
- **Auto-titled sessions** — the session title is set to the first 50 characters of the user's first message.
- **Image lifecycle** — uploaded images are stored for 7 days, then automatically cleaned up to save storage.

### Chat API

| Action | Method | Endpoint |
|---|---|---|
| List all sessions | GET | `/api/v1/chat/sessions/` |
| Start new session | POST | `/api/v1/chat/sessions/new/` |
| Get active session | GET | `/api/v1/chat/active/` |
| Send message | POST | `/api/v1/chat/send/` |
| View message history | GET | `/api/v1/chat/sessions/<id>/messages/` |
| Clear session messages | POST | `/api/v1/chat/sessions/<id>/clear/` |
| Delete session | DELETE | `/api/v1/chat/sessions/<id>/` |
| Delete single message | DELETE | `/api/v1/chat/messages/<id>/` |

---

## 9. Veterinary Clinics

### Registering a Clinic (Vet Owner)

1. Go to `/vets/register/` or use `POST /api/v1/clinics/register/` (the API endpoint registers both the user account and clinic in one request).
2. A **confirmation email** is sent to the clinic's email address.
3. Vet clicks the confirmation link — the clinic is now email-confirmed.
4. An **admin reviews and approves** the clinic.
5. Once approved, the clinic appears in the public directory and on the map.

**A clinic must have both `email_confirmed = True` AND `admin_approved = True` to be publicly listed.**

### Clinic Profile Fields

| Category | Fields |
|---|---|
| Identity | Name (unique), slug (auto-generated), logo image, bio |
| Contact | Phone, email, website URL, Instagram handle/URL |
| Location | City, address, latitude, longitude (auto-geocoded via Google Maps API) |
| Schedule | Working hours per day of week (open time, close time, or "Closed") |
| Specializations | Free-text comma-separated (e.g., "Cats, Dogs, Nutrition, Surgery") |
| Status | `is_verified`, `email_confirmed`, `admin_approved`, EOI flag |
| Vet details | Vet name, degrees (e.g., DVM, MSc), certifications — stored in linked `VetProfile` |

### Vet Dashboard

Clinic owners access their management dashboard at `/vets/dashboard/`:

| Section | URL | What it shows |
|---|---|---|
| Overview | `/vets/dashboard/` | KPIs: total appointments, upcoming, by status |
| Edit profile | `/vets/dashboard/profile/` | Update all clinic details |
| Appointments | `/vets/dashboard/appointments/` | Full appointment list with filters |
| Update appointment | `/vets/dashboard/appointments/<id>/update/` | Change status, add notes |
| Referrals | `/vets/dashboard/referrals/` | Users who signed up via the clinic's link |
| Analytics | `/vets/dashboard/analytics/` | Charts for bookings, referrals |
| Notifications | `/vets/dashboard/notifications/` | In-app alerts for new appointments, etc. |

### Referral Programme

Each confirmed clinic gets a unique referral code (e.g., `vet-happypaws`). The clinic shares the link `/vets/ref/<code>/`, which pre-fills the user registration form. `ReferredUser` records track: which user signed up, via which code, and the current relationship status (`NEW / ACTIVE / INACTIVE`).

### Clinic Finder (Public)

| Action | URL / API |
|---|---|
| Browse directory | `/vets/clinics/` |
| View clinic page | `/vets/clinic/<slug>/` |
| Find nearby (map) | `/vets/find/` |
| API: nearby by GPS | `GET /api/v1/vets/api/nearby-clinics/?lat=&lon=` |
| API: search by city | `GET /api/v1/vets/api/clinics-by-city/?city=` |
| API: detect city from IP | `GET /api/v1/vets/api/location/ip/` |

---

## 10. Appointment Booking

### How a Pet Owner Books

1. Find a clinic via the map or directory.
2. Select an **appointment reason** (Annual Checkup, Vaccination, Emergency, Dental, Nutrition Consultation, …).
3. Pick a **date** from available dates in the next 90 days.
4. Pick a **time slot** (30-minute slots generated from the clinic's working hours schedule).
5. Select which **pet** the appointment is for and add optional notes.
6. Submit — appointment is created with status `PENDING`.
7. Receive a confirmation notification when the clinic confirms.

### Appointment Statuses

```
PENDING  →  CONFIRMED  →  COMPLETED
                       →  NO_SHOW
         →  CANCELLED_USER
         →  CANCELLED_CLINIC
```

### Pet Owner Actions

| Action | Web URL | API |
|---|---|---|
| Book appointment | `/vets/clinic/<slug>/book/` | `POST /api/v1/appointments/` |
| View my appointments | `/vets/my-appointments/` | `GET /api/v1/appointments/my/` |
| View appointment detail | `/vets/appointment/<id>/` | `GET /api/v1/appointments/<id>/` |
| Cancel appointment | `/vets/appointment/<id>/cancel/` | `POST /api/v1/appointments/<id>/cancel/` |
| Get available dates | — | `GET /api/v1/clinics/<id>/available-dates/` |
| Get available time slots | `/vets/clinic/<slug>/available-slots/` | `GET /api/v1/clinics/<id>/available-slots/` |

### Vet / Clinic Owner Actions

| Action | Web URL | API |
|---|---|---|
| View all clinic appointments | `/vets/dashboard/appointments/` | `GET /api/v1/clinics/<id>/appointments/` |
| Confirm appointment | Via dashboard | `PUT /api/v1/clinics/<id>/appointments/<appt_id>/` |
| Mark completed / no-show | Via dashboard | Same PUT endpoint |
| Cancel appointment | Via dashboard | Same PUT endpoint |
| Add private clinic notes | Via dashboard | `clinic_notes` field in PUT |
| List appointment reasons | — | `GET /api/v1/appointments/reasons/` |

---

## 11. Subscription Plans

| Feature | Essentials (Free) | Wellness | Optimal |
|---|---|---|---|
| Max pets | 1 | 2 | 5 |
| AI meal plans / month | 3 | 5 | Unlimited |
| AI health reports / month | 1 | 3 | Unlimited |
| AI chat | Yes | Yes | Yes |
| Clinic finder & booking | Yes | Yes | Yes |
| Forum & blog | Yes | Yes | Yes |
| Price | Free | — | — |

- Browse plans: `/subscription/plans/`
- Plan upgrades are processed via `SubscriptionTransaction` records (payment gateway integration ready).
- AI usage counters reset on the **1st of every month**.
- Admins/superusers are always unlimited.

---

## 12. Blog

### Reading the Blog (All Users)

| Action | URL |
|---|---|
| Browse all posts | `/blog/` |
| Filter by category | `/blog/?category=<slug>` |
| Search (title, content, author) | `/blog/?search=<query>` |
| Sort | `/blog/?sort=newest\|oldest\|views\|comments\|rating` |
| Read a post | `/blog/<slug>/` |
| Rate a post (1–5 stars) | `/blog/<slug>/rate/` |
| Leave a comment | `/blog/<slug>/comment/` |

Features: pagination (9 per page), view counter, average star rating, category badges, Open Graph images, per-post SEO metadata (meta description, keywords, canonical URL).

Blog posts support:
- 4 languages: English, Turkish, Dutch, Finnish
- Markdown content with syntax highlighting, tables, and inline image uploads

### AI-Powered Blog Generation (Staff Only)

FAMMO includes an end-to-end AI content pipeline:

1. **Admin creates a `BlogTopic`** with: title, primary keyword, secondary keywords, target audience, tone (professional / casual / friendly / authoritative), language, and optional notes.
2. **Trigger AI generation** — GPT-4o writes a full SEO-optimised blog post.
3. **AI also drafts** a LinkedIn post (600–1200 characters) and an X/Twitter post (≤280 characters) for each article.
4. **Staff reviews** the generated draft and publishes it.

| Action | URL |
|---|---|
| Blog dashboard | `/blog/dashboard/` |
| Create topic | `/blog/dashboard/topics/create/` |
| Generate post from topic | `/blog/dashboard/topics/<id>/generate/` |
| Manual generation | `/blog/dashboard/generate/` |
| View generation requests | `/blog/dashboard/requests/` |
| Publish / unpublish | `/blog/dashboard/posts/<id>/publish\|unpublish/` |
| Delete post | `/blog/dashboard/posts/<id>/delete/` |

---

## 13. Community Forum (Q&A)

A StackOverflow-style community for pet owners.

### For All Users

| Action | URL |
|---|---|
| Browse questions | `/forum/` |
| Filter by category | `/forum/?category=<cat>` |
| Sort (newest / most votes / unanswered) | `/forum/?sort=...` |
| View question + answers | `/forum/question/<id>/` |
| Ask a question (login required) | `/forum/ask/` |
| Answer a question (login required) | From question detail page |
| Upvote / downvote (AJAX) | `/forum/vote/<type>/<id>/<up\|down>/` |
| Mark best answer (question author) | `/forum/answer/<id>/accept/` |

**Question categories:** Dog Health · Cat Health · Dog Behavior · Cat Behavior · Nutrition & Diet · Training · Grooming · Veterinary Care · Adoption & Rescue · General

**Features:**
- Questions support an optional photo (auto-compressed to <1 MB and converted to JPEG).
- Upvote/downvote system creates a simple reputation mechanism.
- A question author can mark one answer as "accepted" (displayed prominently).
- View counter tracks question popularity.

---

## 14. Notifications

### In-App Notifications (Pet Owners)

| Type | When it fires |
|---|---|
| `APPOINTMENT_CONFIRMED` | Clinic confirms the booking |
| `APPOINTMENT_CANCELLED` | Either side cancels |
| `APPOINTMENT_REMINDER` | Before an upcoming appointment |
| `EMAIL_CONFIRMATION` | At account registration |
| `PET_REMINDER` | Weight update reminder (species/age-based interval) |
| `NEW_REFERRAL` | A new user signs up via the clinic's referral link |
| `ADMIN_MESSAGE` | Manual message sent by a staff member |
| `SYSTEM` | System-level events |

| Action | Web | API |
|---|---|---|
| View all | `/notifications/` | `GET /api/v1/notifications/` |
| Mark one read | `/notifications/<id>/read/` | `POST /api/v1/notifications/<id>/read/` |
| Mark all read | `/notifications/mark-all-read/` | `POST /api/v1/notifications/mark-all-read/` |
| Delete | `/notifications/<id>/delete/` | `DELETE /api/v1/notifications/<id>/` |
| Unread count (badge) | — | `GET /api/v1/notifications/unread-count/` |

### Clinic Notifications

Clinics have a separate notification inbox accessible at `/vets/dashboard/notifications/` and `GET /api/v1/clinics/notifications/`.

### Push Notifications (Mobile)

FAMMO uses **Firebase Cloud Messaging (FCM)** for push notifications on Android, iOS, and web.

| Action | API |
|---|---|
| Register device token | `POST /api/v1/users/register-device/` |
| Unregister device token | `POST /api/v1/users/unregister-device/` |

Multiple devices per user are supported.

### Admin Telegram Alerts

Key platform events (new user registered, new clinic, new forum question, new subscription) are sent as real-time Telegram messages to an admin channel. These are logged in `NotificationLog` with status (sent / failed) and any error details.

---

## 15. Legal & Compliance (GDPR)

| Feature | Detail |
|---|---|
| **Account deletion** | GDPR-compliant 30-day grace period, full audit trail in `AccountDeletionRequest` |
| **Legal documents** | Terms of Service, Privacy Policy, Cookie Policy — versioned per language |
| **User consent** | IP address, user-agent, and timestamp recorded when a user accepts any legal document |
| **Clinic consent** | Same tracking for clinics accepting clinic-specific terms |
| **Consent audit log** | Every acceptance is appended to `ConsentLog` — never overwritten |
| **Location consent** | `location_consent` boolean must be `true` before any coordinates are saved |

**Legal pages:**
- `/privacy-policy/`
- `/terms/`
- `/vets/clinic-terms/`
- `/vets/clinic-partnership/`
- `/vets/eoi-terms/`

**Legal API:**
```
GET  /api/v1/legal/documents/        # Active legal documents
GET  /api/v1/legal/consent/user/     # User's consent records
GET  /api/v1/legal/consent/clinic/   # Clinic's consent records
GET  /api/v1/legal/logs/             # Full consent audit log
```

---

## 16. Admin Features

FAMMO provides a custom admin dashboard at `/admin-dashboard/` (in addition to Django's built-in `/admin/`):

| Feature | Description |
|---|---|
| **KPI Dashboard** | Charts and counters for total users, pets, appointments, blog posts, and subscriptions |
| **Clinic approval** | Review new clinic registrations; approve or reject with one click |
| **Blog management** | Manage the AI topic queue, trigger generation, publish/unpublish posts |
| **User management** | View and search all users; export as CSV |
| **Pet data export** | Export all pet records as CSV |
| **Translation management** | Manage multilingual UI strings at `/translations/` |
| **Email template previews** | Preview every transactional email in the browser before sending |
| **Admin messaging** | Push an `ADMIN_MESSAGE` notification to any user |
| **Legal document versioning** | Create and activate new versions of Terms, Privacy Policy, etc. |
| **Consent audit** | View the full consent log for any user or clinic |
| **Account deletion review** | Approve or postpone pending deletion requests |

---

## 17. Mobile & REST API Reference

All functionality is exposed under the versioned prefix `/api/v1/`. Authentication uses JWT Bearer tokens.

### Authentication
```
POST /api/v1/auth/signup/
POST /api/v1/auth/login/
POST /api/v1/auth/google/
POST /api/v1/auth/forgot-password/
POST /api/v1/auth/reset-password/
POST /api/v1/auth/change-password/
POST /api/v1/auth/resend-activation/
```

### User & Profile
```
GET | PUT | PATCH  /api/v1/profile/me/
POST               /api/v1/users/api/save-location/
POST               /api/v1/users/register-device/
POST               /api/v1/users/unregister-device/
POST               /api/v1/languages/set/
```

### Pet Reference Data
```
GET  /api/v1/pet-types/
GET  /api/v1/breeds/?pet_type=<id>
GET  /api/v1/genders/
GET  /api/v1/age-categories/?pet_type=<id>
GET  /api/v1/food-types/
GET  /api/v1/food-feelings/
GET  /api/v1/food-importance/
GET  /api/v1/body-types/
GET  /api/v1/activity-levels/
GET  /api/v1/food-allergies/
GET  /api/v1/health-issues/
GET  /api/v1/treat-frequencies/
```

### Pets (CRUD)
```
GET  | POST          /api/v1/pets/
GET  | PUT | DELETE  /api/v1/pets/<id>/
```

### AI Features
```
POST  /api/v1/ai/recommendations/     # Generate meal plan for a pet
POST  /api/v1/ai/health-reports/      # Generate health report for a pet
```

### AI Chat
```
GET  | POST    /api/v1/chat/sessions/
POST           /api/v1/chat/sessions/new/
GET  | DELETE  /api/v1/chat/sessions/<id>/
GET            /api/v1/chat/sessions/<id>/messages/
POST           /api/v1/chat/sessions/<id>/clear/
POST           /api/v1/chat/send/
GET            /api/v1/chat/active/
DELETE         /api/v1/chat/messages/<id>/
```

### Clinics & Vets
```
GET  | POST          /api/v1/clinics/
GET                  /api/v1/clinics/my/
GET  | PUT | DELETE  /api/v1/clinics/<id>/
POST                 /api/v1/clinics/register/
POST                 /api/v1/clinics/search/
GET                  /api/v1/clinics/<id>/working-hours/
GET  | PUT           /api/v1/clinics/<id>/vet-profile/
POST                 /api/v1/clinics/send-confirmation-email/
GET                  /api/v1/clinics/confirm-email/<token>/
GET                  /api/v1/vets/api/nearby-clinics/
GET                  /api/v1/vets/api/clinics-by-city/
GET                  /api/v1/vets/api/location/ip/
```

### Clinic Notifications
```
GET   /api/v1/clinics/notifications/
GET   /api/v1/clinics/notifications/unread-count/
```

### Appointments
```
GET  | POST  /api/v1/appointments/
GET          /api/v1/appointments/my/
GET          /api/v1/appointments/<id>/
POST         /api/v1/appointments/<id>/cancel/
GET          /api/v1/appointments/reasons/
GET          /api/v1/clinics/<id>/available-dates/
GET          /api/v1/clinics/<id>/available-slots/
GET          /api/v1/clinics/<id>/appointments/
PUT          /api/v1/clinics/<id>/appointments/<appt_id>/
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
GET          /api/v1/blog/categories/
GET  | POST  /api/v1/blog/posts/
GET  | PUT | DELETE  /api/v1/blog/posts/<id>/
```

### Legal
```
GET  /api/v1/legal/documents/
GET  /api/v1/legal/consent/user/
GET  /api/v1/legal/consent/clinic/
GET  /api/v1/legal/logs/
```

### App Config & Onboarding
```
GET  /api/v1/config/          # App config: base URLs, logos, assets
GET  /api/v1/onboarding/      # Onboarding slides for the mobile app
GET  /api/v1/languages/       # Supported languages list
```

---

## 18. Multi-language Support

FAMMO supports 4 languages:

| Language | Code | URL prefix |
|---|---|---|
| English | `en` | `/` (no prefix — default) |
| Turkish | `tr` | `/tr/` |
| Dutch | `nl` | `/nl/` |
| Finnish | `fi` | `/fi/` |

- The user's **preferred language** is stored in their profile and used in the mobile app.
- Users set their language via profile settings or `POST /api/v1/languages/set/`.
- **Blog posts** are authored per-language — each post has a `language` field.
- **Model fields** that need translation (e.g., `OnboardingSlide.title`) use `django-modeltranslation`.
- **UI strings** use Django's standard `{% trans %}` / `gettext` system with `.po` files in `locale/`.

---

## 19. Data Model Overview

```
CustomUser ─(1:1)─ Profile ─(FK)─ SubscriptionPlan
     │
     ├─(1:N)─ Pet ─(1:N)─ WeightRecord
     │          ├─(1:N)─ AIRecommendation   (meal plans)
     │          ├─(1:N)─ AIHealthReport
     │          └─(1:N)─ PetAgeHistory
     │
     ├─(1:N)─ ChatSession ─(1:N)─ ChatMessage
     │
     ├─(1:N)─ Question ─(1:N)─ Answer
     │                  └─(1:N)─ Vote
     │
     ├─(1:N)─ Notification
     │
     ├─(1:1)─ AccountDeletionRequest
     │
     ├─(1:N)─ AIUsage              (monthly counters per user)
     │
     └─(FK from Clinic)─ owned_clinics

Clinic ─(1:1)─ VetProfile
        ├─(1:N)─ WorkingHours
        ├─(1:N)─ ReferralCode ─(1:N)─ ReferredUser
        └─(1:N)─ Appointment
                      └── (FK to Pet, FK to CustomUser)

NutritionPredictionLog   (standalone — no FK to Pet/User, JSON snapshots)
BlogPost ─(M2M)─ BlogCategory
BlogTopic ──────── BlogGenerationRequest ─(FK)─ BlogPost
```

---

## 20. Deployment & Infrastructure

### Environment Configuration

FAMMO uses `python-decouple` and `python-dotenv`. All secrets and environment-specific settings live in a `.env` file:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for development, `False` in production |
| `SITE_URL` | Full URL (e.g., `https://fammo.ai`) |
| `OPENAI_API_KEY` | OpenAI API key |
| `FAMMO_AI_BACKEND` | `openai` or `proprietary` |
| `GOOGLE_MAPS_API_KEY` | For clinic geocoding |
| `TELEGRAM_BOT_TOKEN` | Admin alert bot |
| `TELEGRAM_CHANNEL_ID` | Target Telegram channel |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST_LOCAL` | MySQL credentials (production) |
| `USE_MYSQL` | `True` to force MySQL (without `IS_CPANEL`) |
| `CELERY_BROKER_URL` | Redis URL (default: `redis://localhost:6379/0`) |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase service account JSON |
| `ENABLE_PLAYWRIGHT_SCREENSHOTS` | `False` on servers without Playwright dependencies |

### Database Strategy

| Environment | Database |
|---|---|
| Local development | SQLite (`db.sqlite3`) |
| Test suite | SQLite (`test_db.sqlite3`) |
| cPanel / production | MySQL (utf8mb4) |

### Celery Scheduled Tasks

| Task | Schedule | What it does |
|---|---|---|
| `pet.tasks.update_pet_age_categories` | Daily at 02:00 UTC | Updates age categories for all pets based on current date |
| `pet.tasks.create_weekly_condition_snapshots` | Monday at 03:00 UTC | Saves weekly health condition snapshots for longitudinal tracking |
| `core.tasks.create_weight_update_notifications` | Daily at 01:30 UTC | Creates weight reminder notifications for pets due for a weigh-in |

### Static & Media Files

| Setting | Development | cPanel (production) |
|---|---|---|
| `STATIC_URL` | `/static/` | `fammo/static/` |
| `MEDIA_URL` | `/media/` | `/fammo/media/` |
| `STATIC_ROOT` | `staticfiles/` | `staticfiles/` |
| `MEDIA_ROOT` | `media/` | `media/` |

### Email

Transactional emails (account activation, clinic confirmation, password reset) are sent via Gmail SMTP:
- Host: `smtp.gmail.com`, Port: 587, TLS enabled
- From: `FAMO <fammo.ai.official@gmail.com>`

---

*This document was auto-generated from the FAMMO codebase on May 14, 2026.*
