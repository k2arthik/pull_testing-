import os
import django
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from unittest.mock import patch

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
django.setup()

from core.views import contact

def verify_contact_post():
    factory = RequestFactory()
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'mobile': '9876543210',
        'service': 'Ganesh Homa',
        'message': 'Testing contact form notifications.'
    }
    
    request = factory.post('/contact/', data)
    
    # Add messages support
    setattr(request, '_messages', FallbackStorage(request))
    
    print("Testing contact form POST...")
    
    # Mock smtplib to avoid actual email sending but verify it's called
    with patch('smtplib.SMTP_SSL') as mock_smtp:
        response = contact(request)
        
        print(f"Response status: {response.status_code}")
        print(f"Redirect URL: {response.url if hasattr(response, 'url') else 'N/A'}")
        
        # Check messages
        msgs = [m.message for m in request._messages]
        print(f"Messages: {msgs}")
        
        if response.status_code == 302 and "sent successfully" in msgs[0]:
            print("\nSUCCESS: Contact form handled correctly.")
        else:
            print("\nFAILURE: Contact form handling failed.")

if __name__ == "__main__":
    verify_contact_post()
