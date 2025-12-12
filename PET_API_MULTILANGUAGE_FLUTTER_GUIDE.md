# Pet API Multi-Language Support for Flutter

## Overview
Your pet models (PetType, Gender, AgeCategory, Breed, FoodFeeling, FoodImportance, BodyType, ActivityLevel, FoodAllergy, HealthIssue, TreatFrequency) now support multiple languages via `django-modeltranslation`. Flutter can automatically load the selected language items.

## Backend Setup (Already Complete ✅)

### Translation Configuration
All pet models are registered in `pet/translation.py` with translatable fields:

```python
# Models support fields with language-specific versions:
# - PetType: name_en, name_tr, name_nl, name_fi
# - Gender: name_en, name_tr, name_nl, name_fi
# - AgeCategory: name_en, name_tr, name_nl, name_fi
# - Breed: name_en, name_tr, name_nl, name_fi
# - FoodType: name_en, name_tr, name_nl, name_fi
# - FoodFeeling: name_en, name_tr, name_nl, name_fi (+ description)
# - FoodImportance: name_en, name_tr, name_nl, name_fi
# - BodyType: name_en, name_tr, name_nl, name_fi (+ description)
# - ActivityLevel: name_en, name_tr, name_nl, name_fi (+ description)
# - FoodAllergy: name_en, name_tr, name_nl, name_fi
# - HealthIssue: name_en, name_tr, name_nl, name_fi
# - TreatFrequency: name_en, name_tr, name_nl, name_fi (+ description)
```

### Supported Languages
- **en**: English
- **tr**: Türkçe (Turkish)
- **nl**: Nederlands (Dutch)
- **fi**: Suomalainen (Finnish)

### User Language Preference Storage
The API stores user's language preference in:
```
/api/v1/me/language/
```

User profile has `preferred_language` field that stores the selected language code.

---

## API Endpoints for Pet Models

### 1. **Pet Type Endpoint**
```
GET /api/v1/pet-types/
```
Returns translated pet types based on `Accept-Language` header.

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Dog"  // Automatically translated based on language header
  },
  {
    "id": 2,
    "name": "Cat"
  }
]
```

### 2. **Gender Endpoint**
```
GET /api/v1/genders/
```

### 3. **Age Categories Endpoint**
```
GET /api/v1/age-categories/?pet_type=1
```
Returns age categories filtered by pet type, with translations.

### 4. **Breeds Endpoint**
```
GET /api/v1/breeds/?pet_type=1
```
Returns breeds filtered by pet type, with translations.

### 5. **Food Types Endpoint**
```
GET /api/v1/food-types/
```

### 6. **Food Feelings Endpoint**
```
GET /api/v1/food-feelings/
```

### 7. **Food Importance Endpoint**
```
GET /api/v1/food-importance/
```

### 8. **Body Types Endpoint**
```
GET /api/v1/body-types/
```

### 9. **Activity Levels Endpoint**
```
GET /api/v1/activity-levels/
```

### 10. **Food Allergies Endpoint**
```
GET /api/v1/food-allergies/
```

### 11. **Health Issues Endpoint**
```
GET /api/v1/health-issues/
```

### 12. **Treat Frequencies Endpoint**
```
GET /api/v1/treat-frequencies/
```

---

## Flutter Implementation

### How Language Selection Works

The **automatic language loading** is controlled by HTTP headers:

```
Accept-Language: en  → Returns English translations
Accept-Language: tr  → Returns Turkish translations
Accept-Language: nl  → Returns Dutch translations
Accept-Language: fi  → Returns Finnish translations
```

### Step 1: Create a Language Manager Service

```dart
import 'package:shared_preferences/shared_preferences.dart';

class LanguageManager {
  static const String _languageKey = 'preferred_language';
  static final LanguageManager _instance = LanguageManager._internal();
  
  late String _currentLanguage;
  
  LanguageManager._internal();
  
  factory LanguageManager() {
    return _instance;
  }
  
  /// Initialize with saved language or default
  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    _currentLanguage = prefs.getString(_languageKey) ?? 'en';
  }
  
  /// Get current language
  String get currentLanguage => _currentLanguage;
  
  /// Set language and save to preferences
  Future<void> setLanguage(String languageCode) async {
    _currentLanguage = languageCode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_languageKey, languageCode);
    
    // Also sync with backend
    await _syncLanguageWithBackend(languageCode);
  }
  
  /// Sync language with backend API
  Future<void> _syncLanguageWithBackend(String languageCode) async {
    // Call POST /api/v1/me/language/
    try {
      // Your API call here
      // await apiClient.post('/api/v1/me/language/', 
      //   data: {'language': languageCode});
    } catch (e) {
      print('Error syncing language: $e');
    }
  }
  
  /// Get language header for HTTP requests
  Map<String, String> getLanguageHeaders() {
    return {
      'Accept-Language': _currentLanguage,
    };
  }
}
```

### Step 2: Update API Client to Include Language Header

```dart
import 'package:http/http.dart' as http;

class ApiClient {
  final String baseUrl;
  final LanguageManager languageManager;
  
  ApiClient({
    required this.baseUrl,
    required this.languageManager,
  });
  
  Future<http.Response> get(
    String endpoint, {
    Map<String, String>? headers,
  }) async {
    final mergedHeaders = {
      ...?headers,
      ...languageManager.getLanguageHeaders(),
      'Authorization': 'Bearer $token', // Your auth token
    };
    
    return http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: mergedHeaders,
    );
  }
  
  Future<http.Response> post(
    String endpoint, {
    required Map<String, dynamic> body,
    Map<String, String>? headers,
  }) async {
    final mergedHeaders = {
      ...?headers,
      ...languageManager.getLanguageHeaders(),
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
    
    return http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: mergedHeaders,
      body: jsonEncode(body),
    );
  }
}
```

### Step 3: Create Pet Options Repository

```dart
class PetOptionsRepository {
  final ApiClient apiClient;
  
  PetOptionsRepository({required this.apiClient});
  
  /// Load pet types in current language
  Future<List<PetType>> getPetTypes() async {
    final response = await apiClient.get('/api/v1/pet-types/');
    
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((item) => PetType.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load pet types');
    }
  }
  
  /// Load genders in current language
  Future<List<Gender>> getGenders() async {
    final response = await apiClient.get('/api/v1/genders/');
    
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((item) => Gender.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load genders');
    }
  }
  
  /// Load age categories for specific pet type
  Future<List<AgeCategory>> getAgeCategories(int petTypeId) async {
    final response = await apiClient.get(
      '/api/v1/age-categories/?pet_type=$petTypeId'
    );
    
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((item) => AgeCategory.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load age categories');
    }
  }
  
  /// Load breeds for specific pet type
  Future<List<Breed>> getBreeds(int petTypeId) async {
    final response = await apiClient.get(
      '/api/v1/breeds/?pet_type=$petTypeId'
    );
    
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((item) => Breed.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load breeds');
    }
  }
  
  // Similar methods for other endpoints...
  Future<List<ActivityLevel>> getActivityLevels() async {
    final response = await apiClient.get('/api/v1/activity-levels/');
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((item) => ActivityLevel.fromJson(item)).toList();
    }
    throw Exception('Failed to load activity levels');
  }
  
  Future<List<FoodAllergy>> getFoodAllergies() async {
    final response = await apiClient.get('/api/v1/food-allergies/');
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((item) => FoodAllergy.fromJson(item)).toList();
    }
    throw Exception('Failed to load food allergies');
  }
  
  Future<List<HealthIssue>> getHealthIssues() async {
    final response = await apiClient.get('/api/v1/health-issues/');
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((item) => HealthIssue.fromJson(item)).toList();
    }
    throw Exception('Failed to load health issues');
  }
  
  // Add other endpoints...
}
```

### Step 4: Create BLoC/Provider for Pet Options

**Using Riverpod (Recommended):**

```dart
final languageManagerProvider = Provider((ref) => LanguageManager());

final apiClientProvider = Provider((ref) {
  final languageManager = ref.watch(languageManagerProvider);
  return ApiClient(
    baseUrl: 'https://your-api.com',
    languageManager: languageManager,
  );
});

final petOptionsRepositoryProvider = Provider((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return PetOptionsRepository(apiClient: apiClient);
});

final petTypesProvider = FutureProvider((ref) async {
  final repository = ref.watch(petOptionsRepositoryProvider);
  return repository.getPetTypes();
});

final gendersProvider = FutureProvider((ref) async {
  final repository = ref.watch(petOptionsRepositoryProvider);
  return repository.getGenders();
});

final ageCategoriesProvider = FutureProvider.family<List<AgeCategory>, int>(
  (ref, petTypeId) async {
    final repository = ref.watch(petOptionsRepositoryProvider);
    return repository.getAgeCategories(petTypeId);
  },
);

final activityLevelsProvider = FutureProvider((ref) async {
  final repository = ref.watch(petOptionsRepositoryProvider);
  return repository.getActivityLevels();
});

final foodAllergiesProvider = FutureProvider((ref) async {
  final repository = ref.watch(petOptionsRepositoryProvider);
  return repository.getFoodAllergies();
});

final healthIssuesProvider = FutureProvider((ref) async {
  final repository = ref.watch(petOptionsRepositoryProvider);
  return repository.getHealthIssues();
});

final currentLanguageProvider = StateNotifierProvider<
    LanguageNotifier,
    String>((ref) => LanguageNotifier());

class LanguageNotifier extends StateNotifier<String> {
  final LanguageManager languageManager;
  
  LanguageNotifier({this.languageManager = const LanguageManager()}) 
    : super('en') {
    _initialize();
  }
  
  Future<void> _initialize() async {
    await languageManager.initialize();
    state = languageManager.currentLanguage;
  }
  
  Future<void> setLanguage(String language) async {
    await languageManager.setLanguage(language);
    state = language;
  }
}
```

### Step 5: Use in UI

```dart
class PetFormScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final petTypes = ref.watch(petTypesProvider);
    final currentLanguage = ref.watch(currentLanguageProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: Text('Add Pet'),
        actions: [
          PopupMenuButton(
            itemBuilder: (context) => [
              PopupMenuItem(
                child: Text('English'),
                onTap: () => _changeLanguage(ref, 'en'),
              ),
              PopupMenuItem(
                child: Text('Türkçe'),
                onTap: () => _changeLanguage(ref, 'tr'),
              ),
              PopupMenuItem(
                child: Text('Nederlands'),
                onTap: () => _changeLanguage(ref, 'nl'),
              ),
              PopupMenuItem(
                child: Text('Suomalainen'),
                onTap: () => _changeLanguage(ref, 'fi'),
              ),
            ],
          ),
        ],
      ),
      body: petTypes.when(
        data: (types) => ListView.builder(
          itemCount: types.length,
          itemBuilder: (context, index) {
            return ListTile(
              title: Text(types[index].name), // Automatically in selected language!
              onTap: () => _selectPetType(context, types[index]),
            );
          },
        ),
        loading: () => Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
      ),
    );
  }
  
  void _changeLanguage(WidgetRef ref, String language) {
    ref.read(currentLanguageProvider.notifier).setLanguage(language);
    // All providers will automatically refresh with new language!
  }
}
```

### Step 6: Automatic Language Switching

When user changes language:

1. **LanguageManager** saves preference to SharedPreferences
2. **API Client** includes new language in `Accept-Language` header
3. **Backend** returns data in that language
4. **Riverpod** invalidates all pet option providers
5. **UI** automatically updates with translated content

```dart
void _changeLanguage(WidgetRef ref, String language) async {
  // Update language
  await ref.read(currentLanguageProvider.notifier).setLanguage(language);
  
  // Invalidate all pet option providers to refresh with new language
  ref.invalidate(petTypesProvider);
  ref.invalidate(gendersProvider);
  ref.invalidate(ageCategoriesProvider);
  ref.invalidate(activityLevelsProvider);
  ref.invalidate(foodAllergiesProvider);
  ref.invalidate(healthIssuesProvider);
  // ... invalidate other providers
}
```

---

## How the Backend Automatically Returns Translated Content

### Django ModelTranslation Magic

When you make a request with `Accept-Language: tr` header:

```
GET /api/v1/pet-types/
Accept-Language: tr
```

Django's `LocaleMiddleware` automatically:

1. **Parses** the `Accept-Language` header
2. **Sets** Django's language context to Turkish
3. **Activates** the Turkish translation layer
4. **Returns** translated field values

So when your serializer accesses `instance.name`, it automatically gets:
- `name_tr` for Turkish requests
- `name_en` for English requests
- Falls back to `name_en` if translation missing (via `MODELTRANSLATION_FALLBACK_LANGUAGES`)

---

## Complete Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    FLUTTER APP                                │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. User selects language (Dropdown/Settings)                │
│                         ↓                                      │
│  2. LanguageManager.setLanguage('tr')                        │
│      - Saves to SharedPreferences                            │
│      - Calls backend sync API                                │
│                         ↓                                      │
│  3. API Request with Accept-Language Header                  │
│      GET /api/v1/pet-types/                                  │
│      Headers: Accept-Language: tr                            │
│                         ↓                                      │
├──────────────────────────────────────────────────────────────┤
│                    DJANGO BACKEND                              │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  4. LocaleMiddleware captures Accept-Language                │
│      - Sets django.utils.translation.activate('tr')          │
│                         ↓                                      │
│  5. Serializer builds response                               │
│      - PetType.objects.all()                                 │
│      - Serializer accesses instance.name                     │
│      - ModelTranslation intercepts: returns name_tr          │
│                         ↓                                      │
│  6. Response JSON                                            │
│      [                                                       │
│        {"id": 1, "name": "Köpek"},  // Turkish for Dog       │
│        {"id": 2, "name": "Kedi"}    // Turkish for Cat       │
│      ]                                                        │
│                         ↓                                      │
├──────────────────────────────────────────────────────────────┤
│                    FLUTTER APP                                │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  7. Response received and parsed                             │
│      - UI automatically updates with Turkish names           │
│      - Riverpod invalidates and rebuilds widgets             │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Advantages

✅ **Automatic**: No manual language file maintenance needed
✅ **Efficient**: Single source of truth (database)
✅ **Flexible**: Easy to add new languages
✅ **Database-driven**: Admin can add/edit translations in Django Admin
✅ **Caching-friendly**: HTTP headers work with CDN caching
✅ **Fallback support**: Falls back to English if translation missing
✅ **SEO-friendly**: Each language version accessible via headers

---

## Troubleshooting

### Issue: Always getting English names even with different language header

**Solution**: Check that:
1. Django's `LocaleMiddleware` is installed in `MIDDLEWARE`
2. Your language code is valid (must be in `LANGUAGES` setting)
3. You've set translated values in Django Admin for that language
4. Cache isn't interfering (clear with appropriate cache headers)

### Issue: Translation fields not available in admin

**Solution**: 
- Ensure `modeltranslation` is in `INSTALLED_APPS` before `pet`
- Run `python manage.py makemigrations` (creates language-specific fields)
- Run `python manage.py migrate`
- Restart Django

### Issue: Fallback not working

**Ensure in settings.py**:
```python
MODELTRANSLATION_FALLBACK_LANGUAGES = ('en',)
```

---

## Summary

Your API automatically loads translated pet model content based on the `Accept-Language` HTTP header. Flutter just needs to:

1. Store user's language preference
2. Include `Accept-Language` header in all pet-related API requests
3. Refresh data when language changes

The rest happens automatically on the backend! 🎉
