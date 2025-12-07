# Clinic Registration API - Complete Flutter Integration Guide

Base URL: `https://fammo.ai/api/v1`

---

## Complete Clinic Registration Flow

### Step 1: User Signs Up & Logs In
First, the user must have an account. See [USER_API_FLUTTER_GUIDE.md](USER_API_FLUTTER_GUIDE.md) for details.

### Step 2: Register Clinic
Once authenticated, user can register their clinic.

---

## Clinic Registration Endpoint

**Endpoint:** `POST /clinics/`

**Authentication:** Required (JWT token)

**Content-Type:** `application/json`

---

## All Available Fields

### Required Fields:
- ✅ `name` (string) - Clinic name

### Optional Basic Information:
- `city` (string) - City name
- `address` (string) - Full street address
- `latitude` (decimal) - GPS latitude coordinate
- `longitude` (decimal) - GPS longitude coordinate
- `phone` (string) - Contact phone number
- `email` (string) - Clinic email address
- `website` (string) - Website URL
- `instagram` (string) - Instagram handle or URL
- `specializations` (string) - Comma-separated specializations
- `bio` (text) - Clinic description/bio
- `logo` (file) - Clinic logo image
- `clinic_eoi` (boolean) - Expression of Interest for pilot program

### Optional Vet Profile Fields:
- `vet_name` (string) - Veterinarian's name
- `degrees` (string) - Academic degrees (e.g., "DVM, PhD")
- `certifications` (string) - Professional certifications

---

## Request Example (Minimal - Only Required Field)

```dart
final accessToken = await storage.read(key: 'access_token');

final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/clinics/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode({
    'name': 'My Veterinary Clinic',
  }),
);
```

**Request Body:**
```json
{
  "name": "My Veterinary Clinic"
}
```

**Response (201 Created):**
```json
{
  "id": 8,
  "name": "My Veterinary Clinic",
  "slug": "my-veterinary-clinic",
  "city": "",
  "address": "",
  "latitude": null,
  "longitude": null,
  "phone": "",
  "email": "",
  "website": "",
  "instagram": "",
  "specializations": "",
  "logo": null,
  "is_verified": false,
  "email_confirmed": false,
  "admin_approved": false,
  "is_active_clinic": false,
  "referral_code": null
}
```

---

## Request Example (Complete - All Fields)

```dart
final accessToken = await storage.read(key: 'access_token');

final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/clinics/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode({
    'name': 'Happy Paws Veterinary Clinic',
    'city': 'Amsterdam',
    'address': 'Prinsengracht 263, 1016 GV Amsterdam',
    'latitude': 52.370216,
    'longitude': 4.895168,
    'phone': '+31 20 123 4567',
    'email': 'info@happypaws.nl',
    'website': 'https://happypaws.nl',
    'instagram': '@happypawsamsterdam',
    'specializations': 'Dogs, Cats, Rabbits, Birds, Emergency Care',
    'bio': 'Happy Paws is a modern veterinary clinic dedicated to providing compassionate care for your beloved pets. Our experienced team offers comprehensive services including routine check-ups, vaccinations, surgery, and emergency care.',
    'clinic_eoi': true,
    'working_hours': [
      {'day_of_week': 0, 'is_closed': false, 'open_time': '09:00', 'close_time': '18:00'},
      {'day_of_week': 1, 'is_closed': false, 'open_time': '09:00', 'close_time': '18:00'},
      {'day_of_week': 2, 'is_closed': false, 'open_time': '09:00', 'close_time': '18:00'},
      {'day_of_week': 3, 'is_closed': false, 'open_time': '09:00', 'close_time': '18:00'},
      {'day_of_week': 4, 'is_closed': false, 'open_time': '09:00', 'close_time': '18:00'},
      {'day_of_week': 5, 'is_closed': false, 'open_time': '09:00', 'close_time': '18:00'},
      {'day_of_week': 6, 'is_closed': true, 'open_time': null, 'close_time': null},
    ],
    'vet_name': 'Dr. Emma van der Berg',
    'degrees': 'DVM, MSc Veterinary Medicine',
    'certifications': 'European Veterinary Specialist in Small Animal Medicine',
  }),
);
```

**Request Body:**
```json
{
  "name": "Happy Paws Veterinary Clinic",
  "city": "Amsterdam",
  "address": "Prinsengracht 263, 1016 GV Amsterdam",
  "latitude": 52.370216,
  "longitude": 4.895168,
  "phone": "+31 20 123 4567",
  "email": "info@happypaws.nl",
  "website": "https://happypaws.nl",
  "instagram": "@happypawsamsterdam",
  "specializations": "Dogs, Cats, Rabbits, Birds, Emergency Care",
  "bio": "Happy Paws is a modern veterinary clinic dedicated to providing compassionate care for your beloved pets. Our experienced team offers comprehensive services including routine check-ups, vaccinations, surgery, and emergency care.",
  "clinic_eoi": true,
  "working_hours": [
    {"day_of_week": 0, "is_closed": false, "open_time": "09:00", "close_time": "18:00"},
    {"day_of_week": 1, "is_closed": false, "open_time": "09:00", "close_time": "18:00"},
    {"day_of_week": 2, "is_closed": false, "open_time": "09:00", "close_time": "18:00"},
    {"day_of_week": 3, "is_closed": false, "open_time": "09:00", "close_time": "18:00"},
    {"day_of_week": 4, "is_closed": false, "open_time": "09:00", "close_time": "18:00"},
    {"day_of_week": 5, "is_closed": false, "open_time": "09:00", "close_time": "18:00"},
    {"day_of_week": 6, "is_closed": true, "open_time": null, "close_time": null}
  ],
  "vet_name": "Dr. Emma van der Berg",
  "degrees": "DVM, MSc Veterinary Medicine",
  "certifications": "European Veterinary Specialist in Small Animal Medicine"
}
```

**Response (201 Created):**
```json
{
  "id": 9,
  "name": "Happy Paws Veterinary Clinic",
  "slug": "happy-paws-veterinary-clinic",
  "city": "Amsterdam",
  "address": "Prinsengracht 263, 1016 GV Amsterdam",
  "latitude": "52.370216",
  "longitude": "4.895168",
  "phone": "+31 20 123 4567",
  "email": "info@happypaws.nl",
  "website": "https://happypaws.nl",
  "instagram": "@happypawsamsterdam",
  "specializations": "Dogs, Cats, Rabbits, Birds, Emergency Care",
  "logo": null,
  "is_verified": false,
  "email_confirmed": false,
  "admin_approved": false,
  "is_active_clinic": false,
  "referral_code": null
}
```

---

## Field Specifications for Flutter Form

### 1. Clinic Name
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Clinic Name *',
    hintText: 'Happy Paws Veterinary Clinic',
    helperText: 'Required',
  ),
  validator: (value) {
    if (value == null || value.isEmpty) {
      return 'Clinic name is required';
    }
    return null;
  },
  maxLength: 160,
)
```
- **Field name:** `name`
- **Type:** String
- **Required:** Yes
- **Max length:** 160 characters
- **Example:** "Happy Paws Veterinary Clinic"

---

### 2. City
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'City',
    hintText: 'Amsterdam',
  ),
  maxLength: 80,
)
```
- **Field name:** `city`
- **Type:** String
- **Required:** No
- **Max length:** 80 characters
- **Example:** "Amsterdam", "Istanbul", "Rotterdam"

---

### 3. Address
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Address',
    hintText: 'Prinsengracht 263, 1016 GV Amsterdam',
  ),
  maxLines: 2,
  maxLength: 220,
)
```
- **Field name:** `address`
- **Type:** String
- **Required:** No
- **Max length:** 220 characters
- **Example:** "Prinsengracht 263, 1016 GV Amsterdam"

---

### 4. Latitude & Longitude (GPS Coordinates)
```dart
// Option 1: Get from device GPS
Future<void> _getCurrentLocation() async {
  Position position = await Geolocator.getCurrentPosition();
  setState(() {
    latitude = position.latitude;
    longitude = position.longitude;
  });
}

// Option 2: Geocode from address (let backend handle)
// If you provide address but not coordinates, 
// the backend will auto-geocode using Google Maps API

// Display coordinates (read-only)
Text('Coordinates: ${latitude?.toStringAsFixed(6)}, ${longitude?.toStringAsFixed(6)}')
```
- **Field names:** `latitude`, `longitude`
- **Type:** Decimal (send as number, not string)
- **Required:** No
- **Format:** Decimal degrees (e.g., 52.370216, 4.895168)
- **Auto-geocoding:** If not provided, backend will geocode from address
- **Example:** 
  - Latitude: 52.370216
  - Longitude: 4.895168

---

### 5. Phone Number
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Phone Number',
    hintText: '+31 20 123 4567',
    prefixIcon: Icon(Icons.phone),
  ),
  keyboardType: TextInputType.phone,
  maxLength: 40,
)
```
- **Field name:** `phone`
- **Type:** String
- **Required:** No
- **Max length:** 40 characters
- **Format:** Any format accepted
- **Example:** "+31 20 123 4567", "05523553091", "(555) 123-4567"

---

### 6. Email Address
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Clinic Email',
    hintText: 'info@clinic.com',
    prefixIcon: Icon(Icons.email),
  ),
  keyboardType: TextInputType.emailAddress,
  validator: (value) {
    if (value != null && value.isNotEmpty) {
      final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
      if (!emailRegex.hasMatch(value)) {
        return 'Please enter a valid email';
      }
    }
    return null;
  },
)
```
- **Field name:** `email`
- **Type:** String (email format)
- **Required:** No
- **Format:** Valid email address
- **Example:** "info@happypaws.nl", "clinic@example.com"

---

### 7. Website
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Website',
    hintText: 'https://www.clinic.com',
    prefixIcon: Icon(Icons.language),
  ),
  keyboardType: TextInputType.url,
  validator: (value) {
    if (value != null && value.isNotEmpty) {
      final urlRegex = RegExp(r'^https?://');
      if (!urlRegex.hasMatch(value)) {
        return 'URL must start with http:// or https://';
      }
    }
    return null;
  },
)
```
- **Field name:** `website`
- **Type:** String (URL format)
- **Required:** No
- **Format:** Must start with http:// or https://
- **Example:** "https://happypaws.nl", "http://clinic.com"

---

### 8. Instagram
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Instagram',
    hintText: '@clinicname or full URL',
    prefixIcon: Icon(Icons.camera_alt),
  ),
  maxLength: 120,
)
```
- **Field name:** `instagram`
- **Type:** String
- **Required:** No
- **Max length:** 120 characters
- **Format:** Handle (@username) or full URL
- **Example:** "@happypawsamsterdam", "https://instagram.com/happypaws"

---

### 9. Specializations
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Specializations',
    hintText: 'Dogs, Cats, Rabbits, Birds',
    helperText: 'Comma-separated list',
  ),
  maxLines: 2,
  maxLength: 200,
)
```
- **Field name:** `specializations`
- **Type:** String
- **Required:** No
- **Max length:** 200 characters
- **Format:** Comma-separated list
- **Example:** "Dogs, Cats, Rabbits, Birds, Emergency Care"

---

### 10. Working Hours (Structured - 7 Days Schedule)

The working hours system uses a structured format:
- 7 records (one for each day: Monday=0, Tuesday=1, ... Sunday=6)
- Each day has:
  - `day_of_week` (0-6)
  - `is_closed` (boolean) - true if clinic is closed that day
  - `open_time` (HH:MM format, e.g., "09:00") - required if not closed
  - `close_time` (HH:MM format, e.g., "18:00") - required if not closed

**Default Values:**
- Monday-Saturday: 09:00 - 18:00 (open)
- Sunday: Closed

**Working hours are included in the registration form** (see complete form example below).

---

### 11. Bio/Description
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'About the Clinic',
    hintText: 'Tell us about your clinic...',
    alignLabelWithHint: true,
  ),
  maxLines: 5,
  maxLength: 1000,
  keyboardType: TextInputType.multiline,
)
```
- **Field name:** `bio`
- **Type:** Text (long string)
- **Required:** No
- **Max length:** No hard limit (use reasonable limit like 1000 chars)
- **Example:** "Happy Paws is a modern veterinary clinic dedicated to providing compassionate care for your beloved pets..."

---

### 12. Logo (Image Upload)
```dart
// For image upload, you need multipart/form-data
// This is separate from the JSON registration

import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

Future<void> uploadClinicLogo(int clinicId, File imageFile) async {
  final accessToken = await storage.read(key: 'access_token');
  
  var request = http.MultipartRequest(
    'PATCH',
    Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/'),
  );
  
  request.headers['Authorization'] = 'Bearer $accessToken';
  request.files.add(
    await http.MultipartFile.fromPath('logo', imageFile.path),
  );
  
  var response = await request.send();
  if (response.statusCode == 200) {
    print('Logo uploaded successfully');
  }
}

// Image picker button
ElevatedButton.icon(
  icon: Icon(Icons.add_photo_alternate),
  label: Text('Upload Logo'),
  onPressed: () async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.gallery);
    if (image != null) {
      // Save for later upload after registration
      setState(() {
        logoFile = File(image.path);
      });
    }
  },
)
```
- **Field name:** `logo`
- **Type:** File (image)
- **Required:** No
- **Format:** Image file (JPEG, PNG)
- **Upload method:** Multipart/form-data (separate from JSON registration)
- **Recommended approach:** 
  1. Register clinic with JSON data
  2. Upload logo afterward using PATCH endpoint
- **Upload path:** `clinic_logos/` on server

---

### 13. Expression of Interest (EOI)
```dart
SwitchListTile(
  title: Text('Join FAMMO Pilot Program'),
  subtitle: Text('Express interest in participating in our pilot program'),
  value: clinicEoi,
  onChanged: (bool value) {
    setState(() {
      clinicEoi = value;
    });
  },
)
```
- **Field name:** `clinic_eoi`
- **Type:** Boolean
- **Required:** No
- **Default:** false
- **Purpose:** Indicates interest in FAMMO's pilot program
- **Example:** true or false

---

### 14. Vet Name
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Veterinarian Name',
    hintText: 'Dr. Emma van der Berg',
  ),
  maxLength: 120,
)
```
- **Field name:** `vet_name`
- **Type:** String
- **Required:** No
- **Max length:** 120 characters
- **Purpose:** Creates VetProfile record linked to clinic
- **Example:** "Dr. Emma van der Berg", "Orhan Demir"

---

### 15. Degrees
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Academic Degrees',
    hintText: 'DVM, MSc Veterinary Medicine',
  ),
  maxLength: 200,
)
```
- **Field name:** `degrees`
- **Type:** String
- **Required:** No
- **Max length:** 200 characters
- **Purpose:** Veterinarian's academic qualifications
- **Example:** "DVM, MSc Veterinary Medicine", "Doctor of Veterinary Medicine"

---

### 16. Certifications
```dart
TextFormField(
  decoration: InputDecoration(
    labelText: 'Professional Certifications',
    hintText: 'Board Certified in...',
  ),
  maxLines: 2,
  maxLength: 240,
)
```
- **Field name:** `certifications`
- **Type:** String
- **Required:** No
- **Max length:** 240 characters
- **Purpose:** Professional certifications and specializations
- **Example:** "European Veterinary Specialist in Small Animal Medicine"

---

## Complete Flutter Form Example

```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:geolocator/geolocator.dart';

class ClinicRegistrationForm extends StatefulWidget {
  @override
  _ClinicRegistrationFormState createState() => _ClinicRegistrationFormState();
}

class _ClinicRegistrationFormState extends State<ClinicRegistrationForm> {
  final _formKey = GlobalKey<FormState>();
  
  // Basic Information
  final _nameController = TextEditingController();
  // Vet Profile
  final _vetNameController = TextEditingController();
  final _degreesController = TextEditingController();
  final _certificationsController = TextEditingController();
  
  // Location
  double? latitude;
  double? longitude;
  bool isLoadingLocation = false;
  
  // EOI
  bool clinicEoi = false;
  
  // Logo
  File? logoFile;
  
  // Working Hours - Default values
  final List<String> dayNames = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
    'Friday', 'Saturday', 'Sunday'
  ];
  List<bool> isClosed = [false, false, false, false, false, false, true]; // Sunday closed
  List<TimeOfDay?> openTimes = List.filled(7, TimeOfDay(hour: 9, minute: 0));
  List<TimeOfDay?> closeTimes = List.filled(7, TimeOfDay(hour: 18, minute: 0));
  
  bool isSubmitting = false;
  bool isLoadingLocation = false;
  
  // EOI
  bool clinicEoi = false;
  
  // Logo
  File? logoFile;
  
  bool isSubmitting = false;

  Future<void> _getCurrentLocation() async {
    setState(() => isLoadingLocation = true);
    
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      
      if (permission == LocationPermission.whileInUse || 
          permission == LocationPermission.always) {
        Position position = await Geolocator.getCurrentPosition();
        setState(() {
          latitude = position.latitude;
          longitude = position.longitude;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Location captured successfully')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to get location: $e')),
      );
    } finally {
      setState(() => isLoadingLocation = false);
    }
  }

  Future<void> _submitForm() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => isSubmitting = true);

    try {
      final storage = FlutterSecureStorage();
      final accessToken = await storage.read(key: 'access_token');

      // Prepare request body
      Map<String, dynamic> requestBody = {
        'name': _nameController.text,
      };

      // Add optional fields if not empty
      if (_cityController.text.isNotEmpty) {
        requestBody['city'] = _cityController.text;
      }
      if (_addressController.text.isNotEmpty) {
        requestBody['address'] = _addressController.text;
      }
      if (latitude != null) {
        requestBody['latitude'] = latitude;
      }
      if (longitude != null) {
        requestBody['longitude'] = longitude;
      }
      if (_phoneController.text.isNotEmpty) {
        requestBody['phone'] = _phoneController.text;
      }
      if (_emailController.text.isNotEmpty) {
        requestBody['email'] = _emailController.text;
      }
      if (_websiteController.text.isNotEmpty) {
        requestBody['website'] = _websiteController.text;
      }
      if (_instagramController.text.isNotEmpty) {
      requestBody['clinic_eoi'] = clinicEoi;
      
      // Working hours - always include
      List<Map<String, dynamic>> workingHours = [];
      for (int i = 0; i < 7; i++) {
        workingHours.add({
          'day_of_week': i,
          'is_closed': isClosed[i],
          'open_time': isClosed[i] ? null : '${openTimes[i]!.hour.toString().padLeft(2, '0')}:${openTimes[i]!.minute.toString().padLeft(2, '0')}',
          'close_time': isClosed[i] ? null : '${closeTimes[i]!.hour.toString().padLeft(2, '0')}:${closeTimes[i]!.minute.toString().padLeft(2, '0')}',
        });
      }
      requestBody['working_hours'] = workingHours;
      
      // Vet profile fields
      if (_vetNameController.text.isNotEmpty) {alizationsController.text;
      }
      if (_bioController.text.isNotEmpty) {
        requestBody['bio'] = _bioController.text;
      }
      
      requestBody['clinic_eoi'] = clinicEoi;
      
      // Vet profile fields
      if (_vetNameController.text.isNotEmpty) {
        requestBody['vet_name'] = _vetNameController.text;
      }
      if (_degreesController.text.isNotEmpty) {
        requestBody['degrees'] = _degreesController.text;
      }
      if (_certificationsController.text.isNotEmpty) {
        requestBody['certifications'] = _certificationsController.text;
      }

      // Submit registration
      final response = await http.post(
        Uri.parse('https://fammo.ai/api/v1/clinics/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode(requestBody),
      );

      if (response.statusCode == 201) {
        final clinic = jsonDecode(response.body);
        
        // Upload logo if selected
        if (logoFile != null) {
          await _uploadLogo(clinic['id']);
        }
        
        // Show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Clinic registered successfully! Check your email for confirmation.'),
            backgroundColor: Colors.green,
          ),
        );
        
        // Navigate to clinic profile or home
        Navigator.of(context).pop();
        
      } else {
        final errors = jsonDecode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Registration failed: ${errors.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
      
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() => isSubmitting = false);
    }
  }

  Future<void> _uploadLogo(int clinicId) async {
    if (logoFile == null) return;
    
    final storage = FlutterSecureStorage();
    final accessToken = await storage.read(key: 'access_token');
    
    var request = http.MultipartRequest(
      'PATCH',
      Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/'),
    );
    
    request.headers['Authorization'] = 'Bearer $accessToken';
    request.files.add(
      await http.MultipartFile.fromPath('logo', logoFile!.path),
    );
    
    await request.send();
  }

  Future<void> _selectTime(BuildContext context, int dayIndex, bool isOpenTime) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: isOpenTime ? openTimes[dayIndex]! : closeTimes[dayIndex]!,
    );
    
    if (picked != null) {
      setState(() {
        if (isOpenTime) {
          openTimes[dayIndex] = picked;
        } else {
          closeTimes[dayIndex] = picked;
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Register Your Clinic'),
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: EdgeInsets.all(16),
          children: [
            // Section: Basic Information
            Text('Basic Information', style: Theme.of(context).textTheme.headlineSmall),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: 'Clinic Name *',
                hintText: 'Happy Paws Veterinary Clinic',
                border: OutlineInputBorder(),
              ),
              validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
              maxLength: 160,
            ),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _cityController,
              decoration: InputDecoration(
                labelText: 'City',
                hintText: 'Amsterdam',
                border: OutlineInputBorder(),
              ),
              maxLength: 80,
            ),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _addressController,
              decoration: InputDecoration(
                labelText: 'Address',
                hintText: 'Prinsengracht 263, 1016 GV',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
              maxLength: 220,
            ),
            SizedBox(height: 16),
            
            // Location
            Card(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Location', style: TextStyle(fontWeight: FontWeight.bold)),
                    SizedBox(height: 8),
                    if (latitude != null && longitude != null)
                      Text('${latitude!.toStringAsFixed(6)}, ${longitude!.toStringAsFixed(6)}')
                    else
                      Text('No location captured', style: TextStyle(color: Colors.grey)),
                    SizedBox(height: 8),
                    ElevatedButton.icon(
                      icon: isLoadingLocation 
                        ? SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                        : Icon(Icons.my_location),
                      label: Text('Get Current Location'),
                      onPressed: isLoadingLocation ? null : _getCurrentLocation,
                    ),
                  ],
                ),
              ),
            ),
            SizedBox(height: 16),
            
            // Contact Information
            Text('Contact Information', style: Theme.of(context).textTheme.headlineSmall),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _phoneController,
              decoration: InputDecoration(
                labelText: 'Phone Number',
                hintText: '+31 20 123 4567',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.phone),
              ),
              keyboardType: TextInputType.phone,
              maxLength: 40,
            ),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                hintText: 'info@clinic.com',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.email),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _websiteController,
              decoration: InputDecoration(
                labelText: 'Website',
                hintText: 'https://www.clinic.com',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.language),
              ),
              keyboardType: TextInputType.url,
            ),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _instagramController,
              decoration: InputDecoration(
                labelText: 'Instagram',
                hintText: '@clinicname',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.camera_alt),
              ),
              maxLength: 120,
            ),
            SizedBox(height: 16),
            
            // Clinic Details
            Text('Clinic Details', style: Theme.of(context).textTheme.headlineSmall),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _specializationsController,
              decoration: InputDecoration(
                labelText: 'Specializations',
                hintText: 'Dogs, Cats, Rabbits, Birds',
                border: OutlineInputBorder(),
                helperText: 'Comma-separated list',
              ),
              maxLines: 2,
              maxLength: 200,
            ),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _bioController,
              decoration: InputDecoration(
                labelText: 'About the Clinic',
                hintText: 'Tell us about your clinic...',
                border: OutlineInputBorder(),
                alignLabelWithHint: true,
              ),
              maxLines: 5,
              maxLength: 1000,
            ),
            SizedBox(height: 16),
            
            // Working Hours Section
            Text('Working Hours', style: Theme.of(context).textTheme.headlineSmall),
            SizedBox(height: 8),
            Text(
              'Set your clinic opening hours for each day',
              style: TextStyle(color: Colors.grey[600], fontSize: 14),
            ),
            SizedBox(height: 16),
            
            // Day cards
            ...List.generate(7, (index) {
              return Card(
                margin: EdgeInsets.only(bottom: 12),
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            dayNames[index],
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Row(
                            children: [
                              Text('Closed', style: TextStyle(fontSize: 14)),
                              Switch(
                                value: isClosed[index],
                                onChanged: (value) {
                                  setState(() => isClosed[index] = value);
                                },
                              ),
                            ],
                          ),
                        ],
                      ),
                      
                      if (!isClosed[index]) ...[
                        SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('Open', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                                  SizedBox(height: 4),
                                  InkWell(
                                    onTap: () => _selectTime(context, index, true),
                                    child: Container(
                                      padding: EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                                      decoration: BoxDecoration(
                                        border: Border.all(color: Colors.grey),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            openTimes[index]!.format(context),
                                            style: TextStyle(fontSize: 15),
                                          ),
                                          Icon(Icons.access_time, size: 18),
                                        ],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('Close', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                                  SizedBox(height: 4),
                                  InkWell(
                                    onTap: () => _selectTime(context, index, false),
                                    child: Container(
                                      padding: EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                                      decoration: BoxDecoration(
                                        border: Border.all(color: Colors.grey),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          Text(
                                            closeTimes[index]!.format(context),
                                            style: TextStyle(fontSize: 15),
                                          ),
                                          Icon(Icons.access_time, size: 18),
                                        ],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              );
            }),
            SizedBox(height: 16),
            
            // Veterinarian Information
            Text('Veterinarian Information', style: Theme.of(context).textTheme.headlineSmall),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _vetNameController,
              decoration: InputDecoration(
                labelText: 'Veterinarian Name',
                hintText: 'Dr. Emma van der Berg',
                border: OutlineInputBorder(),
              ),
              maxLength: 120,
            ),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _degreesController,
              decoration: InputDecoration(
                labelText: 'Academic Degrees',
                hintText: 'DVM, MSc',
                border: OutlineInputBorder(),
              ),
              maxLength: 200,
            ),
            SizedBox(height: 16),
            
            TextFormField(
              controller: _certificationsController,
              decoration: InputDecoration(
                labelText: 'Professional Certifications',
                hintText: 'Board Certified in...',
                border: OutlineInputBorder(),
              ),
              maxLines: 2,
              maxLength: 240,
            ),
            SizedBox(height: 16),
            
            // EOI
            SwitchListTile(
              title: Text('Join FAMMO Pilot Program'),
              subtitle: Text('Express interest in participating'),
              value: clinicEoi,
              onChanged: (value) => setState(() => clinicEoi = value),
            ),
            SizedBox(height: 32),
            
            // Submit Button
            ElevatedButton(
              onPressed: isSubmitting ? null : _submitForm,
              child: isSubmitting
                ? CircularProgressIndicator()
                : Text('Register Clinic'),
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
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
    _bioController.dispose();
    _vetNameController.dispose();
    _degreesController.dispose();
    _certificationsController.dispose();
    super.dispose();
  }
}
```

---

## After Registration

### Email Confirmation Required
After registration, the clinic owner receives a confirmation email:
- **Subject:** "Confirm your FAMMO Clinic Email"
- **Contains:** Activation link
- **Link format:** `https://fammo.ai/api/v1/clinics/confirm-email/{token}/`
- **Action:** User clicks link to confirm email

### Admin Approval Required
- After email confirmation, clinic is pending admin approval
- Admin reviews and approves the clinic
- Only after BOTH email confirmation AND admin approval, clinic appears in public listings

### Clinic Status Fields
```json
{
  "email_confirmed": false,  // Initially false, true after email confirmation
  "admin_approved": false,   // Initially false, true after admin approval
  "is_active_clinic": false  // true only when BOTH above are true
}
```

---

## Error Responses

### 400 Bad Request - Validation Errors
```json
{
  "name": ["This field is required."]
}
```

### 400 Bad Request - Duplicate Name
```json
{
  "name": ["clinic with this name already exists."]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 400 Bad Request - User Already Has Clinic
```json
{
  "detail": "You already have a clinic registered."
}
```

---

## Summary for Flutter Developers

### Required Fields:
1. ✅ `name` (String, max 160 chars)

### Recommended Fields:
2. `city` (String, max 80 chars)
3. `address` (String, max 220 chars)
4. `phone` (String, max 40 chars)
5. `email` (Email format)
6. `specializations` (String, max 200 chars)
7. `bio` (Text)
8. `vet_name` (String, max 120 chars)

### Optional but Useful:
9. `latitude` & `longitude` (Decimal) - GPS coordinates
10. `website` (URL format)
11. `instagram` (String, max 120 chars)
12. `degrees` (String, max 200 chars)
13. `certifications` (String, max 240 chars)
14. `clinic_eoi` (Boolean, default false)
15. `logo` (File, upload separately after registration)

### Form Flow:
1. **User logs in** (must be authenticated)
2. **Fill registration form** (name required, working hours have defaults)
3. **Submit JSON data** (POST /clinics/) - includes working hours
4. **Upload logo** (optional, PATCH /clinics/{id}/ with multipart/form-data)
5. **Confirm email** (user receives email, clicks link)
6. **Wait for admin approval** (automatic process, admin reviews)
7. **Clinic goes live** (appears in public listings when both confirmed and approved)

### GPS Location:
- **Option 1:** Use device GPS (Geolocator package)
- **Option 2:** Leave empty, backend auto-geocodes from address
- **Recommendation:** Try to get GPS, fallback to address geocoding

### Working Hours:
- **Included in registration form** with default values
- Default: Monday-Saturday 09:00-18:00 (open), Sunday closed
- Users can customize before submitting
- Can be updated later using Working Hours API (see "Working Hours Configuration" section below)

---

## Testing

**Test credentials:**
- Email: `paperas@superhouse.vn`
- Password: `Ali5522340731`

**Test clinic (already registered):**
- Clinic ID: 7
- Name: "paperas"
- Owner: paperas@superhouse.vn

---

## Working Hours Configuration (Update After Registration)

**Note:** Working hours are included in the registration form with default values. Use this endpoint to UPDATE working hours after registration.

### Endpoint: POST /clinics/{clinic_id}/working-hours/

**Authentication:** Required (JWT token)

**Content-Type:** `application/json`

---

### Working Hours Model

Each clinic has **7 working hour records** (one for each day of the week):

```dart
class WorkingHours {
  final int id;
  final int dayOfWeek;  // 0 = Monday, 1 = Tuesday, ..., 6 = Sunday
  final String dayName;  // "Monday", "Tuesday", etc.
  final bool isClosed;
  final String? openTime;  // "HH:MM" format, e.g., "09:00"
  final String? closeTime; // "HH:MM" format, e.g., "18:00"

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
```

---

### Request Format

You must send **all 7 days** in a single request:

```dart
final accessToken = await storage.read(key: 'access_token');

// Prepare working hours for all 7 days
List<Map<String, dynamic>> workingHours = [
  {
    'day_of_week': 0,  // Monday
    'is_closed': false,
    'open_time': '09:00',
    'close_time': '18:00',
  },
  {
    'day_of_week': 1,  // Tuesday
    'is_closed': false,
    'open_time': '09:00',
    'close_time': '18:00',
  },
  {
    'day_of_week': 2,  // Wednesday
    'is_closed': false,
    'open_time': '09:00',
    'close_time': '18:00',
  },
  {
    'day_of_week': 3,  // Thursday
    'is_closed': false,
    'open_time': '09:00',
    'close_time': '18:00',
  },
  {
    'day_of_week': 4,  // Friday
    'is_closed': false,
    'open_time': '09:00',
    'close_time': '18:00',
  },
  {
    'day_of_week': 5,  // Saturday
    'is_closed': false,
    'open_time': '09:00',
    'close_time': '14:00',
  },
  {
    'day_of_week': 6,  // Sunday
    'is_closed': true,
    'open_time': null,
    'close_time': null,
  },
];

final response = await http.post(
  Uri.parse('https://fammo.ai/api/v1/clinics/$clinicId/working-hours/'),
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $accessToken',
  },
  body: jsonEncode({'working_hours': workingHours}),
);
```

**Request Body:**
```json
{
  "working_hours": [
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
      "close_time": "14:00"
    },
    {
      "day_of_week": 6,
      "is_closed": true,
      "open_time": null,
      "close_time": null
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "message": "Working hours updated successfully",
  "working_hours": [
    {
      "id": 45,
      "day_of_week": 0,
      "day_name": "Monday",
      "is_closed": false,
      "open_time": "09:00",
      "close_time": "18:00"
    },
    {
      "id": 46,
      "day_of_week": 1,
      "day_name": "Tuesday",
      "is_closed": false,
      "open_time": "09:00",
      "close_time": "18:00"
    },
    {
      "id": 47,
      "day_of_week": 2,
      "day_name": "Wednesday",
      "is_closed": false,
      "open_time": "09:00",
      "close_time": "18:00"
    },
    {
      "id": 48,
      "day_of_week": 3,
      "day_name": "Thursday",
      "is_closed": false,
      "open_time": "09:00",
      "close_time": "18:00"
    },
    {
      "id": 49,
      "day_of_week": 4,
      "day_name": "Friday",
      "is_closed": false,
      "open_time": "09:00",
      "close_time": "18:00"
    },
    {
      "id": 50,
      "day_of_week": 5,
      "day_name": "Saturday",
      "is_closed": false,
      "open_time": "09:00",
      "close_time": "14:00"
    },
    {
      "id": 51,
      "day_of_week": 6,
      "day_name": "Sunday",
      "is_closed": true,
      "open_time": null,
      "close_time": null
    }
  ]
}
```

---

### Flutter UI for Working Hours

```dart
class WorkingHoursSetup extends StatefulWidget {
  final int clinicId;

  WorkingHoursSetup({required this.clinicId});

  @override
  _WorkingHoursSetupState createState() => _WorkingHoursSetupState();
}

class _WorkingHoursSetupState extends State<WorkingHoursSetup> {
  final List<String> dayNames = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 
    'Friday', 'Saturday', 'Sunday'
  ];

  // State for each day
  List<bool> isClosed = List.filled(7, false);
  List<TimeOfDay?> openTimes = List.filled(7, TimeOfDay(hour: 9, minute: 0));
  List<TimeOfDay?> closeTimes = List.filled(7, TimeOfDay(hour: 18, minute: 0));
  
  bool isSubmitting = false;

  Future<void> _submitWorkingHours() async {
    setState(() => isSubmitting = true);

    try {
      final storage = FlutterSecureStorage();
      final accessToken = await storage.read(key: 'access_token');

      // Build working hours array
      List<Map<String, dynamic>> workingHours = [];
      for (int i = 0; i < 7; i++) {
        workingHours.add({
          'day_of_week': i,
          'is_closed': isClosed[i],
          'open_time': isClosed[i] ? null : '${openTimes[i]!.hour.toString().padLeft(2, '0')}:${openTimes[i]!.minute.toString().padLeft(2, '0')}',
          'close_time': isClosed[i] ? null : '${closeTimes[i]!.hour.toString().padLeft(2, '0')}:${closeTimes[i]!.minute.toString().padLeft(2, '0')}',
        });
      }

      final response = await http.post(
        Uri.parse('https://fammo.ai/api/v1/clinics/${widget.clinicId}/working-hours/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode({'working_hours': workingHours}),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Working hours saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop();
      } else {
        final errors = jsonDecode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save: ${errors.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      setState(() => isSubmitting = false);
    }
  }

  Future<void> _selectTime(BuildContext context, int dayIndex, bool isOpenTime) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: isOpenTime ? openTimes[dayIndex]! : closeTimes[dayIndex]!,
    );
    
    if (picked != null) {
      setState(() {
        if (isOpenTime) {
          openTimes[dayIndex] = picked;
        } else {
          closeTimes[dayIndex] = picked;
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Set Working Hours'),
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          Text(
            'Configure your clinic\'s working hours for each day',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          SizedBox(height: 24),
          
          // Day cards
          ...List.generate(7, (index) {
            return Card(
              margin: EdgeInsets.only(bottom: 16),
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          dayNames[index],
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Row(
                          children: [
                            Text('Closed'),
                            Switch(
                              value: isClosed[index],
                              onChanged: (value) {
                                setState(() => isClosed[index] = value);
                              },
                            ),
                          ],
                        ),
                      ],
                    ),
                    
                    if (!isClosed[index]) ...[
                      SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Open Time', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                                SizedBox(height: 4),
                                InkWell(
                                  onTap: () => _selectTime(context, index, true),
                                  child: Container(
                                    padding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                                    decoration: BoxDecoration(
                                      border: Border.all(color: Colors.grey),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          openTimes[index]!.format(context),
                                          style: TextStyle(fontSize: 16),
                                        ),
                                        Icon(Icons.access_time, size: 20),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                          SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('Close Time', style: TextStyle(fontSize: 12, color: Colors.grey[600])),
                                SizedBox(height: 4),
                                InkWell(
                                  onTap: () => _selectTime(context, index, false),
                                  child: Container(
                                    padding: EdgeInsets.symmetric(vertical: 12, horizontal: 16),
                                    decoration: BoxDecoration(
                                      border: Border.all(color: Colors.grey),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(
                                          closeTimes[index]!.format(context),
                                          style: TextStyle(fontSize: 16),
                                        ),
                                        Icon(Icons.access_time, size: 20),
                                      ],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            );
          }),
          
          SizedBox(height: 24),
          
          ElevatedButton(
            onPressed: isSubmitting ? null : _submitWorkingHours,
            child: isSubmitting
              ? CircularProgressIndicator()
              : Text('Save Working Hours'),
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.symmetric(vertical: 16),
            ),
          ),
        ],
      ),
    );
  }
}
```

---

### Validation Rules

1. **All 7 days required:** Must send exactly 7 records (day_of_week 0-6)
2. **Closed days:** If `is_closed = true`, then `open_time` and `close_time` must be `null`
3. **Open days:** If `is_closed = false`, both `open_time` and `close_time` are required
4. **Time format:** Must be "HH:MM" (24-hour format), e.g., "09:00", "18:30"
5. **Time validation:** `open_time` must be before `close_time`

---

### Error Responses

**400 Bad Request - Missing times for open day:**
```json
{
  "working_hours": [
    {},
    {},
    {},
    {
      "open_time": ["Opening and closing times are required when not closed."]
    }
  ]
}
```

**400 Bad Request - Invalid time format:**
```json
{
  "working_hours": [
    {},
    {
      "open_time": ["Time has wrong format. Use one of these formats instead: hh:mm[:ss[.uuuuuu]]."]
    }
  ]
}
```

**400 Bad Request - Open time after close time:**
```json
{
  "working_hours": [
    {},
    {},
    {
      "non_field_errors": ["Opening time must be before closing time"]
    }
  ]
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden - Not clinic owner:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### Complete Registration Flow with Working Hours

```dart
Future<void> registerClinicComplete() async {
  try {
    // Step 1: Register clinic
    final clinicResponse = await registerClinic();
    final clinicId = clinicResponse['id'];
    
    // Step 2: Upload logo (optional)
    if (logoFile != null) {
      await uploadLogo(clinicId);
    }
    
    // Step 3: Set working hours
    await setWorkingHours(clinicId);
    
    // Step 4: Remind user to confirm email
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Registration Complete!'),
        content: Text(
          'Your clinic has been registered successfully.\n\n'
          'Please check your email to confirm your clinic email address.\n\n'
          'After confirmation, admin will review and approve your clinic.'
        ),
        actions: [
          TextButton(
            child: Text('OK'),
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pushReplacementNamed('/clinic-dashboard');
            },
          ),
        ],
      ),
    );
    
  } catch (e) {
    // Handle errors
  }
}
```

---

### Day of Week Reference

| day_of_week | Day Name  |
|-------------|-----------|
| 0           | Monday    |
| 1           | Tuesday   |
| 2           | Wednesday |
| 3           | Thursday  |
| 4           | Friday    |
| 5           | Saturday  |
| 6           | Sunday    |

---

### Time Format Examples

✅ **Valid formats:**
- "09:00"
- "18:30"
- "08:00"
- "23:59"

❌ **Invalid formats:**
- "9:00" (missing leading zero)
- "9am"
- "18:00:00" (seconds not needed, but accepted)
- "25:00" (invalid hour)

---

### Production Example

**Real working hours from production clinic (Ibadoyos klinik):**

```json
{
  "working_hours": [
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
      "id": 10,
      "day_of_week": 2,
      "day_name": "Wednesday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 11,
      "day_of_week": 3,
      "day_name": "Thursday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 12,
      "day_of_week": 4,
      "day_name": "Friday",
      "is_closed": false,
      "open_time": "09:00:00",
      "close_time": "18:00:00"
    },
    {
      "id": 13,
      "day_of_week": 5,
      "day_name": "Saturday",
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
}
```
