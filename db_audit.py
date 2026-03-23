import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.apps import apps

print(f"Active Backend: {connection.vendor}")
print("-" * 30)

# Dynamically find models that might be relevant
print("Checking record counts for key models:")
for model in apps.get_models():
    model_name = f"{model._meta.app_label}.{model._meta.object_name}"
    # Target specific areas: auth, silk, and our core app models
    if model._meta.app_label in ['auth', 'core', 'silk', 'payments']:
        try:
            count = model.objects.count()
            print(f"{model_name}: {count} records")
        except Exception as e:
            print(f"Error checking {model_name}: {e}")
