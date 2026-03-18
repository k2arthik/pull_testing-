from django import template

register = template.Library()

@register.filter
def is_purohit(user):
    """Check if the user has a priest profile."""
    return user.is_authenticated and hasattr(user, 'priest_profile')

@register.filter
def is_devotee(user):
    """Check if the user has a devotee profile."""
    return user.is_authenticated and hasattr(user, 'devotee_profile')

@register.filter
def is_on_purohit_mgmt(request):
    """Check if the current request is for a purohit management page."""
    mgmt_urls = ['purohit_dashboard', 'priest_availability', 'priest_bookings', 'purohit_edit_profile']
    return request.resolver_match and request.resolver_match.url_name in mgmt_urls

@register.filter
def is_on_devotee_mgmt(request):
    """Check if the current request is for a devotee management page."""
    mgmt_urls = ['devotee_dashboard', 'my_bookings']
    return request.resolver_match and request.resolver_match.url_name in mgmt_urls

@register.filter
def get_service_name(slug):
    """Map service slug to title."""
    from ..models import Puja
    service_title = Puja.objects.filter(slug=slug).values_list('title', flat=True).first()
    if service_title:
        return service_title
    return slug.replace('-', ' ').title()
