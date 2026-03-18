import os
import django
import sys
from django.test.utils import get_runner
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
django.setup()

def run_tests():
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)
    failures = test_runner.run_tests(['core.tests_dashboard'])
    return failures

if __name__ == "__main__":
    failures = run_tests()
    if failures:
        sys.exit(1)
    else:
        sys.exit(0)
