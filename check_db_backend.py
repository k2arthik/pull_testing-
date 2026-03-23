import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

print(f"Active Database Backend: {connection.vendor}")
print(f"Database Engine: {django.conf.settings.DATABASES['default']['ENGINE']}")
