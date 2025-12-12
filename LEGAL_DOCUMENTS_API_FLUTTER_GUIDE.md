# FAMMO Legal Documents API - Flutter Integration Guide

## Overview

FAMMO provides a comprehensive legal documents system with multi-language support for:
- **User Terms and Conditions** - For pet owners using the app
- **User Privacy Policy** - Privacy terms for users
- **Clinic Terms and Conditions** - For veterinary clinics
- **Clinic Partnership Agreement** - Partnership terms for clinics
- **Expression of Interest (EOI) Terms** - For clinics joining pilot program

All documents are **editable via Django admin** and support **multi-language translation** using django-modeltranslation.

---

## API Endpoints

### Base URL
```
https://your-api-domain.com/api/v1/
```

### Authentication
Most endpoints are **public** (no auth required). Consent recording requires **JWT authentication**.

---

## 📄 1. Get All Legal Documents

Retrieve all active legal documents.

**Endpoint:**
```
GET /legal/documents/
```

**Query Parameters:**
- `doc_type` (optional): Filter by document type
  - `user_terms` - User Terms and Conditions
  - `user_privacy` - User Privacy Policy
  - `clinic_terms` - Clinic Terms and Conditions
  - `clinic_partnership` - Clinic Partnership Agreement
  - `clinic_eoi` - Expression of Interest Terms

**Headers:**
- `Accept-Language: en` (optional) - Language code for translated content
  - Supported: `en`, `fi`, `nl`, `tr`

**Example Request:**
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<List<dynamic>> getAllLegalDocuments() async {
  final response = await http.get(
    Uri.parse('https://api.fammo.ai/api/v1/legal/documents/'),
    headers: {
      'Accept-Language': 'en', // Change to user's language
    },
  );

  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    return data['results'];
  } else {
    throw Exception('Failed to load legal documents');
  }
}
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
      "title": "FAMMO User Terms and Conditions",
      "version": "1.0",
      "content": "<h1>FAMMO User Terms and Conditions</h1>...",
      "summary": "Terms and Conditions for FAMMO platform users.",
      "effective_date": "2025-01-15T10:00:00Z",
      "created_at": "2025-01-10T14:30:00Z"
    }
  ]
}
```

---

## 📄 2. Get Specific Document by Type

Retrieve the latest active document of a specific type.

**Endpoint:**
```
GET /legal/documents/by_type/?doc_type=<doc_type>
```

**Query Parameters:**
- `doc_type` (required): Document type identifier

**Example Request:**
```dart
Future<Map<String, dynamic>> getUserTerms(String languageCode) async {
  final response = await http.get(
    Uri.parse('https://api.fammo.ai/api/v1/legal/documents/by_type/?doc_type=user_terms'),
    headers: {
      'Accept-Language': languageCode,
    },
  );

  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Failed to load user terms');
  }
}
```

**Response:**
```json
{
  "id": 1,
  "doc_type": "user_terms",
  "doc_type_display": "User Terms and Conditions",
  "title": "FAMMO User Terms and Conditions",
  "version": "1.0",
  "content": "<h1>FAMMO User Terms and Conditions</h1><p>Last Updated: January 2025</p>...",
  "summary": "Terms and Conditions for FAMMO platform users.",
  "effective_date": "2025-01-15T10:00:00Z",
  "created_at": "2025-01-10T14:30:00Z"
}
```

---

## ✅ 3. Record User Consent

Record when a user accepts a legal document (e.g., during registration).

**Endpoint:**
```
POST /legal/consent/user/
```

**Authentication:** Required (JWT Token)

**Headers:**
- `Authorization: Bearer <access_token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "document": 1,
  "accepted": true
}
```

**Example Request:**
```dart
Future<void> recordUserConsent(String token, int documentId) async {
  final response = await http.post(
    Uri.parse('https://api.fammo.ai/api/v1/legal/consent/user/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'document': documentId,
      'accepted': true,
    }),
  );

  if (response.statusCode != 201) {
    throw Exception('Failed to record consent');
  }
}
```

**Response:**
```json
{
  "id": 42,
  "document": 1,
  "document_title": "FAMMO User Terms and Conditions",
  "document_type": "user_terms",
  "accepted": true,
  "accepted_at": "2025-01-15T12:34:56Z"
}
```

---

## ✅ 4. Record Clinic Consent

Record when a clinic accepts a legal document (e.g., during clinic registration).

**Endpoint:**
```
POST /legal/consent/clinic/
```

**Authentication:** Required (JWT Token)

**Headers:**
- `Authorization: Bearer <access_token>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "document": 3,
  "clinic_email": "clinic@example.com",
  "accepted": true
}
```

**Example Request:**
```dart
Future<void> recordClinicConsent(
  String token,
  int documentId,
  String clinicEmail,
) async {
  final response = await http.post(
    Uri.parse('https://api.fammo.ai/api/v1/legal/consent/clinic/'),
    headers: {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    },
    body: json.encode({
      'document': documentId,
      'clinic_email': clinicEmail,
      'accepted': true,
    }),
  );

  if (response.statusCode != 201) {
    throw Exception('Failed to record clinic consent');
  }
}
```

---

## 🔍 5. Check User Compliance

Check if the current user has accepted all required documents.

**Endpoint:**
```
GET /legal/consent/user/check_compliance/
```

**Authentication:** Required

**Example Request:**
```dart
Future<Map<String, dynamic>> checkUserCompliance(String token) async {
  final response = await http.get(
    Uri.parse('https://api.fammo.ai/api/v1/legal/consent/user/check_compliance/'),
    headers: {
      'Authorization': 'Bearer $token',
    },
  );

  if (response.statusCode == 200) {
    return json.decode(response.body);
  } else {
    throw Exception('Failed to check compliance');
  }
}
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

## 🔍 6. Check Clinic Compliance

Check if a clinic has accepted all required documents.

**Endpoint:**
```
GET /legal/consent/clinic/check_compliance/?clinic_email=<email>
```

**Authentication:** Required

**Query Parameters:**
- `clinic_email` (required): Email of the clinic to check

---

## 📋 7. Get Available Document Types

List all available document types.

**Endpoint:**
```
GET /legal/documents/available_types/
```

**Response:**
```json
[
  {
    "value": "user_terms",
    "label": "User Terms and Conditions"
  },
  {
    "value": "user_privacy",
    "label": "User Privacy Policy"
  },
  {
    "value": "clinic_terms",
    "label": "Clinic Terms and Conditions"
  },
  {
    "value": "clinic_partnership",
    "label": "Clinic Partnership Agreement"
  },
  {
    "value": "clinic_eoi",
    "label": "Expression of Interest (EOI) Terms"
  }
]
```

---

## 🛠️ Flutter Implementation Example

### Complete Legal Documents Service

```dart
// lib/services/legal_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class LegalService {
  final String baseUrl = 'https://api.fammo.ai/api/v1';
  
  // Get user terms
  Future<Map<String, dynamic>> getUserTerms(String languageCode) async {
    final response = await http.get(
      Uri.parse('$baseUrl/legal/documents/by_type/?doc_type=user_terms'),
      headers: {'Accept-Language': languageCode},
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to load user terms');
  }
  
  // Get clinic terms
  Future<Map<String, dynamic>> getClinicTerms(String languageCode) async {
    final response = await http.get(
      Uri.parse('$baseUrl/legal/documents/by_type/?doc_type=clinic_terms'),
      headers: {'Accept-Language': languageCode},
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to load clinic terms');
  }
  
  // Get clinic partnership agreement
  Future<Map<String, dynamic>> getPartnershipAgreement(String languageCode) async {
    final response = await http.get(
      Uri.parse('$baseUrl/legal/documents/by_type/?doc_type=clinic_partnership'),
      headers: {'Accept-Language': languageCode},
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to load partnership agreement');
  }
  
  // Get EOI terms
  Future<Map<String, dynamic>> getEOITerms(String languageCode) async {
    final response = await http.get(
      Uri.parse('$baseUrl/legal/documents/by_type/?doc_type=clinic_eoi'),
      headers: {'Accept-Language': languageCode},
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    }
    throw Exception('Failed to load EOI terms');
  }
  
  // Record user consent
  Future<void> recordUserConsent(String token, int documentId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/legal/consent/user/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'document': documentId,
        'accepted': true,
      }),
    );
    
    if (response.statusCode != 201) {
      throw Exception('Failed to record consent');
    }
  }
  
  // Record clinic consent
  Future<void> recordClinicConsent(
    String token,
    int documentId,
    String clinicEmail,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/legal/consent/clinic/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'document': documentId,
        'clinic_email': clinicEmail,
        'accepted': true,
      }),
    );
    
    if (response.statusCode != 201) {
      throw Exception('Failed to record clinic consent');
    }
  }
}
```

### UI Widget for Terms and Conditions

```dart
// lib/widgets/terms_viewer.dart
import 'package:flutter/material.dart';
import 'package:flutter_html/flutter_html.dart';

class TermsViewer extends StatelessWidget {
  final String title;
  final String htmlContent;
  
  const TermsViewer({
    Key? key,
    required this.title,
    required this.htmlContent,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Html(
          data: htmlContent,
          style: {
            "h1": Style(fontSize: FontSize(24), fontWeight: FontWeight.bold),
            "h2": Style(fontSize: FontSize(20), fontWeight: FontWeight.bold),
            "p": Style(fontSize: FontSize(16), lineHeight: LineHeight(1.5)),
            "ul": Style(padding: HtmlPaddings.only(left: 20)),
            "li": Style(padding: HtmlPaddings.only(bottom: 8)),
          },
        ),
      ),
    );
  }
}
```

### Registration Screen Example

```dart
// lib/screens/registration_screen.dart
import 'package:flutter/material.dart';
import '../services/legal_service.dart';
import '../widgets/terms_viewer.dart';

class RegistrationScreen extends StatefulWidget {
  @override
  _RegistrationScreenState createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final LegalService _legalService = LegalService();
  bool _agreeTerms = false;
  Map<String, dynamic>? _termsDocument;
  
  @override
  void initState() {
    super.initState();
    _loadTerms();
  }
  
  Future<void> _loadTerms() async {
    try {
      final terms = await _legalService.getUserTerms('en');
      setState(() {
        _termsDocument = terms;
      });
    } catch (e) {
      print('Error loading terms: $e');
    }
  }
  
  void _showTerms() {
    if (_termsDocument != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => TermsViewer(
            title: _termsDocument!['title'],
            htmlContent: _termsDocument!['content'],
          ),
        ),
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Register')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            // ... other registration fields ...
            
            CheckboxListTile(
              title: Row(
                children: [
                  Text('I agree to the '),
                  GestureDetector(
                    onTap: _showTerms,
                    child: Text(
                      'Terms and Conditions',
                      style: TextStyle(
                        color: Colors.blue,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ),
                ],
              ),
              value: _agreeTerms,
              onChanged: (value) {
                setState(() {
                  _agreeTerms = value ?? false;
                });
              },
            ),
            
            ElevatedButton(
              onPressed: _agreeTerms ? _register : null,
              child: Text('Sign Up'),
            ),
          ],
        ),
      ),
    );
  }
  
  Future<void> _register() async {
    // After successful registration, record consent
    // await _legalService.recordUserConsent(token, _termsDocument!['id']);
  }
}
```

---

## 🌍 Multi-Language Support

The API automatically returns content in the requested language using the `Accept-Language` header:

```dart
// Get user's locale
import 'dart:io';

String getLanguageCode() {
  final locale = Platform.localeName; // e.g., 'en_US'
  return locale.split('_')[0]; // returns 'en'
}

// Use in API calls
final languageCode = getLanguageCode();
final terms = await legalService.getUserTerms(languageCode);
```

**Supported Languages:**
- `en` - English (default)
- `fi` - Finnish
- `nl` - Dutch
- `tr` - Turkish

---

## 🔐 Best Practices

1. **Cache Documents Locally**
   - Download and cache legal documents
   - Refresh periodically or on app start
   - Show cached version if offline

2. **Version Tracking**
   - Store the document version user accepted
   - Prompt re-acceptance when version changes

3. **Audit Trail**
   - Always record consent after user accepts
   - Include timestamp and document ID

4. **User Experience**
   - Make documents easily accessible
   - Use readable HTML rendering (flutter_html package)
   - Provide scroll-to-bottom confirmation

5. **Error Handling**
   - Have fallback content if API fails
   - Show user-friendly error messages
   - Allow offline registration with pending consent

---

## 📦 Required Flutter Packages

Add to `pubspec.yaml`:

```yaml
dependencies:
  http: ^1.1.0
  flutter_html: ^3.0.0-beta.2
  shared_preferences: ^2.2.2  # For caching
```

---

## 🔄 Document Update Flow

When backend updates documents:

1. **Version Check**: Compare current version with user's accepted version
2. **Notification**: Alert user about updates
3. **Re-acceptance**: Require user to review and accept new version
4. **Record**: Save new consent with updated document ID

```dart
Future<bool> needsReAcceptance(String token, String docType) async {
  // Check if user needs to re-accept updated terms
  final compliance = await checkUserCompliance(token);
  return !compliance['compliant'];
}
```

---

## 🎯 Integration Checklist

### User Registration
- [ ] Load User Terms document via API
- [ ] Load Privacy Policy document via API
- [ ] Display links to view full documents
- [ ] Require checkboxes for acceptance
- [ ] Record consent after successful registration
- [ ] Handle multi-language based on user locale

### Clinic Registration
- [ ] Load Clinic Terms document
- [ ] Load Partnership Agreement document
- [ ] Load EOI Terms (optional)
- [ ] Display all three documents clearly
- [ ] Mark EOI as optional
- [ ] Record all consents after registration

### Settings Screen
- [ ] Show "Legal" section
- [ ] Links to view all accepted documents
- [ ] Show version and acceptance date
- [ ] Allow re-reading documents

---

## 🆘 Support

For API issues or questions:
- **Email**: dev@fammo.ai
- **Documentation**: https://docs.fammo.ai
- **API Status**: https://status.fammo.ai

---

## 📝 Notes

- All content is HTML formatted - use `flutter_html` for rendering
- Documents are editable via Django admin panel
- Translations managed through django-modeltranslation
- Consent records include IP address and user agent for audit trail
- Documents support versioning for compliance tracking
