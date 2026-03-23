import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PriestProfile, DevoteeProfile

print("--- Recent Users ---")
for user in User.objects.order_by('-date_joined')[:5]:
    print(f"User: {user.username}, Email: {user.email}, Joined: {user.date_joined}")

print("\n--- Recent Priest Profiles ---")
for p in PriestProfile.objects.order_by('-created_at')[:5]:
    print(f"Priest: {p.fullname}, Email: {p.user.email}, Created: {p.created_at}")

print("\n--- Recent Devotee Profiles ---")
for d in DevoteeProfile.objects.order_by('-created_at')[:5]:
    print(f"Devotee: {d.fullname}, Email: {d.user.email}, Created: {d.created_at}")
