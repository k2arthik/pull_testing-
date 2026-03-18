from django.core.management.base import BaseCommand

from core.models import Puja, PujaCategory, EnquiryCategory
from core.services_data import services as services_data


CATEGORY_DEFS = [
    {
        "name": "Prosperity & Wealth",
        "slug": "prosperity-wealth",
        "description": "Divine blessings for abundance and prosperity",
        "display_order": 1,
    },
    {
        "name": "Health & Healing",
        "slug": "health-healing",
        "description": "Sacred rituals for health, vitality and longevity",
        "display_order": 2,
    },
    {
        "name": "Protection & Power",
        "slug": "protection-power",
        "description": "Divine shield against negativity and evil",
        "display_order": 3,
    },
    {
        "name": "Peace & Harmony",
        "slug": "peace-harmony",
        "description": "Pujas for inner peace, calm, and harmony",
        "display_order": 4,
    },
    {
        "name": "Wisdom & Family Blessings",
        "slug": "wisdom-family",
        "description": "Knowledge, progeny and family harmony",
        "display_order": 5,
    },
    {
        "name": "Marriages",
        "slug": "marriages",
        "description": "Sacred ceremonies for auspicious unions",
        "display_order": 6,
    },
    {
        "name": "Other Sacred Services",
        "slug": "other-services",
        "description": "More divine rituals for every occasion & life milestone",
        "display_order": 7,
    },
]

ENQUIRY_CATEGORY_DEFS = [
    {"name": "Refund", "slug": "refund", "display_order": 1},
    {"name": "Pooja Service", "slug": "pooja-service", "display_order": 2},
    {"name": "Payment Issue", "slug": "payment-issue", "display_order": 3},
    {"name": "Reschedule", "slug": "reschedule", "display_order": 4},
    {"name": "Other", "slug": "other", "display_order": 5},
]

FEATURED_SLUGS = [
    "pradosha-kala-abhishekam",
    "ganesh-homa",
    "navagraha-shanti-pooja",
    "satyanarayan-pooja",
    "maha-lakshmi-pooja",
    "rudrabhishekam-pooja",
    "chandi-homa",
    "sudarshana-homa",
]

CATEGORY_RULES = [
    ("prosperity-wealth", ["lakshmi", "dhan", "wealth", "prosperity", "satyanarayan", "rushi", "varalakshmi"]),
    ("health-healing", ["mrityunjaya", "dhanvantari", "ayush", "health", "healing", "ayur"]),
    ("protection-power", ["sudarshana", "chandi", "durga", "raksha", "narasimha", "narsimha", "kali", "bhairava"]),
    ("peace-harmony", ["shanti", "shanthi", "rudra", "rudrabhishekam", "navagraha"]),
    ("wisdom-family", ["saraswati", "vidya", "gopala", "santana", "family", "children", "education"]),
    ("marriages", ["kalyanam", "marriage", "vivah", "seemantham", "shashti", "bheema", "upanayanam"]),
]


def _pick_category(slug, title):
    haystack = f"{slug} {title}".lower()
    for cat_slug, keywords in CATEGORY_RULES:
        if any(k in haystack for k in keywords):
            return cat_slug
    return "other-services"


class Command(BaseCommand):
    help = "Seed reference data: Puja categories, services, and enquiry categories."

    def handle(self, *args, **options):
        # Categories
        categories = {}
        for c in CATEGORY_DEFS:
            obj, _ = PujaCategory.objects.update_or_create(
                slug=c["slug"],
                defaults={
                    "name": c["name"],
                    "description": c["description"],
                    "display_order": c["display_order"],
                    "is_active": True,
                },
            )
            categories[c["slug"]] = obj

        # Enquiry categories
        for c in ENQUIRY_CATEGORY_DEFS:
            EnquiryCategory.objects.update_or_create(
                slug=c["slug"],
                defaults={
                    "name": c["name"],
                    "description": "",
                    "display_order": c["display_order"],
                    "is_active": True,
                },
            )

        # Services
        created = 0
        updated = 0
        for idx, (slug, data) in enumerate(services_data.items(), start=1):
            title = data.get("title", slug.replace("-", " ").title())
            category_slug = _pick_category(slug, title)
            category = categories.get(category_slug)

            defaults = {
                "title": title,
                "category": category,
                "short_description": data.get("short_description", ""),
                "full_description": data.get("full_description", ""),
                "page_description": data.get("short_description", ""),
                "benefits": [],
                "image": data.get("image", ""),
                "gallery": data.get("gallery", []),
                "duration": data.get("duration", ""),
                "price": data.get("price", ""),
                "pandits": data.get("pandits", ""),
                "location": data.get("location", ""),
                "deity": data.get("deity", ""),
                "required_purohits": data.get("required_purohits", 1),
                "is_featured": slug in FEATURED_SLUGS,
                "display_order": idx,
                "is_active": True,
            }

            obj, was_created = Puja.objects.update_or_create(slug=slug, defaults=defaults)
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Services created: {created}, updated: {updated}."))
