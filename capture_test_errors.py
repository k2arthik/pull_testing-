import os
import django
import sys
import unittest
from django.conf import settings
from django.test.utils import get_runner
from io import StringIO

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
django.setup()

def run_tests_to_file():
    TestRunner = get_runner(settings)
    
    # Use StringIO to capture output
    out = StringIO()
    test_runner = TestRunner(verbosity=2, stream=out, interactive=False)
    
    failures = test_runner.run_tests(['core.tests_dashboard'])
    
    with open('test_results_detailed.txt', 'w', encoding='utf-8') as f:
        f.write(out.getvalue())
    
    return failures

if __name__ == "__main__":
    failures = run_tests_to_file()
    print(f"Tests finished with {failures} failures/errors.")
