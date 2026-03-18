import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from core.models import PriestProfile, PriestAvailability, Booking

print("Checking PriestAvailability records...")
for av in PriestAvailability.objects.all():
    try:
        print(f"ID: {av.id}, Priest: {av.priest.fullname}, Date: {av.date} (type: {type(av.date)})")
    except Exception as e:
        print(f"Error in PriestAvailability ID {av.id}: {e}")

print("\nChecking Booking records...")
for b in Booking.objects.all():
    try:
        print(f"ID: {b.id}, Priest: {b.priest.fullname}, Date: {b.booking_date} (type: {type(b.booking_date)})")
    except Exception as e:
        print(f"Error in Booking ID {b.id}: {e}")
