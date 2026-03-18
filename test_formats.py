import sqlite3
import datetime

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

def test_isoformat(table, col):
    print(f"Testing {table}.{col} for fromisoformat compatibility...")
    cursor.execute(f"SELECT id, {col} FROM {table}")
    for row in cursor.fetchall():
        id, val = row
        if val is None:
            print(f"ID {id}: Skipping None")
            continue
        try:
            # Django's parse_datetime internally calls fromisoformat in some versions
            # Or its own logic. But the error said "fromisoformat: argument must be str"
            # which happens if val is NOT a string.
            if not isinstance(val, str):
                print(f"!!! PROBLEM !!! ID {id}: Value is {type(val)}: {val}")
            else:
                # If it's a string, try to parse it
                try:
                    datetime.datetime.fromisoformat(val)
                except ValueError:
                    # Might not be a full datetime string, could be a date string
                    try:
                        datetime.date.fromisoformat(val[:10])
                    except:
                        print(f"!!! FORMAT ERROR !!! ID {id}: '{val}'")
        except Exception as e:
            print(f"!!! CRASH !!! ID {id}: {e}")

test_isoformat("core_priestavailability", "date")
test_isoformat("core_booking", "booking_date")
conn.close()
