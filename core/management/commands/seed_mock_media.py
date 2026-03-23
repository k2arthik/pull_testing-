import os
import shutil
from django.core.management.base import BaseCommand
from core.models import Blog, Photo, Video
from django.conf import settings
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seed the database with mock blogs, photos, and videos, copying real images'

    def handle(self, *args, **options):
        self.stdout.write('Seeding mock media data...')

        # Ensure media directories exist
        media_photos = os.path.join(settings.MEDIA_ROOT, 'photos')
        media_blogs = os.path.join(settings.MEDIA_ROOT, 'blogs')
        os.makedirs(media_photos, exist_ok=True)
        os.makedirs(media_blogs, exist_ok=True)

        def copy_static_to_media(filename, subfolder):
            src = os.path.join(settings.BASE_DIR, 'static', 'images', filename)
            dst_folder = os.path.join(settings.MEDIA_ROOT, subfolder)
            dst = os.path.join(dst_folder, filename)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                return f"{subfolder}/{filename}"
            return None

        # 1. Seed Blogs
        blogs = [
            {
                'title': 'The Significance of Ganesh Chaturthi',
                'category': 'Rituals',
                'excerpt': 'Discover the deep spiritual meaning behind the worship of Lord Ganesha.',
                'content': '<p>Lord Ganesha... marks the birth of the Lord, and it is a time for communal prayer.</p>',
                'image_name': 'blogtemple.png'
            },
            {
                'title': 'Daily Vedic Rituals for a Peaceful Home',
                'category': 'Lifestyle',
                'excerpt': 'A guide to simple yet powerful Vedic practices you can perform every day.',
                'content': '<p>In the Vedic tradition, our home is a sacred space...</p>',
                'image_name': 'blog2.png'
            }
        ]
        for blog_data in blogs:
            img_path = copy_static_to_media(blog_data.pop('image_name'), 'blogs')
            blog, created = Blog.objects.get_or_create(
                title=blog_data['title'],
                defaults={**blog_data, 'image': img_path}
            )
            if created:
                self.stdout.write(f"Created Blog: {blog.title}")

        # 2. Seed Photos (Gallery)
        photos = [
            {'title': 'Maha Shivaratri Celebration', 'image_name': 'gallery1.jpeg'},
            {'title': 'Traditional Homa Ceremony', 'image_name': 'gallery2.jpeg'},
            {'title': 'Altar Decoration', 'image_name': 'gallery3.jpeg'},
            {'title': 'Vedic Temple Architecture', 'image_name': 'gallery4.jpeg'},
            {'title': 'Sacred Ritual Ingredients', 'image_name': 'temple1.jpeg'},
            {'title': 'Pandit Chanting Mantras', 'image_name': 'temple2.jpeg'}
        ]
        for photo_data in photos:
            img_path = copy_static_to_media(photo_data.pop('image_name'), 'photos')
            photo, created = Photo.objects.get_or_create(
                title=photo_data['title'],
                defaults={'image': img_path}
            )
            if created:
                self.stdout.write(f"Created Photo: {photo.title}")

        # 3. Seed Videos (Using more reliable YouTube embed for Rickroll or generic Vedic)
        # Error 153 often happens due to domain restrictions or malformed embed code.
        # We will use a more robust embed URL.
        videos = [
            {
                'title': 'Introduction to Karya Siddhi Services',
                'youtube_iframe': '<iframe width="100%" height="100%" src="https://www.youtube.com/embed/dQw4w9WgXcQ?rel=0&modestbranding=1" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
            },
            {
                'title': 'A Glimpse into Vedic Vivah',
                'youtube_iframe': '<iframe width="100%" height="100%" src="https://www.youtube.com/embed/fD363S5I608?rel=0" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
            }
        ]
        for video_data in videos:
            # Update existing or create
            video, created = Video.objects.update_or_create(
                title=video_data['title'],
                defaults=video_data
            )
            if created:
                self.stdout.write(f"Created Video: {video.title}")
            else:
                self.stdout.write(f"Updated Video: {video.title}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded mock data and copied images.'))
