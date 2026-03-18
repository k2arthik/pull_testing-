import os
import django
import sys
import traceback

# Configure Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import DevoteeProfile, PriestProfile
from django.urls import reverse

def test():
    try:
        mobile = "9988776655"
        email = "repro_devotee@test.com"
        password = "password123"
        
        User.objects.filter(email=email).delete()
        User.objects.filter(username__startswith='repro_devotee').delete()
        user = User.objects.create_user(username='repro_devotee', email=email, password=password)
        DevoteeProfile.objects.create(user=user, fullname="Repro Devotee", mobile=mobile, address="Hyderabad Test Address")
        
        client = Client()
        print("Submitting post request...")
        response = client.post(reverse('login'), {'login_id': mobile, 'password': password})
        print(f"Status: {response.status_code}")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test()
