import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.get(username='chinnaprashanth3033_1')
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"Successfully promoted {user.username} to superuser.")
except User.DoesNotExist:
    print("User chinnaprashanth3033_1 does not exist.")
except Exception as e:
    print(f"Error: {e}")
