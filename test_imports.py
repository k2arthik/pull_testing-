import os
import sys

print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

try:
    import core
    print("Imported core")
except ImportError as e:
    print(f"Failed to import core: {e}")

try:
    import myproject.settings
    print("Imported myproject.settings")
except ImportError as e:
    print(f"Failed to import myproject.settings: {e}")
