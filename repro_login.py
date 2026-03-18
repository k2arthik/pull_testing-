import os
import django
import sys

# Configure Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from core.models import DevoteeProfile, PriestProfile
from django.urls import reverse

def test_mobile_login():
    # Setup test devotee
    mobile = "9988776655"
    email = "repro_devotee@test.com"
    password = "password123"
    
    # Cleanup
    User.objects.filter(email=email).delete()
    User.objects.filter(username__startswith='repro_devotee').delete()
    
    user = User.objects.create_user(username='repro_devotee', email=email, password=password)
    DevoteeProfile.objects.create(user=user, fullname="Repro Devotee", mobile=mobile, address="Hyderabad Test Address")
    
    print(f"Created Devotee: {user.username} with mobile: {mobile}")
    
    client = Client()
    
    # Test Devotee Login with Mobile
    print("\n--- Testing Devotee Login with Mobile ---")
    response = client.post(reverse('login'), {'login_id': mobile, 'password': password})
    print(f"Status: {response.status_code}")
    if response.status_code == 302:
        print(f"Redirected to: {response['Location']}")
    else:
        # Check for messages
        messages = list(response.context.get('messages', [])) if response.context else []
        for msg in messages:
            print(f"Message: {msg}")
            
    # Test Purohit Login with Mobile
    print("\n--- Testing Purohit Login with Mobile ---")
    p_mobile = "8877665544"
    p_email = "repro_priest@test.com"
    
    User.objects.filter(email=p_email).delete()
    p_user = User.objects.create_user(username='repro_priest', email=p_email, password=password)
    PriestProfile.objects.create(
        user=p_user, 
        fullname="Repro Priest", 
        mobile=p_mobile, 
        experience=5, 
        location="Hyderabad Temple",
        language=["Telugu"]
    )
    
    print(f"Created Priest: {p_user.username} with mobile: {p_mobile}")
    
    response = client.post(reverse('purohit_login'), {'login_id': p_mobile, 'password': password})
    print(f"Status: {response.status_code}")
    if response.status_code == 302:
        print(f"Redirected to: {response['Location']}")
    else:
        # Check if it fails form validation
        if 'form' in response.context:
            print(f"Form Errors: {response.context['form'].errors}")
        messages = list(response.context.get('messages', [])) if response.context else []
        for msg in messages:
            print(f"Message: {msg}")

if __name__ == "__main__":
    test_mobile_login()
