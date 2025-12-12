# Legal Documents API Guide for Flutter

## Overview
This guide shows you how to fetch legal documents (Terms & Conditions, Privacy Policy, Partnership Agreements, etc.) from the FAMMO API and display them in your Flutter app. All documents support multiple languages and can be edited by admins through the Django admin panel.

## Available Legal Documents

The API supports 5 types of legal documents:

| Document Type | API Value | Description |
|--------------|-----------|-------------|
| User Terms & Conditions | `user_terms` | Terms for regular users |
| User Privacy Policy | `user_privacy` | Privacy policy for users |
| Clinic Terms & Conditions | `clinic_terms` | Terms for clinic partners |
| Clinic Partnership Agreement | `clinic_partnership` | Partnership agreement for clinics |
| Expression of Interest (EOI) | `clinic_eoi` | EOI terms for pilot program |

## API Endpoints

### 1. Get All Active Legal Documents
```
GET /api/v1/legal/documents/
```

**Query Parameters:**
- `doc_type` (optional): Filter by document type (`user_terms`, `clinic_terms`, etc.)

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
      "title": "FAMMO.ai – Terms and Conditions",
      "version": "1.0",
      "content": "<p>Welcome to FAMMO.ai...</p>",
      "summary": "Terms and conditions for FAMMO users",
      "effective_date": "2025-12-12T10:00:00Z",
      "created_at": "2025-12-12T10:00:00Z"
    }
  ]
}
```

### 2. Get Specific Legal Document by Type
```
GET /api/v1/legal/documents/by_type/?doc_type=user_terms
```

**Query Parameters:**
- `doc_type` (required): Document type to fetch

**Headers:**
- `Accept-Language`: Language code (e.g., `en`, `fi`, `nl`, `tr`) - Content is automatically translated

**Response:**
```json
{
  "id": 1,
  "doc_type": "user_terms",
  "doc_type_display": "User Terms and Conditions",
  "title": "FAMMO.ai – Terms and Conditions",
  "version": "1.0",
  "content": "<p>Welcome to FAMMO.ai...</p>",
  "summary": "Terms and conditions for FAMMO users",
  "effective_date": "2025-12-12T10:00:00Z",
  "created_at": "2025-12-12T10:00:00Z"
}
```

### 3. Get Available Document Types
```
GET /api/v1/legal/documents/available_types/
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

### 4. Record User Consent
```
POST /api/v1/legal/consent/user/
```

**Headers:**
- `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "document": 1,
  "accepted": true
}
```

**Response:**
```json
{
  "id": 1,
  "document": 1,
  "document_title": "FAMMO.ai – Terms and Conditions",
  "document_type": "user_terms",
  "accepted": true,
  "accepted_at": "2025-12-12T10:30:00Z"
}
```

### 5. Get User's Consent History
```
GET /api/v1/legal/consent/user/
```

**Headers:**
- `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "document": 1,
      "document_title": "FAMMO.ai – Terms and Conditions",
      "document_type": "user_terms",
      "accepted": true,
      "accepted_at": "2025-12-12T10:30:00Z"
    }
  ]
}
```

### 6. Check User Compliance
```
GET /api/v1/legal/consent/user/check_compliance/
```

**Headers:**
- `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "compliant": true,
  "missing_documents": [],
  "accepted_documents": ["user_terms", "user_privacy"]
}
```

### 7. Record Clinic Consent
```
POST /api/v1/legal/consent/clinic/
```

**Headers:**
- `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "document": 3,
  "clinic_email": "clinic@example.com",
  "accepted": true
}
```

**Response:**
```json
{
  "id": 1,
  "document": 3,
  "document_title": "Clinic Terms and Conditions",
  "document_type": "clinic_terms",
  "clinic_email": "clinic@example.com",
  "accepted": true,
  "accepted_at": "2025-12-12T11:00:00Z"
}
```

## Flutter Implementation

### 1. Create Model Classes

```dart
// lib/models/legal_document.dart
class LegalDocument {
  final int id;
  final String docType;
  final String docTypeDisplay;
  final String title;
  final String version;
  final String content;
  final String? summary;
  final DateTime effectiveDate;
  final DateTime createdAt;

  LegalDocument({
    required this.id,
    required this.docType,
    required this.docTypeDisplay,
    required this.title,
    required this.version,
    required this.content,
    this.summary,
    required this.effectiveDate,
    required this.createdAt,
  });

  factory LegalDocument.fromJson(Map<String, dynamic> json) {
    return LegalDocument(
      id: json['id'],
      docType: json['doc_type'],
      docTypeDisplay: json['doc_type_display'],
      title: json['title'],
      version: json['version'],
      content: json['content'],
      summary: json['summary'],
      effectiveDate: DateTime.parse(json['effective_date']),
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

// lib/models/user_consent.dart
class UserConsent {
  final int id;
  final int document;
  final String documentTitle;
  final String documentType;
  final bool accepted;
  final DateTime acceptedAt;

  UserConsent({
    required this.id,
    required this.document,
    required this.documentTitle,
    required this.documentType,
    required this.accepted,
    required this.acceptedAt,
  });

  factory UserConsent.fromJson(Map<String, dynamic> json) {
    return UserConsent(
      id: json['id'],
      document: json['document'],
      documentTitle: json['document_title'],
      documentType: json['document_type'],
      accepted: json['accepted'],
      acceptedAt: DateTime.parse(json['accepted_at']),
    );
  }
}
```

### 2. Create API Service

```dart
// lib/services/legal_api_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/legal_document.dart';
import '../models/user_consent.dart';

class LegalApiService {
  final String baseUrl;
  final String? accessToken;

  LegalApiService({
    required this.baseUrl,
    this.accessToken,
  });

  Map<String, String> get _headers {
    final headers = {
      'Content-Type': 'application/json',
      'Accept-Language': 'en', // Change based on user preference
    };
    if (accessToken != null) {
      headers['Authorization'] = 'Bearer $accessToken';
    }
    return headers;
  }

  /// Fetch all legal documents
  Future<List<LegalDocument>> getAllDocuments({String? docType}) async {
    final uri = Uri.parse('$baseUrl/api/v1/legal/documents/')
        .replace(queryParameters: docType != null ? {'doc_type': docType} : null);
    
    final response = await http.get(uri, headers: _headers);
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final results = data['results'] as List;
      return results.map((json) => LegalDocument.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load documents: ${response.statusCode}');
    }
  }

  /// Fetch specific legal document by type
  Future<LegalDocument> getDocumentByType(String docType) async {
    final uri = Uri.parse('$baseUrl/api/v1/legal/documents/by_type/')
        .replace(queryParameters: {'doc_type': docType});
    
    final response = await http.get(uri, headers: _headers);
    
    if (response.statusCode == 200) {
      return LegalDocument.fromJson(json.decode(response.body));
    } else if (response.statusCode == 404) {
      throw Exception('Document not found');
    } else {
      throw Exception('Failed to load document: ${response.statusCode}');
    }
  }

  /// Record user consent
  Future<UserConsent> recordUserConsent(int documentId, bool accepted) async {
    final uri = Uri.parse('$baseUrl/api/v1/legal/consent/user/');
    
    final response = await http.post(
      uri,
      headers: _headers,
      body: json.encode({
        'document': documentId,
        'accepted': accepted,
      }),
    );
    
    if (response.statusCode == 201 || response.statusCode == 200) {
      return UserConsent.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to record consent: ${response.statusCode}');
    }
  }

  /// Get user's consent history
  Future<List<UserConsent>> getUserConsentHistory() async {
    final uri = Uri.parse('$baseUrl/api/v1/legal/consent/user/');
    
    final response = await http.get(uri, headers: _headers);
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final results = data['results'] as List;
      return results.map((json) => UserConsent.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load consent history: ${response.statusCode}');
    }
  }

  /// Check if user is compliant with required documents
  Future<Map<String, dynamic>> checkUserCompliance() async {
    final uri = Uri.parse('$baseUrl/api/v1/legal/consent/user/check_compliance/');
    
    final response = await http.get(uri, headers: _headers);
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to check compliance: ${response.statusCode}');
    }
  }
}
```

### 3. Create Legal Document Screen

```dart
// lib/screens/legal_document_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_html/flutter_html.dart';
import '../models/legal_document.dart';
import '../services/legal_api_service.dart';

class LegalDocumentScreen extends StatefulWidget {
  final String docType;
  final String title;
  final bool requireConsent;

  const LegalDocumentScreen({
    Key? key,
    required this.docType,
    required this.title,
    this.requireConsent = false,
  }) : super(key: key);

  @override
  State<LegalDocumentScreen> createState() => _LegalDocumentScreenState();
}

class _LegalDocumentScreenState extends State<LegalDocumentScreen> {
  late Future<LegalDocument> _documentFuture;
  final LegalApiService _apiService = LegalApiService(
    baseUrl: 'https://your-api-url.com',
    accessToken: 'your-access-token', // Get from auth service
  );
  bool _accepted = false;
  bool _isRecordingConsent = false;

  @override
  void initState() {
    super.initState();
    _documentFuture = _apiService.getDocumentByType(widget.docType);
  }

  Future<void> _recordConsent(int documentId) async {
    setState(() => _isRecordingConsent = true);
    
    try {
      await _apiService.recordUserConsent(documentId, true);
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Consent recorded successfully')),
        );
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to record consent: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isRecordingConsent = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: FutureBuilder<LegalDocument>(
        future: _documentFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          
          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, size: 48, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('Error: ${snapshot.error}'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      setState(() {
                        _documentFuture = _apiService.getDocumentByType(widget.docType);
                      });
                    },
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }
          
          final document = snapshot.data!;
          
          return Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        document.title,
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Version ${document.version} • Effective: ${_formatDate(document.effectiveDate)}',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey[600],
                            ),
                      ),
                      if (document.summary != null) ...[
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.blue.shade50,
                            borderRadius: BorderRadius.circular(8),
                            border: Border(
                              left: BorderSide(color: Colors.blue, width: 4),
                            ),
                          ),
                          child: Html(data: document.summary!),
                        ),
                      ],
                      const SizedBox(height: 16),
                      Html(
                        data: document.content,
                        style: {
                          "body": Style(
                            fontSize: FontSize(16.0),
                            lineHeight: const LineHeight(1.6),
                          ),
                        },
                      ),
                    ],
                  ),
                ),
              ),
              if (widget.requireConsent)
                Container(
                  padding: const EdgeInsets.all(16.0),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 4,
                        offset: const Offset(0, -2),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      CheckboxListTile(
                        title: Text('I have read and agree to ${document.title}'),
                        value: _accepted,
                        onChanged: (value) {
                          setState(() => _accepted = value ?? false);
                        },
                        controlAffinity: ListTileControlAffinity.leading,
                      ),
                      const SizedBox(height: 8),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: _accepted && !_isRecordingConsent
                              ? () => _recordConsent(document.id)
                              : null,
                          child: _isRecordingConsent
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(strokeWidth: 2),
                                )
                              : const Text('Accept and Continue'),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          );
        },
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
```

### 4. Usage Examples

#### Display Terms During Registration
```dart
// In your registration flow
ElevatedButton(
  onPressed: () async {
    final accepted = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const LegalDocumentScreen(
          docType: 'user_terms',
          title: 'Terms and Conditions',
          requireConsent: true,
        ),
      ),
    );
    
    if (accepted == true) {
      // Continue with registration
      _completeRegistration();
    }
  },
  child: const Text('View Terms & Conditions'),
)
```

#### Check Compliance Before Feature Access
```dart
Future<void> _checkComplianceBeforeAccess() async {
  final apiService = LegalApiService(
    baseUrl: 'https://your-api-url.com',
    accessToken: await _getAccessToken(),
  );
  
  try {
    final compliance = await apiService.checkUserCompliance();
    
    if (compliance['compliant'] == true) {
      // User is compliant, allow access
      _accessFeature();
    } else {
      // Show missing documents
      final missingDocs = compliance['missing_documents'] as List;
      _showMissingDocumentsDialog(missingDocs);
    }
  } catch (e) {
    print('Error checking compliance: $e');
  }
}
```

#### Clinic Registration with Multiple Consents
```dart
Future<void> _registerClinic() async {
  // Get all required documents
  final documents = await Future.wait([
    _apiService.getDocumentByType('clinic_terms'),
    _apiService.getDocumentByType('clinic_partnership'),
    _apiService.getDocumentByType('clinic_eoi'), // Optional
  ]);
  
  // Show documents and get consent
  for (final doc in documents) {
    final accepted = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => LegalDocumentScreen(
          docType: doc.docType,
          title: doc.title,
          requireConsent: true,
        ),
      ),
    );
    
    if (accepted != true && doc.docType != 'clinic_eoi') {
      // Required document not accepted
      return;
    }
  }
  
  // All required documents accepted, proceed with registration
  _completeClinicRegistration();
}
```

## Best Practices

### 1. Language Support
Always include the `Accept-Language` header to get translated content:

```dart
final headers = {
  'Accept-Language': Localizations.localeOf(context).languageCode,
};
```

### 2. Caching
Cache legal documents to reduce API calls:

```dart
class LegalDocumentCache {
  static final Map<String, LegalDocument> _cache = {};
  static const Duration cacheExpiry = Duration(hours: 24);
  
  static Future<LegalDocument> get(
    String docType,
    LegalApiService apiService,
  ) async {
    final cached = _cache[docType];
    if (cached != null) {
      return cached;
    }
    
    final document = await apiService.getDocumentByType(docType);
    _cache[docType] = document;
    return document;
  }
  
  static void clear() => _cache.clear();
}
```

### 3. Error Handling
Always handle errors gracefully:

```dart
try {
  final document = await apiService.getDocumentByType('user_terms');
  // Use document
} on SocketException {
  // No internet connection
  showNoInternetDialog();
} on HttpException {
  // Server error
  showServerErrorDialog();
} catch (e) {
  // Other errors
  showGenericErrorDialog();
}
```

### 4. Consent Tracking
Track consent status locally to avoid repeated API calls:

```dart
class ConsentManager {
  static const String _keyPrefix = 'consent_';
  
  static Future<bool> hasConsent(String docType) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool('$_keyPrefix$docType') ?? false;
  }
  
  static Future<void> recordConsent(String docType, bool accepted) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('$_keyPrefix$docType', accepted);
  }
}
```

## Testing

### Test Data Setup
Use the Django admin panel or management command to create test documents:

```bash
python manage.py seed_legal_documents
```

### Test Scenarios
1. **Fetch document in different languages**
2. **Handle missing documents (404)**
3. **Record consent without authentication (should fail)**
4. **Check compliance for new users**
5. **Update consent status**

## Admin Panel Management

Admins can manage legal documents through Django admin:

1. Navigate to: `https://your-domain.com/admin/core/legaldocument/`
2. Click "Add Legal Document"
3. Fill in:
   - Document Type
   - Title (in all languages)
   - Content (HTML supported)
   - Version
   - Effective Date
4. Check "Is Active" to make it live
5. Save

The document will immediately be available via the API in all configured languages.

## Support

For questions or issues:
- Email: support@fammo.ai
- GitHub Issues: [Repository URL]
