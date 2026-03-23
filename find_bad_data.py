import sqlite3
import os

db_path = 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def check_nulls(table, col):
    print(f"Checking {table}.{col} for NULLs or weird types...")
    cursor.execute(f"SELECT id, {col} FROM {table}")
    for row in cursor.fetchall():
        if row[1] is None:
            print(f"!!! NULL found in {table} ID {row[0]}")
        elif not isinstance(row[1], str):
            print(f"!!! Non-string found in {table} ID {row[0]}: {type(row[1])} {row[1]}")

check_nulls("core_priestavailability", "date")
check_nulls("core_booking", "booking_date")
conn.close()
