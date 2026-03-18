from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import DevoteeProfile

class DevoteeAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.forgot_url = reverse('devotee_forgot_password')
        self.verify_url = reverse('devotee_verify_otp')
        self.reset_url = reverse('devotee_reset_password')
        
        self.devotee_data = {
            'fullname': 'Test Devotee',
            'email': 'devotee@example.com',
            'mobile': '1234567890',
            'address': 'Test Address in Hyderabad', # Required field
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }

    def test_devotee_registration_success(self):
        response = self.client.post(self.signup_url, self.devotee_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(email='devotee@example.com').exists())
        user = User.objects.get(email='devotee@example.com')
        self.assertTrue(hasattr(user, 'devotee_profile'))
        self.assertEqual(user.devotee_profile.mobile, '1234567890')

    def test_devotee_registration_invalid_mobile(self):
        data = self.devotee_data.copy()
        data['mobile'] = '123' # Too short
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "exactly 10 digits")

    def test_devotee_login_success(self):
        # Register first
        self.client.post(self.signup_url, self.devotee_data)
        self.client.logout()
        
        # Login
        response = self.client.post(self.login_url, {
            'login_id': '1234567890',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('devotee_dashboard'))

    def test_devotee_login_email_success(self):
        # Register first
        self.client.post(self.signup_url, self.devotee_data)
        self.client.logout()
        
        # Login using email
        response = self.client.post(self.login_url, {
            'login_id': 'devotee@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('devotee_dashboard'))

    def test_devotee_login_email_case_and_whitespace_success(self):
        # Register first
        self.client.post(self.signup_url, self.devotee_data)
        self.client.logout()
        
        # Login using email with different case and spaces
        response = self.client.post(self.login_url, {
            'login_id': '  DEVOTEE@example.COM  ',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('devotee_dashboard'))

    def test_devotee_forgot_password_flow(self):
        # Register first
        self.client.post(self.signup_url, self.devotee_data)
        self.client.logout()
        
        # Step 1: Request OTP
        response = self.client.post(self.forgot_url, {'email': 'devotee@example.com'})
        self.assertEqual(response.status_code, 302)
        
        otp = self.client.session.get('devotee_reset_otp')
        self.assertIsNotNone(otp)
        
        # Step 2: Verify OTP
        response = self.client.post(self.verify_url, {'otp': otp})
        self.assertRedirects(response, self.reset_url)
        
        # Step 3: Reset Password
        new_pass = 'NewPassword123!'
        response = self.client.post(self.reset_url, {
            'password': new_pass,
            'confirm_password': new_pass
        })
        self.assertRedirects(response, self.login_url)
        
        # Verify login with new password
        login = self.client.login(username=User.objects.get(email='devotee@example.com').username, password=new_pass)
        self.assertTrue(login)
