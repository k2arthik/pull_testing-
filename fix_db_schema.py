import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("ALTER TABLE core_booking ALTER COLUMN payment_method DROP NOT NULL;")
    cursor.execute("ALTER TABLE core_booking ALTER COLUMN refund_percentage DROP NOT NULL;")
    print("Successfully dropped NOT NULL constraints.")
