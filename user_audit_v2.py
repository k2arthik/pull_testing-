import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth.models import User

print("USER AUDIT REPORT")
print("-" * 60)
print(f"{'Username':<25} | {'Is Staff':<10} | {'Is Superuser':<12}")
print("-" * 60)

for user in User.objects.all():
    print(f"{user.username:<25} | {str(user.is_staff):<10} | {str(user.is_superuser):<12}")
print("-" * 60)
