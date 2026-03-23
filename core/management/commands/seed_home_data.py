from django.core.management.base import BaseCommand
from core.models import HomeHeroConfig, SpiritualJourneyStep, SankalpPillar, Testimonial, HomeAboutConfig
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seed the database with existing hardcoded home page content'

    def handle(self, *args, **options):
        self.stdout.write('Seeding home page data...')

        # 1. Home Hero Config
        hero, created = HomeHeroConfig.objects.get_or_create(
            id=1,
            defaults={
                'title_gold': 'BRINGING SACRED',
                'title_ivory': 'RITUALS TO YOUR HOME',
                'subtitle': 'Experience the sanctity of Authentic Vedic Rituals performed by verified Pandits. Bring the temple\'s spiritual vibration to your home.',
                'quote_text': 'Dharmo Rakshati Rakshitah',
                'watermark_text': 'ॐ नमः शिवाय',
            }
        )
        if not created:
            self.stdout.write('Hero config already exists.')

        # 2. Spiritual Journey Steps
        journey_steps = [
            {
                'step_number': '01',
                'title': 'Choose Seva',
                'description': 'Select your desired Puja or Homam from our list of Vedic rituals.',
                'icon_class': 'fas fa-hand-holding-heart',
                'display_order': 1
            },
            {
                'step_number': '02',
                'title': 'Book Slot',
                'description': 'Pick an auspicious date & time. Our astrologers can guide you.',
                'icon_class': 'fas fa-calendar-alt',
                'display_order': 2
            },
            {
                'step_number': '03',
                'title': 'Divine Ritual',
                'description': 'Qualified Pandits perform the Puja with strict Vedic vidhi.',
                'icon_class': 'fas fa-fire-alt',
                'display_order': 3
            },
            {
                'step_number': '04',
                'title': 'Receive Blessings',
                'description': 'Receive blessings & video of the ritual at your doorstep.',
                'icon_class': 'fas fa-hands-praying',
                'display_order': 4
            }
        ]
        for step_data in journey_steps:
            SpiritualJourneyStep.objects.get_or_create(
                step_number=step_data['step_number'],
                defaults=step_data
            )

        # 3. Sankalp Pillars
        pillars = [
            {
                'title': 'Siddha Purohit',
                'subtitle': 'Verified Acharyas',
                'description': 'Services performed only by Gurukul-trained Brahmins with extensive experience in Karma Kanda.',
                'display_order': 1
            },
            {
                'title': 'Vedic Vidhi',
                'subtitle': 'Authentic Rituals',
                'description': 'Our rituals strictly follow the Rig Vedic & Yajur Vedic scriptures. Mantras are chanted with perfect pronunciation.',
                'display_order': 2
            },
            {
                'title': 'Shuddha Samagri',
                'subtitle': 'Pure Ingredients',
                'description': 'We use only Grade-A ghee, fresh flowers, and organic offerings. No compromise on the sanctity of the Havan.',
                'display_order': 3
            }
        ]
        for pillar_data in pillars:
            SankalpPillar.objects.get_or_create(
                title=pillar_data['title'],
                defaults=pillar_data
            )

        # 4. Testimonials
        testimonials = [
            {
                'name': 'Rajesh Kumar',
                'location': 'Hyderabad, India',
                'text': 'I was blown away by the Pradosha Kala Abhishekam. Even through a screen, the devotion was so clear that I could actually feel the vibrations! The Sankalp process felt incredibly authentic, too.',
                'display_order': 1
            },
            {
                'name': 'Priya Reddy',
                'location': 'California, USA',
                'text': 'Finding authentic rituals abroad can be tough, but this service made it so easy. The Ganesh Homa was perfect, and I was so impressed by how beautifully the prasadam was packaged. Such a great experience!',
                'display_order': 2
            },
            {
                'name': 'Amit Sharma',
                'location': 'New Delhi, India',
                'text': 'We loved the Satyanarayan Puja video! It was so authentic and heartwarming—my grandma was deeply moved by it. Honestly, every Hindu family should give this a watch.',
                'display_order': 3
            }
        ]
        for test_data in testimonials:
            Testimonial.objects.get_or_create(
                name=test_data['name'],
                defaults=test_data
            )

        # 5. Home About Config
        about, created = HomeAboutConfig.objects.get_or_create(
            id=1,
            defaults={
                'title': 'Authentic & Divine',
                'subtitle': 'We bring traditional Vedic rituals to your doorstep with utmost devotion and authenticity.',
                'badge_text': 'Why Choose Us',
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded home page data.'))
