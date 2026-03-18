import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth.models import User

print("Listing all users and their privileges:")
print(f"{'Username':<15} | {'Is Staff':<10} | {'Is Superuser':<12}")
print("-" * 45)

for user in User.objects.all():
    print(f"{user.username:<15} | {str(user.is_staff):<10} | {str(user.is_superuser):<12}")
