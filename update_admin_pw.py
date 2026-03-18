import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

User = get_user_model()
try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print("User 'admin' password updated successfully.")
except Exception as e:
    print(f"Error updating password: {e}")
