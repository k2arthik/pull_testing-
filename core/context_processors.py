from .models import SEOMetadata

def seo_metadata(request):
    """
    Fetch SEO metadata for the current path and inject into context.
    Default values are provided if no metadata is found in DB.
    """
    path = request.path
    try:
        seo = SEOMetadata.objects.get(path=path)
        return {
            'seo_title': seo.title_tag,
            'seo_description': seo.meta_description,
            'seo_keywords': seo.keywords,
            'seo_og_image': seo.og_image.url if seo.og_image else None,
        }
    except SEOMetadata.DoesNotExist:
        # Provide sensible defaults
        return {
            'seo_title': 'Karya Siddhi - Authentic Vedic Services',
            'seo_description': 'Experience traditional Vedic rituals with utmost devotion and authenticity.',
            'seo_keywords': 'Vedic, Puja, Rituals, Spiritual, Hyderabad',
            'seo_og_image': None,
        }
