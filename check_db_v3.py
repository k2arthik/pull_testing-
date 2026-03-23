import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings

db_path = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def check_table(table_name, date_column):
    print(f"\nChecking table {table_name}...")
    cursor.execute(f"SELECT id, {date_column} FROM {table_name}")
    rows = cursor.fetchall()
    for row in rows:
        val = row[1]
        if val is None or not isinstance(val, (str, bytes)):
             print(f"!!! PROBLEM !!! ID: {row[0]}, Value: {val}, Type: {type(val)}")
        else:
             print(f"OK - ID: {row[0]}, Value: {val}")

try:
    check_table("core_priestavailability", "date")
    check_table("core_booking", "booking_date")
except Exception as e:
    print(f"Error: {e}")

conn.close()
