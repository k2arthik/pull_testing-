import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth import get_user_model
from core.models import PriestProfile
from datetime import date, timedelta

User = get_user_model()

# Create Priest
priest_email = "priest_test@example.com"
priest_pass = "testpass123"
try:
    priest_user = User.objects.get(email=priest_email)
    print("Priest user exists")
except User.DoesNotExist:
    priest_user = User.objects.create_user(username="priest_test", email=priest_email, password=priest_pass)
    print("Created priest user")

try:
    profile = priest_user.priest_profile
    print("Priest profile exists")
except:
    profile = PriestProfile.objects.create(
        user=priest_user,
        fullname="Test Priest",
        mobile="1234567890",
        experience=5,
        language="English, Sanskrit",
        location="Test Location",
        services=['ganesh-homa', 'satyanarayan-pooja']
    )
    print("Created priest profile")

# Ensure services
if 'ganesh-homa' not in profile.services:
    profile.services.append('ganesh-homa')
    profile.save()
    print("Added ganesh-homa service")

# Create Devotee
devotee_email = "devotee_test@example.com"
devotee_pass = "testpass123"
try:
    devotee_user = User.objects.get(email=devotee_email)
    print("Devotee user exists")
except User.DoesNotExist:
    devotee_user = User.objects.create_user(username="devotee_test", email=devotee_email, password=devotee_pass)
    print("Created devotee user")

print("Setup complete")
