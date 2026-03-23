from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import PriestProfile
from django.core.files.uploadedfile import SimpleUploadedFile

class PriestAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('purohit_signup')
        self.login_url = reverse('purohit_login')
        self.edit_url = reverse('purohit_edit_profile')
        self.dashboard_url = reverse('purohit_dashboard')
        
    def test_priest_registration_success(self):
        # Use a real minimal JPEG to pass ImageField validation
        small_jpg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\n\x00\n\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xe2\xe8\xa2\x8a\xf9\x93\xf7\x13\xff\xd9'
        photo = SimpleUploadedFile("test_photo.jpg", small_jpg, content_type="image/jpeg")
        
        response = self.client.post(self.signup_url, {
            'fullname': 'Test Priest',
            'email': 'priest@example.com',
            'mobile': '1234567890',
            'experience': 5,
            'language': 'English',
            'location': 'Test Location, Hyderabad',
            'specialization': 'Vedic Rituals',
            'gothram': 'Kashyap',
            'qualification': 'Vedic Scholar',
            'qualification_place': 'Varanasi',
            'formal_vedic_training': True,
            'knows_smaardham': True,
            'organize_scientifically': True,
            'can_perform_rituals': True,
            'password': 'Password123!',
            'photo': photo,
            'services': ['ganesh-homa', 'sudarshana-homa']
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        
        user = User.objects.get(email='priest@example.com')
        self.assertTrue(PriestProfile.objects.filter(user=user).exists())
        profile = user.priest_profile
        self.assertEqual(profile.fullname, 'Test Priest')
        self.assertEqual(profile.services, ['ganesh-homa', 'sudarshana-homa'])

    def test_priest_registration_duplicate_email(self):
        User.objects.create_user(username='existing', email='duplicate@example.com', password='Password123!')
        small_jpg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\n\x00\n\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xe2\xe8\xa2\x8a\xf9\x93\xf7\x13\xff\xd9'
        photo = SimpleUploadedFile("photo.jpg", small_jpg, content_type="image/jpeg")
        
        response = self.client.post(self.signup_url, {
            'fullname': 'New Priest',
            'email': 'DUPLICATE@example.com', # Case-insensitive
            'mobile': '1234567890',
            'experience': 5,
            'language': 'English',
            'location': 'Test Location, Hyderabad',
            'gothram': 'Kashyap',
            'qualification': 'Vedic Scholar',
            'qualification_place': 'Varanasi',
            'formal_vedic_training': True,
            'knows_smaardham': True,
            'organize_scientifically': True,
            'can_perform_rituals': True,
            'password': 'NewPassword123!',
            'photo': photo,
            'services': ['ganesh-homa']
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This email is already registered. Please use another email.")
        self.assertContains(response, 'value="New Priest"')

    def test_priest_login_success(self):
        user = User.objects.create_user(username='testpriest', email='priest@example.com', password='Password123!')
        PriestProfile.objects.create(
            user=user, fullname='Test Priest', mobile='1', experience=1, language='E', location='L'
        )
        
        response = self.client.post(self.login_url, {
            'login_id': '1',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)

    def test_priest_login_fail_wrong_password(self):
        user = User.objects.create_user(username='testpriest', email='priest@example.com', password='Password123!')
        PriestProfile.objects.create(user=user, fullname='T', mobile='1', experience=1, language='E', location='L')
        
        response = self.client.post(self.login_url, {
            'login_id': '1',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_priest_logout(self):
        user = User.objects.create_user(username='testpriest', email='priest@example.com', password='Password123!')
        PriestProfile.objects.create(user=user, fullname='T', mobile='1', experience=1, language='E', location='L')
        self.client.login(username='testpriest', password='Password123!')
        
        response = self.client.get(reverse('purohit_logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_priest_login_email_success(self):
        user = User.objects.create_user(username='testpriest_email', email='priest_email@example.com', password='Password123!')
        PriestProfile.objects.create(
            user=user, fullname='Test Priest Email', mobile='2', experience=1, language='E', location='L'
        )
        
        # Login using email
        response = self.client.post(self.login_url, {
            'login_id': 'priest_email@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)

    def test_priest_login_email_case_and_whitespace_success(self):
        user = User.objects.create_user(username='testpriest_space', email='Priest_Space@example.com', password='Password123!')
        PriestProfile.objects.create(
            user=user, fullname='Test Priest Space', mobile='3', experience=1, language='E', location='L'
        )
        
        # Login using email with different case and leading/trailing spaces
        response = self.client.post(self.login_url, {
            'login_id': '  priest_space@EXAMPLE.com  ',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)

    def test_priest_login_email_case_and_whitespace_success(self):
        user = User.objects.create_user(username='testpriest_space', email='Priest_Space@example.com', password='Password123!')
        PriestProfile.objects.create(
            user=user, fullname='Test Priest Space', mobile='3', experience=1, language='E', location='L'
        )
        
        # Login using email with different case and leading/trailing spaces
        response = self.client.post(self.login_url, {
            'login_id': '  priest_space@EXAMPLE.com  ',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)

    def test_priest_edit_profile_success(self):
        user = User.objects.create_user(username='testpriest', email='priest@example.com', password='Password123!')
        profile = PriestProfile.objects.create(
            user=user, fullname='Old Name', mobile='1234567890', experience=1, language='E', location='L, Hyderabad'
        )
        self.client.login(username='testpriest', password='Password123!')
        
        small_jpg = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00\n\x00\n\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xe2\xe8\xa2\x8a\xf9\x93\xf7\x13\xff\xd9'
        photo = SimpleUploadedFile("new_photo.jpg", small_jpg, content_type="image/jpeg")
        
        response = self.client.post(self.edit_url, {
            'fullname': 'New Name',
            'mobile': '0987654321',
            'experience': 10,
            'language': 'English',
            'location': 'New Location, Hyderabad',
            'gothram': 'New Gothram',
            'qualification': 'New Qual',
            'qualification_place': 'New Place',
            'formal_vedic_training': True,
            'knows_smaardham': True,
            'organize_scientifically': True,
            'can_perform_rituals': True,
            'photo': photo,
            'services': ['santana-gopala-homa']
        })
        self.assertEqual(response.status_code, 302)
        
        profile.refresh_from_db()
        self.assertEqual(profile.fullname, 'New Name')
        self.assertEqual(profile.experience, 10)
        self.assertEqual(profile.services, ['santana-gopala-homa'])

class PriestForgotPasswordTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.forgot_url = reverse('purohit_forgot_password')
        self.verify_otp_url = reverse('purohit_verify_otp')
        self.reset_url = reverse('purohit_reset_password')
        self.login_url = reverse('purohit_login')
        
        # Create a user and priest profile
        self.password = 'OldPassword123!'
        self.user = User.objects.create_user(username='testpriest', email='priest@example.com', password=self.password)
        self.profile = PriestProfile.objects.create(
            user=self.user, 
            fullname='Test Priest', 
            mobile='9876543210', 
            experience=5, 
            language='English', 
            location='Test Location, Hyderabad'
        )

    def test_forgot_password_flow_success(self):
        # Step 1: Request OTP
        email = 'priest@example.com'
        response = self.client.post(self.forgot_url, {'email': email})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.verify_otp_url)
        
        # Verify OTP in session
        self.assertEqual(self.client.session['reset_email'], 'priest@example.com')
        self.assertTrue('reset_otp' in self.client.session)
        otp = self.client.session['reset_otp']
        
        # Step 2: Verify OTP
        response = self.client.post(self.verify_otp_url, {'otp': otp})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.reset_url)
        self.assertTrue(self.client.session.get('otp_verified'))
        
        # Check session verified flag
        session = self.client.session
        self.assertTrue(session['otp_verified'])
        
        # Step 3: Reset Password
        new_password = 'NewStrongPassword1@'
        response = self.client.post(self.reset_url, {
            'password': new_password,
            'confirm_password': new_password
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        
        # Verify login with new password
        self.client.logout()
        login = self.client.login(username='testpriest', password=new_password)
        self.assertTrue(login)
        
        # Verify old password fails
        self.client.logout()
        login = self.client.login(username='testpriest', password=self.password)
        self.assertFalse(login)

    def test_forgot_password_invalid_email(self):
        response = self.client.post(self.forgot_url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email address not registered")

    def test_verify_otp_invalid(self):
        # Manually set session
        session = self.client.session
        session['reset_email'] = 'priest@example.com'
        session['reset_otp'] = '123456'
        session.save()
        
        response = self.client.post(self.verify_otp_url, {'otp': '000000'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid OTP")

    def test_reset_password_mismatch(self):
        # Manually set session
        session = self.client.session
        session['reset_email'] = 'priest@example.com'
        session['otp_verified'] = True
        session.save()
        
        response = self.client.post(self.reset_url, {
            'password': 'Password1!',
            'confirm_password': 'Password2@'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")

