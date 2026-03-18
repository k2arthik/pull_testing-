import os
import django
from django.test import RequestFactory
from django.contrib.auth.models import User
from core.models import PriestProfile, PriestAvailability
from core.views import purohit_dashboard
from django.contrib.messages.storage.fallback import FallbackStorage

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
django.setup()

def debug_dashboard():
    # Setup
    user = User.objects.filter(username='priest').first()
    if not user:
        user = User.objects.create_user(username='priest', password='password123')
    
    profile, created = PriestProfile.objects.get_or_create(
        user=user,
        defaults={'fullname': 'Debug Priest', 'experience': 5, 'mobile': '123'}
    )
    
    # Create availability
    from datetime import date
    PriestAvailability.objects.get_or_create(
        priest=profile,
        date=date.today(),
        defaults={'morning_available': True, 'morning_start': '08:00', 'morning_end': '12:00'}
    )
    
    factory = RequestFactory()
    request = factory.get('/purohit/dashboard/')
    request.user = user
    
    # Add messages middleware support
    setattr(request, '_messages', FallbackStorage(request))
    
    try:
        print("Calling purohit_dashboard...")
        response = purohit_dashboard(request)
        print("Response status code:", response.status_code)
    except Exception as e:
        import traceback
        print("CAUGHT EXCEPTION:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_dashboard()
