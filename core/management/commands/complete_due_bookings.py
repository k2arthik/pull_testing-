from django.core.management.base import BaseCommand

from core.utils.booking_status import complete_due_bookings


class Command(BaseCommand):
    help = "Mark confirmed/in-progress bookings as completed once their end time has passed."

    def handle(self, *args, **options):
        updated = complete_due_bookings()
        self.stdout.write(self.style.SUCCESS(f"Completed bookings updated: {updated}"))
