from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import PriestProfile
import json

class ServiceParsingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testpriest', password='password')
        self.profile = PriestProfile.objects.create(
            user=self.user,
            fullname="Test Priest",
            mobile="1234567890",
            experience=5,
            language="Sanskrit",
            location="Test Location",
            services=[] # Will be updated in tests
        )
        self.client.login(username='testpriest', password='password')

    def test_services_as_list(self):
        """Test when services is stored as a proper list."""
        self.profile.services = ["ganesh-homa", "satyanarayan-pooja"]
        self.profile.save()
        
        try:
            response = self.client.get('/purohit-dashboard/')
            if response.status_code != 200:
                print(f"Status Code: {response.status_code}")
                if response.status_code == 302:
                    print(f"Redirect URL: {response.url}")
            
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Ganesh Homa")
            self.assertContains(response, "Satyanarayan Pooja")
        except Exception as e:
            print(f"Test Exception: {e}")
            raise

    def test_services_as_comma_separated_string(self):
        """Test when services is stored as a comma-separated string."""
        self.profile.services = "ganesh-homa, satyanarayan-pooja" 
        self.profile.save()
        
        try:
            response = self.client.get('/purohit-dashboard/')
            if response.status_code != 200:
                print(f"Status Code: {response.status_code}")
                if response.status_code == 302:
                    print(f"Redirect URL: {response.url}")

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Ganesh Homa")
            self.assertContains(response, "Satyanarayan Pooja")
        except Exception as e:
            print(f"Test Exception: {e}")
            raise

    def test_services_as_json_string(self):
        """Test when services is stored as a JSON string."""
        self.profile.services = json.dumps(["ganesh-homa", "satyanarayan-pooja"])
        self.profile.save()
        
        try:
            response = self.client.get('/purohit-dashboard/')
            if response.status_code != 200:
                print(f"Status Code: {response.status_code}")
                if response.status_code == 302:
                    print(f"Redirect URL: {response.url}")

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Ganesh Homa")
            self.assertContains(response, "Satyanarayan Pooja")
        except Exception as e:
            print(f"Test Exception: {e}")
            raise
