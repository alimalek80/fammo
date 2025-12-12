# Legal Documents and Consent Management System

## Overview

A complete backend system for managing legal documents (Terms & Conditions, Privacy Policies, Agreements) and tracking user/clinic consent. This enables:

1. **Admin Management**: Create, edit, and version legal documents
2. **Multi-language Support**: Same document in multiple languages
3. **Audit Trail**: Track all consent events with IP, user agent, and timestamps
4. **Compliance Reporting**: Check if users/clinics have accepted required documents
5. **API Endpoints**: For both mobile apps and web interfaces

---

## Models

### 1. LegalDocument
Stores the actual legal document content with versioning support.

**Fields:**
- `doc_type` - Type of document (user_terms, user_privacy, clinic_terms, clinic_partnership, clinic_eoi)
- `language` - Language code (en, fi, nl, tr, etc.)
- `title` - Document title
- `version` - Version identifier
- `content` - Full legal text (HTML allowed)
- `summary` - Brief summary
- `is_active` - Is this the current active version?
- `effective_date` - When this version takes effect
- `admin_notes` - Internal notes

**Usage:**
```python
# Create a new terms document
LegalDocument.objects.create(
    doc_type='user_terms',
    language='en',
    title='Terms and Conditions v2.0',
    version='2.0',
    content='<h1>Terms...</h1>',
    is_active=True,
    effective_date=timezone.now()
)

# Get latest active document
doc = LegalDocument.objects.get(
    doc_type='user_terms',
    language='en',
    is_active=True
)
```

---

### 2. UserConsent
Tracks when users accept documents during registration or later.

**Fields:**
- `user` - ForeignKey to CustomUser
- `document` - ForeignKey to LegalDocument
- `accepted` - Whether user accepted (True) or revoked (False)
- `accepted_at` - When they accepted
- `ip_address` - IP address for audit
- `user_agent` - Browser info for audit

**Usage:**
```python
# Record user acceptance
UserConsent.objects.create(
    user=user,
    document=terms_doc,
    accepted=True,
    ip_address='192.168.1.1',
    user_agent='Mozilla/5.0...'
)

# Check if user accepted document
has_accepted = UserConsent.objects.filter(
    user=user,
    document=doc,
    accepted=True
).exists()
```

---

### 3. ClinicConsent
Same as UserConsent but for clinics during clinic registration.

**Fields:**
- `user` - ForeignKey to CustomUser (clinic owner)
- `document` - ForeignKey to LegalDocument
- `clinic_email` - Email of clinic (for audit trail)
- `accepted` - Whether clinic accepted
- `accepted_at` - When they accepted
- `ip_address` - IP address for audit
- `user_agent` - Browser info for audit

**Usage:**
```python
# Record clinic acceptance
ClinicConsent.objects.create(
    user=request.user,
    document=clinic_terms,
    clinic_email='clinic@example.com',
    accepted=True,
    ip_address='192.168.1.1'
)
```

---

### 4. ConsentLog
Audit log for all consent-related activities.

**Fields:**
- `action` - Type of action (created, updated, accepted, revoked, reminded)
- `document` - ForeignKey to LegalDocument
- `user` - ForeignKey to user (nullable)
- `details` - Description of action
- `timestamp` - When it happened
- `admin_user` - Who made the change (for admin actions)

**Usage:**
```python
# Log a consent action
ConsentLog.objects.create(
    action='accepted',
    document=doc,
    user=user,
    details='User accepted terms during registration'
)
```

---

## API Endpoints

### Get Legal Documents

**Endpoint:** `GET /api/v1/legal/documents/`

Returns list of all active legal documents (public access).

**Query Parameters:**
- `doc_type` - Filter by document type
- `language` - Filter by language
- `page` - Page number for pagination

**Example:**
```bash
# Get all English terms documents
GET /api/v1/legal/documents/?doc_type=user_terms&language=en

# Get all clinic partnership agreements
GET /api/v1/legal/documents/?doc_type=clinic_partnership
```

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "doc_type": "user_terms",
      "doc_type_display": "User Terms and Conditions",
      "language": "en",
      "title": "Terms and Conditions v2.0",
      "version": "2.0",
      "content": "<h1>Terms...</h1>",
      "summary": "Our terms of service",
      "effective_date": "2024-01-01T00:00:00Z",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

### Get Specific Document by Type

**Endpoint:** `GET /api/v1/legal/documents/by_type/`

Get the latest active document by type and language.

**Query Parameters:**
- `doc_type` (required) - Document type
- `language` (optional, default: en) - Language code

**Example:**
```bash
GET /api/v1/legal/documents/by_type/?doc_type=user_terms&language=fi
```

**Response:**
```json
{
  "id": 2,
  "doc_type": "user_terms",
  "doc_type_display": "User Terms and Conditions",
  "language": "fi",
  "title": "Käyttöehdot v2.0",
  "version": "2.0",
  "content": "<h1>Käyttöehdot...</h1>",
  "effective_date": "2024-01-01T00:00:00Z"
}
```

---

### List Available Document Types

**Endpoint:** `GET /api/v1/legal/documents/available_types/`

Returns all available document types.

**Response:**
```json
[
  {"value": "user_terms", "label": "User Terms and Conditions"},
  {"value": "user_privacy", "label": "User Privacy Policy"},
  {"value": "clinic_terms", "label": "Clinic Terms and Conditions"},
  {"value": "clinic_partnership", "label": "Clinic Partnership Agreement"},
  {"value": "clinic_eoi", "label": "Expression of Interest (EOI) Terms"}
]
```

---

### Record User Consent

**Endpoint:** `POST /api/v1/legal/consent/user/`

Records that user has accepted a legal document. Requires authentication.

**Request:**
```json
{
  "document": 1,
  "accepted": true
}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 5,
  "document": 1,
  "document_title": "Terms and Conditions v2.0",
  "document_type": "user_terms",
  "accepted": true,
  "accepted_at": "2024-11-15T10:30:00Z"
}
```

---

### Get User's Consent History

**Endpoint:** `GET /api/v1/legal/consent/user/`

Get all consent records for the authenticated user. Requires authentication.

**Query Parameters:**
- `page` - Page number

**Example:**
```bash
GET /api/v1/legal/consent/user/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 5,
      "document": 1,
      "document_title": "Terms and Conditions v2.0",
      "document_type": "user_terms",
      "accepted": true,
      "accepted_at": "2024-11-15T10:30:00Z"
    },
    {
      "id": 6,
      "document": 2,
      "document_title": "Privacy Policy v1.0",
      "document_type": "user_privacy",
      "accepted": true,
      "accepted_at": "2024-11-15T10:30:00Z"
    }
  ]
}
```

---

### Check User Compliance

**Endpoint:** `GET /api/v1/legal/consent/user/check_compliance/`

Check if user has accepted all required documents.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "compliant": true,
  "missing_documents": [],
  "accepted_documents": ["user_terms", "user_privacy"]
}
```

---

### Record Clinic Consent

**Endpoint:** `POST /api/v1/legal/consent/clinic/`

Records that clinic has accepted a legal document. Requires authentication.

**Request:**
```json
{
  "document": 3,
  "clinic_email": "clinic@example.com",
  "accepted": true
}
```

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 7,
  "document": 3,
  "document_title": "Clinic Terms and Conditions v2.0",
  "document_type": "clinic_terms",
  "clinic_email": "clinic@example.com",
  "accepted": true,
  "accepted_at": "2024-11-15T10:30:00Z"
}
```

---

### Get Clinic Consent History

**Endpoint:** `GET /api/v1/legal/consent/clinic/`

Get all consent records for clinics owned by authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

---

### Check Clinic Compliance

**Endpoint:** `GET /api/v1/legal/consent/clinic/check_compliance/`

Check if a clinic has accepted all required documents.

**Query Parameters:**
- `clinic_email` (required) - Email of clinic to check

**Example:**
```bash
GET /api/v1/legal/consent/clinic/check_compliance/?clinic_email=clinic@example.com
```

**Response:**
```json
{
  "compliant": true,
  "missing_documents": [],
  "accepted_documents": ["clinic_terms", "clinic_partnership"]
}
```

---

### View Consent Audit Logs (Admin Only)

**Endpoint:** `GET /api/v1/legal/logs/`

View all consent audit logs. Requires admin privileges.

**Query Parameters:**
- `action` - Filter by action type (created, updated, accepted, revoked, reminded)
- `doc_type` - Filter by document type
- `page` - Page number

**Example:**
```bash
GET /api/v1/legal/logs/?action=accepted&doc_type=user_terms
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "action": "accepted",
      "action_display": "Consent Accepted",
      "document": 1,
      "document_title": "Terms and Conditions v2.0",
      "user": 5,
      "user_email": "user@example.com",
      "admin_user": null,
      "admin_email": null,
      "details": "User accepted terms during registration",
      "timestamp": "2024-11-15T10:30:00Z"
    }
  ]
}
```

---

## Integration with Registration

### User Registration Flow

1. **Frontend gets documents:**
   ```javascript
   // Get terms and privacy policy
   GET /api/v1/legal/documents/by_type/?doc_type=user_terms&language=en
   GET /api/v1/legal/documents/by_type/?doc_type=user_privacy&language=en
   ```

2. **User signs up (with checkbox acceptance):**
   ```javascript
   POST /api/v1/auth/signup/
   {
     "email": "user@example.com",
     "password": "...",
     "agree_terms": true  // From checkbox
   }
   ```

3. **Backend records consent:**
   ```python
   # In SignupView
   user = ...  # Create user
   
   # Record consent to terms
   terms_doc = LegalDocument.objects.get(doc_type='user_terms', language=user_language, is_active=True)
   UserConsent.objects.create(
       user=user,
       document=terms_doc,
       accepted=True,
       ip_address=get_client_ip(request),
       user_agent=request.META.get('HTTP_USER_AGENT', '')
   )
   ```

### Clinic Registration Flow

1. **Frontend gets clinic documents:**
   ```javascript
   GET /api/v1/legal/documents/by_type/?doc_type=clinic_terms&language=en
   GET /api/v1/legal/documents/by_type/?doc_type=clinic_partnership&language=en
   GET /api/v1/legal/documents/by_type/?doc_type=clinic_eoi&language=en
   ```

2. **Clinic registers (with checkboxes):**
   ```javascript
   POST /api/v1/clinics/register/
   {
     "name": "Clinic Name",
     "email": "clinic@example.com",
     "agree_clinic_terms": true,
     "agree_partnership": true,
     "clinic_eoi": false
   }
   ```

3. **Backend records consent:**
   ```python
   # In ClinicRegistrationView
   clinic = ...  # Create clinic
   
   # Record consent to clinic terms
   clinic_terms = LegalDocument.objects.get(doc_type='clinic_terms', is_active=True)
   ClinicConsent.objects.create(
       user=request.user,
       document=clinic_terms,
       clinic_email=clinic.email,
       accepted=True,
       ip_address=get_client_ip(request)
   )
   ```

---

## Admin Panel

All models are registered in Django admin for easy management:

1. **Legal Documents** - Create/edit/version legal documents
2. **User Consent** - View which users accepted which documents
3. **Clinic Consent** - View which clinics accepted which documents
4. **Consent Logs** - Audit trail of all consent activities

---

## Database Migrations

Create migrations for the new models:

```bash
python manage.py makemigrations core
python manage.py migrate core
```

---

## Example: Creating Documents via Admin

1. Go to Django Admin → Legal Documents
2. Click "Add Legal Document"
3. Fill in:
   - Document Type: "User Terms and Conditions"
   - Language: "en"
   - Title: "Terms and Conditions v2.0"
   - Version: "2.0"
   - Content: [Paste full HTML content]
   - Is Active: ✓
   - Effective Date: [Today]
4. Save

---

## Benefits

✅ **Compliance**: Audit trail of all user/clinic acceptances
✅ **Multi-language**: Same documents in different languages
✅ **Versioning**: Track document versions and changes
✅ **Easy Updates**: Change documents without code changes
✅ **API-driven**: Mobile apps can fetch and display documents
✅ **Admin Control**: Full control via Django admin panel
✅ **Security**: Tracks IP and user agent for fraud prevention

---

## Next Steps

1. Run migrations to create tables
2. Create initial legal documents in Django admin
3. Update registration views to call consent endpoints
4. Test with API endpoints
5. Deploy to production
