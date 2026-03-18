import sqlite3
import os

db_path = 'db.sqlite3'
if not os.path.exists(db_path):
    print("DB not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Raw data from core_priestavailability 'date' column:")
cursor.execute("SELECT id, date FROM core_priestavailability")
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row[0]}, Value: {row[1]}, Type: {type(row[1])}")

print("\nRaw data from core_booking 'booking_date' column:")
cursor.execute("SELECT id, booking_date FROM core_booking")
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row[0]}, Value: {row[1]}, Type: {type(row[1])}")

conn.close()
