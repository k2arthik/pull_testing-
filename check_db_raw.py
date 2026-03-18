import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings

db_path = settings.DATABASES['default']['NAME']
print(f"Database path: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\nRaw data from core_priestavailability table:")
try:
    cursor.execute("SELECT id, date FROM core_priestavailability")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Date Value: {row[1]}, Type: {type(row[1])}")
except Exception as e:
    print(f"Error reading core_priestavailability: {e}")

print("\nRaw data from core_booking table:")
try:
    cursor.execute("SELECT id, booking_date FROM core_booking")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Date Value: {row[1]}, Type: {type(row[1])}")
except Exception as e:
    print(f"Error reading core_booking: {e}")

conn.close()
