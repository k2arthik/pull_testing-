import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth.models import User

users = []
for user in User.objects.all():
    users.append({
        'username': user.username,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser
    })

with open('user_report.json', 'w') as f:
    json.dump(users, f, indent=4)

print(f"Successfully wrote {len(users)} users to user_report.json")
