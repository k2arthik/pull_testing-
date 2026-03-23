import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name = 'core_booking';")
    columns = cursor.fetchall()
    with open('db_schema.txt', 'w') as f:
        for col in columns:
            f.write(f"{col[0]} - Nullable: {col[1]}\n")
