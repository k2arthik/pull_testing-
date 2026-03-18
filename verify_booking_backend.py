import os
import django
import json
import traceback
import re
from datetime import date, timedelta

print("Starting verification script...")

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
    django.setup()
    print("Django setup complete.")

    from django.conf import settings
    settings.ALLOWED_HOSTS += ['testserver']

    from django.test import Client
    from django.contrib.auth import get_user_model
    from core.models import PriestProfile, PriestAvailability, Booking

    User = get_user_model()

    print("Fetching users...")
    try:
        priest_user = User.objects.get(username="priest_test")
        devotee_user = User.objects.get(username="devotee_test")
        priest_profile = priest_user.priest_profile
        print(f"Users found: Priest={priest_user}, Devotee={devotee_user}")
    except Exception as e:
        print(f"User fetch failed: {e}")
        exit(1)

    tomorrow = date.today() + timedelta(days=1)
    tomorrow_str = tomorrow.isoformat()

    # 1. Test Save Availability
    print("\n--- 1. Testing Save Availability ---")
    client = Client()
    client.force_login(priest_user)

    data = {
        "date": tomorrow_str,
        "morning": {"available": True, "start": "06:00", "end": "12:00"},
        "afternoon": {"available": False},
        "evening": {"available": False},
        "custom_slots": [],
        "notes": "Testing notes"
    }

    try:
        response = client.post(
            '/api/availability/save/',
            data=json.dumps(data),
            content_type='application/json'
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            content = response.content.decode('utf-8')
            title = re.search(r'<title>(.*?)</title>', content)
            if title:
                print(f"Error Title: {title.group(1)}")
            exception = re.search(r'<th>Exception Value:</th>\s*<td><pre class="exception_value">(.*?)</pre>', content, re.DOTALL)
            if exception:
                print(f"Exception Value: {exception.group(1)}")
    except Exception as e:
        print(f"Client POST failed: {e}")
        traceback.print_exc()

    # 2. Test Public API
    print("\n--- 2. Testing Public API ---")
    client.logout()
    try:
        response = client.get(f'/api/availability/public/{priest_profile.id}/?date={tomorrow_str}')
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response Data: {response.json()}")
        else:
            content = response.content.decode('utf-8')
            title = re.search(r'<title>(.*?)</title>', content)
            if title:
                 print(f"Error Title: {title.group(1)}")
    except Exception as e:
        print(f"Client GET failed: {e}")

    # 3. Test Booking
    print("\n--- 3. Testing Booking ---")
    client.force_login(devotee_user)
    booking_data = {
        "booking_date": tomorrow_str,
        "slot_type": "morning",
        "start_time": "08:00:00", # Explicit seconds
        "end_time": "09:00:00",
        "phone": "9876543210",
        "address": "Test Address",
        "special_requests": ""
    }
    
    try:
        response = client.post(
            f'/book/priest/{priest_profile.id}/?service=ganesh-homa',
            data=booking_data
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 302:
            print(f"Redirect URL: {response.url}")
        else:
            content = response.content.decode('utf-8')
            title = re.search(r'<title>(.*?)</title>', content)
            if title:
                 print(f"Error Title: {title.group(1)}")
            exception = re.search(r'<th>Exception Value:</th>\s*<td><pre class="exception_value">(.*?)</pre>', content, re.DOTALL)
            if exception:
                print(f"Exception Value: {exception.group(1)}")

    except Exception as e:
        print(f"Client POST Booking failed: {e}")

except Exception:
    traceback.print_exc()
