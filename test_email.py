import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

def test_email():
    print("Attempting to send a test email...")
    try:
        subject = 'Karya Siddhi - Email Test'
        message = 'This is a test email from the Karya Siddhi system to verify SMTP settings.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.DEFAULT_FROM_EMAIL]
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        print("Test email sent SUCCESSFULLY!")
    except Exception as e:
        print(f"FAILED to send test email: {e}")

if __name__ == "__main__":
    test_email()
