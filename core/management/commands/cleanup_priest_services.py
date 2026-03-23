"""
Management command to clean up priest service data.
Converts service titles to proper slugs.
"""
from django.core.management.base import BaseCommand
from core.models import PriestProfile, Puja


class Command(BaseCommand):
    help = 'Clean up priest service data - convert titles to slugs'

    def handle(self, *args, **options):
        # Create a reverse mapping: title -> slug from DB
        title_to_slug = {}
        for puja in Puja.objects.all():
            title_to_slug[puja.title.lower()] = puja.slug
            title_to_slug[puja.title.lower().strip()] = puja.slug
        
        # Add manual mappings for common variations
        title_to_slug['ganapathi homam'] = 'ganesh-homa'
        title_to_slug['ganesh homam'] = 'ganesh-homa'
        
        priests = PriestProfile.objects.all()
        updated_count = 0
        
        for priest in priests:
            if not priest.services:
                continue
                
            cleaned_services = []
            needs_update = False
            
            for service in priest.services:
                service_clean = service.strip()
                
                # Check if it's already a valid slug
                if Puja.objects.filter(slug=service_clean).exists():
                    cleaned_services.append(service_clean)
                else:
                    # Try to find the slug from the title
                    service_lower = service_clean.lower()
                    if service_lower in title_to_slug:
                        cleaned_services.append(title_to_slug[service_lower])
                        needs_update = True
                        self.stdout.write(
                            self.style.WARNING(
                                f'Converting "{service_clean}" -> "{title_to_slug[service_lower]}" for {priest.fullname}'
                            )
                        )
                    else:
                        # Keep as is if we can't find a match
                        cleaned_services.append(service_clean)
                        self.stdout.write(
                            self.style.ERROR(
                                f'Could not find slug for "{service_clean}" for {priest.fullname}'
                            )
                        )
            
            if needs_update:
                priest.services = cleaned_services
                priest.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {priest.fullname}: {cleaned_services}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned {updated_count} priest profiles'
            )
        )
