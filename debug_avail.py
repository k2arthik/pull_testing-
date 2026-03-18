import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.test import Client
from core.models import PriestProfile, PriestAvailability
from django.utils import timezone
from datetime import datetime, timedelta

date_str = '2026-03-24'
now = timezone.localtime(timezone.now())
forty_eight_hours_later = now + timedelta(hours=48)
p = PriestProfile.objects.first()

with open('debug_avail.txt', 'w') as f:
    f.write(f"Priest: {p.fullname}\n")
    avail = PriestAvailability.objects.filter(priest=p, date=date_str).first()
    if avail:
        f.write(f"Afternoon available flag: {avail.afternoon_available}\n")
        f.write(f"Afternoon start: {avail.afternoon_start}\n")
    else:
        f.write("No avail found\n")
        
    c = Client()
    r = c.get(f'/api/availability/service/ganesh-pooja/?date={date_str}')
    f.write(f"API Response: {r.status_code}\n")
    f.write(r.content.decode('utf-8'))
