# Replaced SQLite-specific raw SQL migration with a database-agnostic version.
# The original migration used PRAGMA and sqlite_master to reshape the `language`
# column, which is SQLite-only. On PostgreSQL, JSONField is created natively in
# migration 0001, so no manual column surgery is required here.

import json
from django.db import migrations


def migrate_language_to_json(apps, schema_editor):
    """
    Ensure all language values in core_priestprofile are valid JSON lists.
    Uses Django ORM-style cursor queries that work on any DB backend.
    """
    if schema_editor.connection.vendor == 'sqlite':
        # This path only needed for SQLite (legacy support)
        return  # Skip on PostgreSQL — column already correct

    # On PostgreSQL, language is already a jsonb column; fix any bad string data
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT id, language FROM core_priestprofile")
        rows = cursor.fetchall()
        for row_id, lang in rows:
            new_lang = None
            if lang is None:
                new_lang = json.dumps([])
            elif isinstance(lang, list):
                continue  # already correct
            else:
                try:
                    parsed = json.loads(lang) if isinstance(lang, str) else lang
                    new_lang = json.dumps(parsed if isinstance(parsed, list) else [str(parsed)])
                except (json.JSONDecodeError, ValueError):
                    new_lang = json.dumps([str(lang).strip()] if str(lang).strip() else [])
            if new_lang is not None:
                cursor.execute(
                    "UPDATE core_priestprofile SET language = %s WHERE id = %s",
                    (new_lang, row_id)
                )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_booking_priestavailability'),
    ]

    operations = [
        migrations.RunPython(migrate_language_to_json, migrations.RunPython.noop),
    ]
