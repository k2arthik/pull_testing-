from django.core.management.base import BaseCommand
from core.models import PujaCategory, Puja, EnquiryCategory
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds initial Puja Categories, Puja Services, and Enquiry Categories'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Seed Enquiry Categories
        enquiry_categories = ["Refund", "Pooja Service", "Payment", "Other"]
        for cat_name in enquiry_categories:
            EnquiryCategory.objects.get_or_create(
                name=cat_name,
                defaults={'slug': slugify(cat_name), 'is_active': True}
            )
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(enquiry_categories)} enquiry categories."))

        # 2. Seed Puja Categories
        categories_data = [
            {"name": "Prosperity", "description": "Rituals for wealth and success."},
            {"name": "Health & Wellness", "description": "Prayers for physical and mental well-being."},
            {"name": "Peace & Harmony", "description": "Pooja for domestic peace and tranquility."},
            {"name": "Protection", "description": "Shielding from negative influences and obstacles."},
            {"name": "Wisdom & Education", "description": "Blessings for knowledge and academic success."},
            {"name": "Marriages & Relationships", "description": "Rituals for marital bliss and harmony."},
            {"name": "Others", "description": "General poojas and other unique services."},
        ]

        for cat_data in categories_data:
            cat, created = PujaCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    'slug': slugify(cat_data["name"]),
                    'description': cat_data["description"],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created category: {cat.name}')

        # 3. Seed initial Puja Services (example set)
        # Note: In a real scenario, this would be more comprehensive.
        # This populates from the metadata I saw in the services template.
        pujas_to_seed = [
            {
                "title": "Ganesh Pooja",
                "category_name": "Prosperity",
                "short_description": "For removal of obstacles.",
                "duration": "1-2 Hours",
                "price": "5001",
                "is_featured": True
            },
            {
                "title": "Maha Lakshmi Pooja",
                "category_name": "Prosperity",
                "short_description": "For wealth and abundance.",
                "duration": "2-3 Hours",
                "price": "7501",
                "is_featured": True
            },
            {
                "title": "Mrityunjaya Homa",
                "category_name": "Health & Wellness",
                "short_description": "For longevity and health.",
                "duration": "3-4 Hours",
                "price": "11001",
                "is_featured": True
            },
            {
                "title": "Satyanarayana Swamy Vratam",
                "category_name": "Peace & Harmony",
                "short_description": "For overall prosperity and peace.",
                "duration": "3 Hours",
                "price": "6501",
                "is_featured": True
            },
        ]

        for p_data in pujas_to_seed:
            cat = PujaCategory.objects.get(name=p_data["category_name"])
            Puja.objects.get_or_create(
                slug=slugify(p_data["title"]),
                defaults={
                    "title": p_data["title"],
                    "category": cat,
                    "short_description": p_data["short_description"],
                    "duration": p_data["duration"],
                    "price": p_data["price"],
                    "is_featured": p_data["is_featured"],
                    "is_active": True
                }
            )

        self.stdout.write(self.style.SUCCESS("Database seeding completed."))
