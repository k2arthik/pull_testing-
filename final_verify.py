import os
import django
import datetime
from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
django.setup()

from core.models import PriestAvailability, Booking, PriestProfile
from django.test import RequestFactory
from core.views import purohit_dashboard
from django.contrib.messages.storage.fallback import FallbackStorage

def run_final_check():
    print("Checking PriestAvailability.date types:")
    for av in PriestAvailability.objects.all():
        print(f"ID: {av.id}, Value: {av.date}, Type: {type(av.date)}")
    
    print("\nChecking Booking.booking_date types:")
    for b in Booking.objects.all():
        print(f"ID: {b.id}, Value: {b.booking_date}, Type: {type(b.booking_date)}")

    # Try to call the dashboard for the first priest found
    profile = PriestProfile.objects.first()
    if profile:
        print(f"\nTesting dashboard for priest: {profile.fullname}")
        factory = RequestFactory()
        request = factory.get('/purohit/dashboard/')
        request.user = profile.user
        setattr(request, '_messages', FallbackStorage(request))
        
        try:
            response = purohit_dashboard(request)
            print("Dashboard status code:", response.status_code)
            if response.status_code == 200:
                print("SUCCESS: Dashboard rendered correctly.")
        except Exception as e:
            print("FAILURE: Dashboard failed with error:", e)
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_final_check()
