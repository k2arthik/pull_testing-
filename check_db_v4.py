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
    print(f"Checking {table_name}...")
    cursor.execute(f"SELECT id, {date_column} FROM {table_name}")
    rows = cursor.fetchall()
    found_problem = False
    for row in rows:
        val = row[1]
        # In SQLite, DateTimeField is stored as a string. 
        # Django's parse_datetime fails if it gets something else (though SQLite mostly stores as str)
        # OR if it's empty/None or invalid format.
        try:
            from django.utils.dateparse import parse_datetime, parse_date
            if "availability" in table_name:
                if val: parse_datetime(val)
            else:
                if val: parse_date(val)
        except Exception as e:
            print(f"ERROR on ID {row[0]}: val='{val}' error={e}")
            found_problem = True
    
    if not found_problem:
        print(f"All records in {table_name} OK.")

check_table("core_priestavailability", "date")
check_table("core_booking", "booking_date")
conn.close()
