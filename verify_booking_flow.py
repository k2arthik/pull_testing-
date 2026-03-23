import os
import django
from django.test import Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from core.models import PriestProfile, Booking

User = get_user_model()

@override_settings(ALLOWED_HOSTS=['*'])
def test_booking_flow():
    print("Testing Booking Flow and Validation...")
    client = Client()
    
    # Create test user
    user, _ = User.objects.get_or_create(username="devotee_test", email="devotee@example.com")
    user.set_password("pass123")
    user.save()
    
    # Create test priest
    priest_user, _ = User.objects.get_or_create(username="priest_test", email="priest@example.com")
    priest, _ = PriestProfile.objects.get_or_create(
        user=priest_user,
        fullname="Purohit Test",
        mobile="1234567890",
        experience=10,
        location="Hyderabad"
    )
    
    client.login(username="devotee_test", password="pass123")
    
    booking_date = (timezone.now() + timedelta(days=3)).date().isoformat()
    
    print("\n--- Testing Invalid Address (Chennai) ---")
    response = client.post(reverse('book_priest', args=[priest.id]), {
        'booking_date': booking_date,
        'slot_type': 'morning',
        'start_time': '08:00',
        'end_time': '10:00',
        'devotee_name': 'Test Devotee',
        'phone': '9876543210',
        'address': 'T Nagar, Chennai',
    }, follow=True)
    
    messages = []
    if response.context:
        messages = list(response.context.get('messages', []))
    else:
        # Check if messages are in the redirect response if follow=True didn't catch them
        # Usually follow=True handles it, but just in case
        print("Warning: response.context is None. This could be due to a redirect or Bad Request.")
    error_found = any("Hyderabad only" in str(m) for m in messages)
    if error_found:
        print("PASS: Booking with Chennai failed with correct message.")
    else:
        print(f"FAIL: Booking with Chennai did not show Hyderabad error. Messages: {messages}")

    print("\n--- Testing Valid Booking (Hyderabad) ---")
    response = client.post(reverse('book_priest', args=[priest.id]), {
        'booking_date': booking_date,
        'slot_type': 'morning',
        'start_time': '10:00',
        'end_time': '12:00',
        'devotee_name': 'Test Devotee',
        'phone': '9876543210',
        'address': 'Madhapur, Hyderabad',
    }, follow=True)
    
    if response.status_code == 200 and 'booking_success' in response.redirect_chain[-1][0]:
        print("PASS: Redirected to booking success page.")
    else:
        print(f"FAIL: Did not redirect to success page. Last response: {response.status_code}")
        # Check for errors in context if it didn't redirect
        msgs = list(response.context.get('messages', [])) if response.context else []
        print(f"Messages found: {msgs}")

if __name__ == "__main__":
    test_booking_flow()
