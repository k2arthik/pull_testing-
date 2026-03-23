from django.shortcuts import render, get_object_or_404
from .services_data import services as services_data

def home(request):
    """Render the home page."""
    return render(request, 'pages/home.html')

def about(request):
    """Render the about page."""
    return render(request, 'pages/about.html')

def services(request):
    """Render the services page."""
    return render(request, 'pages/services.html')

def service_detail(request, service_slug):
    """Render the detailed page for a specific service."""
    service = services_data.get(service_slug)
    if not service:
        # In a real app, you might raise 404. Here we render a custom 404 or redirect.
        # For simplicity, let's just render the home page or a 404 page if it exists.
        # But properly raising 404 is better django practice.
        from django.http import Http404
        raise Http404("Service not found")
        
    context = {
        'service': service
    }
    return render(request, 'pages/service_detail.html', context)

def temples(request):
    """Render the temples page."""
    return render(request, 'pages/temples.html')

def contact(request):
    """Render the contact page."""
    return render(request, 'pages/contact.html')

def login_view(request):
    """Render the login page."""
    return render(request, 'pages/login.html')

def signup_view(request):
    """Render the signup page."""
    return render(request, 'pages/signup.html')

def blogs(request):
    """Render the blogs page."""
    return render(request, 'pages/blogs.html')
