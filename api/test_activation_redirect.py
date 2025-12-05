"""
Test activation flow for API signup users

This test verifies that:
1. Users who sign up via API (with password) are redirected to login after activation
2. Users who sign up via web wizard (no password) are redirected to password setup
3. Mobile app users get deep link redirect
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class ActivationRedirectTest(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_api_signup_user_redirects_to_login_after_activation(self):
        """User with password (API signup) should redirect to login"""
        # Create inactive user with password (simulates API signup)
        user = User.objects.create_user(
            email='api_user@example.com',
            password='TestPassword123!',
            is_active=False
        )
        
        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = f'/en/users/activate/{uid}/{token}/'
        
        # Click activation link
        response = self.client.get(activation_url, follow=True)
        
        # Should redirect to login page
        self.assertRedirects(response, '/en/users/login/', status_code=302)
        
        # User should be activated
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Should show success message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('activated successfully', str(messages[0]))
    
    def test_mobile_app_user_redirects_to_deep_link(self):
        """Mobile app user should get deep link redirect"""
        # Create inactive user with password
        user = User.objects.create_user(
            email='mobile_user@example.com',
            password='TestPassword123!',
            is_active=False
        )
        
        # Generate activation link with source=app parameter
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = f'/en/users/activate/{uid}/{token}/?source=app'
        
        # Click activation link
        response = self.client.get(activation_url, follow=False)
        
        # Should redirect to deep link
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('fammo://login'))
        self.assertIn('activated=true', response.url)
        self.assertIn('mobile_user@example.com', response.url)
        
        # User should be activated
        user.refresh_from_db()
        self.assertTrue(user.is_active)
    
    def test_web_wizard_user_redirects_to_password_setup(self):
        """User without password (web wizard) should redirect to password setup"""
        # Create inactive user WITHOUT password (simulates web wizard)
        user = User.objects.create(
            email='wizard_user@example.com',
            is_active=False
        )
        # Don't set password - user.set_unusable_password() is called by default
        
        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = f'/en/users/activate/{uid}/{token}/'
        
        # Click activation link
        response = self.client.get(activation_url, follow=True)
        
        # Should redirect to password setup page
        self.assertRedirects(response, '/en/users/set-password-after-activation/', status_code=302)
        
        # User should be activated
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Session should contain user ID
        session = self.client.session
        self.assertIn('newly_activated_user_id', session)
        self.assertEqual(session['newly_activated_user_id'], user.pk)
    
    def test_invalid_activation_link_redirects_to_login(self):
        """Invalid activation link should show error and redirect to login"""
        # Use invalid token
        activation_url = '/en/users/activate/invalid/invalid/'
        
        # Click activation link
        response = self.client.get(activation_url, follow=True)
        
        # Should redirect to login
        self.assertRedirects(response, '/en/users/login/', status_code=302)
        
        # Should show error message
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('invalid', str(messages[0]).lower())
    
    def test_already_active_user_still_works(self):
        """Already active user clicking link again should still work"""
        # Create active user with password
        user = User.objects.create_user(
            email='active_user@example.com',
            password='TestPassword123!',
            is_active=True  # Already active
        )
        
        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_url = f'/en/users/activate/{uid}/{token}/'
        
        # Click activation link
        response = self.client.get(activation_url, follow=True)
        
        # Should still redirect to login (gracefully handle already active)
        self.assertRedirects(response, '/en/users/login/', status_code=302)


if __name__ == '__main__':
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
    django.setup()
    
    import unittest
    unittest.main()
