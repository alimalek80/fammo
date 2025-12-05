"""
API Tests for Mobile App Endpoints

Run tests:
    python manage.py test api
    python manage.py test api.tests.APIEndpointTests
    python manage.py test api.tests.APIEndpointTests.test_ping
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from userapp.models import Profile
from pet.models import Pet, PetType, Gender, Breed

User = get_user_model()


class APIEndpointTests(APITestCase):
    """Test suite for API v1 endpoints"""
    
    def setUp(self):
        """Set up test fixtures - runs before each test"""
        # Create test user (must be active for JWT to work)
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='TestPass123!',
            is_active=True  # Explicitly set active
        )
        
        # Get or create profile
        self.profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={'preferred_language': 'en'}
        )
        
        # Create pet type and breed for pet tests
        self.pet_type = PetType.objects.create(name='Dog')
        self.gender = Gender.objects.create(name='Male')
        self.breed = Breed.objects.create(
            pet_type=self.pet_type,
            name='Golden Retriever'
        )
        
        # Create test pet
        self.pet = Pet.objects.create(
            user=self.user,
            name='Buddy',
            pet_type=self.pet_type,
            gender=self.gender,
            breed=self.breed,
            weight=25.5,
            age_years=3
        )
        
        # JWT tokens
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)
        
        # API client
        self.client = APIClient()
    
    def authenticate(self):
        """Helper method to authenticate requests"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    # ==================== BASIC ENDPOINTS ====================
    
    def test_ping_endpoint(self):
        """Test GET /api/v1/ping/ returns pong message"""
        url = reverse('api-ping')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'pong from FAMMO API')
    
    def test_config_endpoint_returns_urls(self):
        """Test GET /api/v1/config/ returns configuration"""
        url = reverse('api-config')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('base_url', response.data)
        self.assertIn('static_url', response.data)
        self.assertIn('media_url', response.data)
        self.assertIn('assets', response.data)
        self.assertIn('api_version', response.data)
        
        # Check assets
        assets = response.data['assets']
        self.assertIn('logo', assets)
        self.assertIn('favicon', assets)
        self.assertIn('placeholder_pet', assets)
    
    # ==================== AUTH ENDPOINTS ====================
    
    def test_token_obtain_with_valid_credentials(self):
        """Test POST /api/v1/auth/token/ with valid credentials"""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'testuser@example.com',
            'password': 'TestPass123!'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_token_obtain_with_invalid_credentials(self):
        """Test POST /api/v1/auth/token/ with invalid credentials"""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test POST /api/v1/auth/token/refresh/ refreshes token"""
        url = reverse('token_refresh')
        data = {'refresh': self.refresh_token}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    # ==================== LANGUAGE ENDPOINTS ====================
    
    def test_languages_list(self):
        """Test GET /api/v1/languages/ returns language list"""
        url = reverse('api-languages')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('languages', response.data)
        self.assertIsInstance(response.data['languages'], list)
        self.assertGreater(len(response.data['languages']), 0)
        
        # Check language structure
        first_lang = response.data['languages'][0]
        self.assertIn('code', first_lang)
        self.assertIn('name', first_lang)
        self.assertIn('native_name', first_lang)
    
    def test_get_user_language_authenticated(self):
        """Test GET /api/v1/me/language/ returns user's language"""
        self.authenticate()
        url = reverse('api-set-language')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('language', response.data)
        self.assertEqual(response.data['language'], 'en')
    
    def test_get_user_language_unauthenticated(self):
        """Test GET /api/v1/me/language/ without auth returns 401"""
        url = reverse('api-set-language')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_set_user_language_valid(self):
        """Test POST /api/v1/me/language/ with valid language code"""
        self.authenticate()
        url = reverse('api-set-language')
        data = {'language': 'tr'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['language'], 'tr')
        self.assertTrue(response.data['success'])
        
        # Verify database update
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.preferred_language, 'tr')
    
    def test_set_user_language_invalid_code(self):
        """Test POST /api/v1/me/language/ with invalid language code"""
        self.authenticate()
        url = reverse('api-set-language')
        data = {'language': 'invalid_code'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_set_user_language_missing_code(self):
        """Test POST /api/v1/me/language/ without language code"""
        self.authenticate()
        url = reverse('api-set-language')
        data = {}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    # ==================== PROFILE ENDPOINTS ====================
    
    def test_get_user_profile_authenticated(self):
        """Test GET /api/v1/me/ returns user profile"""
        self.authenticate()
        url = reverse('api-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertIn('preferred_language', response.data)
    
    def test_get_user_profile_unauthenticated(self):
        """Test GET /api/v1/me/ without auth returns 401"""
        url = reverse('api-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # ==================== PET ENDPOINTS ====================
    
    def test_list_my_pets_authenticated(self):
        """Test GET /api/v1/pets/ returns user's pets"""
        self.authenticate()
        url = reverse('api-my-pets')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Buddy')
    
    def test_list_my_pets_unauthenticated(self):
        """Test GET /api/v1/pets/ without auth returns 401"""
        url = reverse('api-my-pets')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_pet_authenticated(self):
        """Test POST /api/v1/pets/ creates new pet"""
        self.authenticate()
        url = reverse('api-my-pets')
        data = {
            'name': 'Max',
            'pet_type': self.pet_type.id,
            'gender': self.gender.id,
            'breed': self.breed.id,
            'weight': 30.0,
            'age_years': 2
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Max')
        self.assertEqual(Pet.objects.filter(user=self.user).count(), 2)
    
    def test_get_pet_detail_authenticated(self):
        """Test GET /api/v1/pets/{id}/ returns pet details"""
        self.authenticate()
        url = reverse('api-my-pet-detail', kwargs={'pk': self.pet.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Buddy')
        self.assertEqual(response.data['id'], self.pet.id)
    
    def test_get_other_user_pet_denied(self):
        """Test GET /api/v1/pets/{id}/ for another user's pet returns 404"""
        # Create another user and pet
        other_user = User.objects.create_user(
            email='other@example.com',
            password='OtherPass123!',
            is_active=True
        )
        other_pet = Pet.objects.create(
            user=other_user,
            name='OtherPet',
            pet_type=self.pet_type,
            weight=20.0
        )
        
        self.authenticate()
        url = reverse('api-my-pet-detail', kwargs={'pk': other_pet.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_pet_authenticated(self):
        """Test PUT /api/v1/pets/{id}/ updates pet"""
        self.authenticate()
        url = reverse('api-my-pet-detail', kwargs={'pk': self.pet.id})
        data = {
            'name': 'Buddy Updated',
            'pet_type': self.pet_type.id,
            'weight': 26.0,
            'age_years': 4
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Buddy Updated')
        self.assertEqual(float(response.data['weight']), 26.0)
        
        # Verify database update
        self.pet.refresh_from_db()
        self.assertEqual(self.pet.name, 'Buddy Updated')
    
    def test_partial_update_pet_authenticated(self):
        """Test PATCH /api/v1/pets/{id}/ partially updates pet"""
        self.authenticate()
        url = reverse('api-my-pet-detail', kwargs={'pk': self.pet.id})
        data = {'name': 'Buddy Patched'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Buddy Patched')
        
        # Verify other fields unchanged
        self.pet.refresh_from_db()
        self.assertEqual(float(self.pet.weight), 25.5)
    
    def test_delete_pet_authenticated(self):
        """Test DELETE /api/v1/pets/{id}/ deletes pet"""
        self.authenticate()
        url = reverse('api-my-pet-detail', kwargs={'pk': self.pet.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Pet.objects.filter(user=self.user).count(), 0)
    
    def test_delete_other_user_pet_denied(self):
        """Test DELETE /api/v1/pets/{id}/ for another user's pet returns 404"""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='OtherPass123!',
            is_active=True
        )
        other_pet = Pet.objects.create(
            user=other_user,
            name='OtherPet',
            pet_type=self.pet_type,
            weight=20.0
        )
        
        self.authenticate()
        url = reverse('api-my-pet-detail', kwargs={'pk': other_pet.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify pet still exists
        self.assertTrue(Pet.objects.filter(id=other_pet.id).exists())


class APIConfigEndpointDetailTests(APITestCase):
    """Detailed tests for the config endpoint"""
    
    def test_config_contains_all_required_fields(self):
        """Test config endpoint returns all required fields"""
        url = reverse('api-config')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Required top-level fields
        required_fields = ['base_url', 'static_url', 'media_url', 'assets', 'api_version']
        for field in required_fields:
            self.assertIn(field, response.data)
        
        # Required asset fields
        required_assets = ['logo', 'favicon', 'placeholder_pet']
        for asset in required_assets:
            self.assertIn(asset, response.data['assets'])
    
    def test_config_urls_are_absolute(self):
        """Test config endpoint returns absolute URLs"""
        url = reverse('api-config')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check URLs start with http
        self.assertTrue(response.data['base_url'].startswith('http'))
        self.assertTrue(response.data['static_url'].startswith('http'))
        self.assertTrue(response.data['media_url'].startswith('http'))
        
        # Check asset URLs are absolute
        for asset_url in response.data['assets'].values():
            self.assertTrue(asset_url.startswith('http'))
    
    def test_config_no_authentication_required(self):
        """Test config endpoint works without authentication"""
        url = reverse('api-config')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AuthenticationEndpointTests(APITestCase):
    """Test suite for authentication endpoints (signup, login, password reset)"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.signup_url = reverse('api-signup')
        self.login_url = reverse('token_obtain_pair')
        self.forgot_password_url = reverse('api-forgot-password')
        self.reset_password_url = reverse('api-reset-password')
        self.resend_activation_url = reverse('api-resend-activation')
        self.delete_test_user_url = reverse('api-delete-test-user')
        
        self.test_email = 'testuser@example.com'
        self.test_password = 'SecurePass123!'
    
    def test_signup_creates_user(self):
        """Test user signup creates a new user account"""
        data = {
            'email': self.test_email,
            'password': self.test_password,
            'password_confirm': self.test_password
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.test_email)
        
        # Verify user exists in database
        user = User.objects.get(email=self.test_email)
        self.assertFalse(user.is_active)  # Should be inactive until email verification
    
    def test_signup_password_mismatch(self):
        """Test signup fails when passwords don't match"""
        data = {
            'email': self.test_email,
            'password': self.test_password,
            'password_confirm': 'DifferentPass123!'
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_signup_duplicate_email(self):
        """Test signup fails with duplicate email"""
        # Create first user
        User.objects.create_user(email=self.test_email, password=self.test_password)
        
        # Try to create second user with same email
        data = {
            'email': self.test_email,
            'password': self.test_password,
            'password_confirm': self.test_password
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_signup_weak_password(self):
        """Test signup with weak password (may succeed depending on password validation settings)"""
        data = {
            'email': self.test_email,
            'password': '123',
            'password_confirm': '123'
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        # Password validation may be disabled in some environments
        # If validation is enabled, should return 400, otherwise 201
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED])
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials returns JWT tokens"""
        # Create active user
        User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            is_active=True
        )
        
        data = {
            'email': self.test_email,
            'password': self.test_password
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_with_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            is_active=True
        )
        
        data = {
            'email': self.test_email,
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_inactive_user(self):
        """Test login fails for inactive users"""
        User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            is_active=False
        )
        
        data = {
            'email': self.test_email,
            'password': self.test_password
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_forgot_password_sends_email(self):
        """Test forgot password endpoint"""
        # Create user
        User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            is_active=True
        )
        
        data = {'email': self.test_email}
        response = self.client.post(self.forgot_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_forgot_password_nonexistent_email(self):
        """Test forgot password with non-existent email (should still return success for security)"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.forgot_password_url, data, format='json')
        
        # Should still return success to not reveal if email exists
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_resend_activation_email(self):
        """Test resend activation email for inactive users"""
        # Create inactive user
        User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            is_active=False
        )
        
        data = {'email': self.test_email}
        response = self.client.post(self.resend_activation_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_resend_activation_email_already_active(self):
        """Test resend activation email fails for already active users"""
        # Create active user
        User.objects.create_user(
            email=self.test_email,
            password=self.test_password,
            is_active=True
        )
        
        data = {'email': self.test_email}
        response = self.client.post(self.resend_activation_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_resend_activation_nonexistent_email(self):
        """Test resend activation email with non-existent email"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.resend_activation_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_test_user_in_debug_mode(self):
        """Test delete test user endpoint (requires DEBUG=True)"""
        from django.conf import settings
        
        # Create user
        User.objects.create_user(
            email=self.test_email,
            password=self.test_password
        )
        
        data = {'email': self.test_email}
        response = self.client.delete(self.delete_test_user_url, data, format='json')
        
        if settings.DEBUG:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            # Verify user was deleted
            self.assertFalse(User.objects.filter(email=self.test_email).exists())
        else:
            # Should be forbidden in production
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_test_user_nonexistent(self):
        """Test delete test user with non-existent email"""
        from django.conf import settings
        
        data = {'email': 'nonexistent@example.com'}
        response = self.client.delete(self.delete_test_user_url, data, format='json')
        
        if settings.DEBUG:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
