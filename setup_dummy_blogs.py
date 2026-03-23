import os
import django
import sys

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from core.models import Blog
from django.utils import timezone

def create_dummy_blogs():
    print("Creating dummy blogs...")
    
    blogs_data = [
        {
            "title": "The Essence of Vedic Chanting",
            "category": "Tradition",
            "excerpt": "Discover the profound vibrations and historical significance of Vedic mantras.",
            "content": "<h2>The Power of Sound</h2><p>Vedic chanting is one of the oldest oral traditions in the world...</p>"
        },
        {
            "title": "Understanding Ganesha Chaturthi",
            "category": "Rituals",
            "excerpt": "A deep dive into the symbols and spiritual meanings behind the celebration.",
            "content": "<h2>The Lord of Beginnings</h2><p>Ganesha Chaturthi is celebrated with great fervor...</p>"
        },
        {
            "title": "The Science of Homam",
            "category": "Science",
            "excerpt": "Exploring the environmental and psychological benefits of ritual fire ceremonies.",
            "content": "<h2>Fire as a Purifier</h2><p>Homam or Havan is a sacred ritual involving fire...</p>"
        },
        {
            "title": "Living a Spiritual Life",
            "category": "Lifestyle",
            "excerpt": "Practical tips for integrating spiritual practices into your daily routine.",
            "content": "<h2>Small Steps to Peace</h2><p>Mindfulness and meditation can be practiced by anyone...</p>"
        }
    ]

    for data in blogs_data:
        blog, created = Blog.objects.get_or_create(
            title=data["title"],
            defaults={
                "category": data["category"],
                "excerpt": data["excerpt"],
                "content": data["content"],
                "date": timezone.now().date(),
                # Assuming some default image for testing, or it will be empty
            }
        )
        if created:
            print(f"Created blog: {blog.title}")
        else:
            print(f"Blog already exists: {blog.title}")

if __name__ == "__main__":
    create_dummy_blogs()
