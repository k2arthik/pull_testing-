import subprocess
import sys

try:
    result = subprocess.run(
        [sys.executable, 'manage.py', 'test', 'core.tests_dashboard', '-v', '2'],
        capture_output=True,
        text=True,
        encoding='utf-8', # Try utf-8 first
        errors='replace'
    )
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
except Exception as e:
    print(f"Error running subprocess: {e}")
