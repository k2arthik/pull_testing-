from datetime import datetime

from django.db import models
from django.utils import timezone

from core.models import Booking


def complete_due_bookings(queryset=None):
    """
    Mark bookings as completed when their end time has passed.
    Uses local time (TIME_ZONE) for comparison.
    """
    now = timezone.localtime()
    today = now.date()
    now_time = now.time()

    base_qs = queryset if queryset is not None else Booking.objects.all()
    due_qs = base_qs.filter(
        status__in=['confirmed', 'in_progress']
    ).filter(
        models.Q(booking_date__lt=today) |
        models.Q(booking_date=today, end_time__lte=now_time)
    )
    return due_qs.update(status='completed', puja_completed_at=now)
