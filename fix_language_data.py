"""
Fix existing language data in the database so migration 0003 can proceed.
Converts plain strings like 'Telugu' to valid JSON arrays like '["Telugu"]'.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='core_priestprofile'")
if not cursor.fetchone():
    print("Table core_priestprofile not found.")
    conn.close()
    exit()

# Fetch all rows with their current language value
cursor.execute("SELECT id, language FROM core_priestprofile")
rows = cursor.fetchall()

fixed = 0
for row_id, lang in rows:
    new_lang = None
    if lang is None:
        new_lang = '[]'
    else:
        # Check if already valid JSON
        try:
            parsed = json.loads(lang)
            if isinstance(parsed, list):
                # Already a JSON array - make sure it's stored cleanly
                new_lang = json.dumps(parsed)
            else:
                new_lang = json.dumps([str(parsed)])
        except (json.JSONDecodeError, ValueError):
            # Plain string like 'Telugu'
            if lang.strip():
                new_lang = json.dumps([lang.strip()])
            else:
                new_lang = '[]'

    if new_lang is not None and new_lang != lang:
        cursor.execute("UPDATE core_priestprofile SET language = ? WHERE id = ?", (new_lang, row_id))
        print(f"  Row {row_id}: '{lang}' -> '{new_lang}'")
        fixed += 1

conn.commit()
conn.close()
print(f"\nDone. Fixed {fixed} rows.")
print("Now run: python manage.py migrate")
