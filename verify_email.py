import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_email():
    print("Testing Email Configuration...")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"Port: {settings.EMAIL_PORT}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    print(f"Backend: {settings.EMAIL_BACKEND}")
    
    try:
        # Use a real recipient if possible, or just test the connection
        # For testing, we'll try to send to the host user itself
        sent = send_mail(
            'Karya Siddhi - Test Email',
            'This is a test email to verify SMTP configuration.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )
        print(f"SUCCESS: Email sent (result: {sent})")
    except Exception as e:
        print(f"ERROR: Email sending failed: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_email()
