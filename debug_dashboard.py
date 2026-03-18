
import os
import django
import sys

# Add the current directory to sys.path to ensure imports work correctly
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'karya_siddhi.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PriestProfile, PriestAvailability, Booking
from django.utils import timezone
from datetime import timedelta
from django.test import Client
from django.urls import reverse

def debug_render():
    # Cleanup existing test data if any
    User.objects.filter(username='debug_priest').delete()
    
    # Create test data
    user = User.objects.create_user(username='debug_priest', email='debug@test.com', password='password123')
    profile = PriestProfile.objects.create(
        user=user,
        fullname="Debug Priest",
        mobile="1234567890",
        experience=10,
        location="Debug Temple"
    )
    
    # Add availability
    tomorrow = timezone.now().date() + timedelta(days=1)
    PriestAvailability.objects.create(
        priest=profile,
        date=tomorrow,
        morning_available=True,
        morning_start="06:00:00",
        morning_end="12:00:00"
    )
    
    client = Client()
    client.force_login(user)
    
    response = client.get(reverse('purohit_dashboard'))
    
    print("STATUS CODE:", response.status_code)
    print("--- CONTENT START ---")
    print(response.content.decode())
    print("--- CONTENT END ---")

if __name__ == "__main__":
    debug_render()
