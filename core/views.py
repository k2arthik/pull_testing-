from django.shortcuts import render, get_object_or_404, redirect
from django.db import models
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import (
    PriestProfile, DevoteeProfile, PriestAvailability, Booking, NewsletterSubscriber,
    Photo, Video, Blog, BookingAdditionalPriest, BookingFeedback, BookingEnquiry,
    Puja, PujaCategory, EnquiryCategory,
    HomeHeroConfig, SpiritualJourneyStep, SankalpPillar, Testimonial, HomeAboutConfig
)
from .utils.booking_status import complete_due_bookings
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from payments.services.refund_service import calculate_refund_amount, process_refund
import json
from django.core.exceptions import ValidationError
from .forms import (
    PriestRegistrationForm, PriestLoginForm, PriestEditForm, 
    DevoteeRegistrationForm, PurohitResetPasswordForm
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, time, timedelta
from django.db.models import Q, Prefetch
from django.core.mail import send_mail
from django.conf import settings
import random

def log_debug(message):
    """Log debug messages to a file with robust encoding."""
    log_path = r'c:\Users\91703\OneDrive\Desktop\karyasiddhi\debug_log.txt'
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Error writing to log: {str(e)}")

def format_time_display(time_obj):
    """Helper to format time for emails."""
    if not time_obj: return ""
    if isinstance(time_obj, str):
        # Already a string? try to parse if needed or return as is
        return time_obj
    return time_obj.strftime("%I:%M %p")

def get_service_title(service_slug):
    """Helper to get Puja title by slug with a safe fallback."""
    title = Puja.objects.filter(slug=service_slug).values_list('title', flat=True).first()
    return title or service_slug.replace('-', ' ').title()

def get_service_by_slug(service_slug):
    """Helper to fetch active Puja by slug."""
    return get_object_or_404(Puja, slug=service_slug, is_active=True)


def home(request):
    """Render the home page with dynamic configuration."""
    featured_services = Puja.objects.filter(is_active=True, is_featured=True).order_by('display_order', 'title')[:8]
    
    # Home Page Configs
    hero_config = HomeHeroConfig.objects.filter(is_active=True).first()
    journey_steps = SpiritualJourneyStep.objects.all().order_by('display_order', 'step_number')
    pillars = SankalpPillar.objects.all().order_by('display_order', 'title')
    testimonials = Testimonial.objects.filter(is_active=True).order_by('display_order', '-date_added')
    about_config = HomeAboutConfig.objects.first()
    photos = Photo.objects.all().order_by('-created_at')[:6]
    videos = Video.objects.all().order_by('-created_at')[:3]

    return render(request, 'pages/home.html', {
        'featured_services': featured_services,
        'hero': hero_config,
        'journey_steps': journey_steps,
        'pillars': pillars,
        'testimonials': testimonials,
        'about': about_config,
        'photos': photos,
        'videos': videos,
    })

def about(request):
    """Render the about page."""
    return render(request, 'pages/about.html')

def services(request):
    """Render the services page."""
    categories = (
        PujaCategory.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch(
                'pujas',
                queryset=Puja.objects.filter(is_active=True).order_by('display_order', 'title')
            )
        )
        .order_by('display_order', 'name')
    )
    return render(request, 'pages/services.html', {
        'service_categories': categories
    })

def service_detail(request, service_slug):
    """Render the detailed page for a specific service."""
    service = get_service_by_slug(service_slug)
    required_purohits = service.required_purohits

    context = {
        'service': service,
        'service_slug': service_slug,
        'today_date': timezone.localtime(timezone.now()).date().isoformat()
    }
    return render(request, 'pages/service_detail.html', context)

def temples(request):
    """Render the temples page."""
    return render(request, 'pages/temples.html')

def contact(request):
    """Handle contact form submission and render page."""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        service = request.POST.get('service', 'Not Specified')
        message = request.POST.get('message')
        
        log_debug(f"Contact form submitted by {name} ({email})")
        
        # 1. Email to Admin
        admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
        admin_body = (
            f"New Contact Form Submission\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {mobile}\n"
            f"Service: {service}\n"
            f"Message: {message}\n"
        )
        
        try:
            # Notify Admins
            send_mail(
                f'New Inquiry: {name}',
                admin_body,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True
            )
            
            # 2. Confirmation to User
            user_body = (
                f"Namaste {name},\n\n"
                f"Thank you for reaching out to Karya Siddhi Pooja Services.\n\n"
                f"We have received your message regarding '{service}' and our representative will contact you shortly at {mobile} or via this email.\n\n"
                f"Your Message Summary:\n\"{message}\"\n\n"
                f"Regards,\nKarya Siddhi Team"
            )
            send_mail(
                'Thank you for contacting Karya Siddhi',
                user_body,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True
            )
            
            return redirect('contact_success')
        except Exception as e:
            log_debug(f"Error sending contact emails: {e}")
            messages.error(request, "There was an error sending your message. Please try again or call us directly.")
            
    return render(request, 'pages/contact.html')

def contact_success(request):
    """Render the contact success page with auto-redirect logic."""
    return render(request, 'pages/contact_success.html')

def subscribe_newsletter(request):
    """Handle newsletter subscription via AJAX with duplicate checks."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Email is required.'}, status=400)
        
        # Check if already subscribed
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({'status': 'exists', 'message': 'You have already subscribed.'})
        
        log_debug(f"Newsletter subscription request for: {email}")
        
        # 1. Email to Admin
        admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
        admin_body = f"New Newsletter Subscriber\n\nEmail: {email}\n\nThis user wants to receive Dharmic updates."
        
        try:
            # Save to database
            NewsletterSubscriber.objects.create(email=email)
            
            # Notify Admins
            send_mail(
                'New Newsletter Subscriber',
                admin_body,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True
            )
            
            # 2. Confirmation to User
            user_body = (
                f"Namaste,\n\n"
                f"Thank you for joining the Karya Siddhi spiritual community.\n\n"
                f"You are now subscribed to receive our daily panchang updates, ritual guides, and special temple event notifications.\n\n"
                f"Stay blessed,\nKarya Siddhi Team"
            )
            send_mail(
                'Welcome to Karya Siddhi Community',
                user_body,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True
            )
            
            return JsonResponse({'status': 'success', 'message': 'Successfully subscribed.'})
        except Exception as e:
            log_debug(f"Error in newsletter subscription: {e}")
            return JsonResponse({'status': 'error', 'message': 'Internal server error.'}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def login_view(request):
    """Handle Devotee login."""
    log_debug(f"login_view called with method {request.method}")
    next_url = request.GET.get('next') or request.POST.get('next') or ''

    def get_role_based_redirect(user, target_url):
        # 1. Never redirect back to login/logout pages
        forbidden_paths = [reverse('login'), reverse('admin_login'), reverse('purohit_login'), reverse('logout')]
        if target_url in forbidden_paths or not target_url:
            target_url = None

        # 2. Check Role permissions for 'next' target
        if target_url:
            is_admin_path = target_url.startswith('/admin-portal/') or target_url.startswith('/admin-bookings/')
            is_priest_path = target_url.startswith('/purohit/')
            
            if is_admin_path and not user.is_superuser:
                messages.error(request, "Access denied. Admin portal requires administrator privileges.")
                target_url = None
            elif is_priest_path and not hasattr(user, 'priest_profile'):
                messages.error(request, "Access denied. Priest portal requires a Purohit profile.")
                target_url = None

        if target_url:
            return target_url

        # 3. Default Dashboards
        if hasattr(user, 'priest_profile'):
            return reverse('purohit_dashboard')
        if user.is_superuser:
            return reverse('admin_dashboard')
        return reverse('devotee_dashboard')

    if request.user.is_authenticated:
        log_debug(f"User already authenticated: {request.user}")
        return redirect(get_role_based_redirect(request.user, next_url))

    if request.method == 'POST':
        login_id = request.POST.get('login_id') or request.POST.get('mobile') # Compatibility with old templates during transition
        if login_id:
            login_id = login_id.strip()
            
        password = request.POST.get('password')
        log_debug(f"Login attempt for login_id: {login_id}")

        user_obj = None
        if login_id and '@' in login_id:
            # Try to find user by email (case-insensitive)
            user_obj = User.objects.filter(email__iexact=login_id).first()
        else:
            # Try to find Devotee by mobile
            devotee_profile = DevoteeProfile.objects.filter(mobile=login_id).first()
            if devotee_profile:
                user_obj = devotee_profile.user

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                return redirect(get_role_based_redirect(user, next_url))
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "Account with this mobile number or email does not exist.")

    return render(request, 'pages/login.html', {'next': next_url})

def signup_selector_view(request):
    """Render the signup selector page."""
    return render(request, 'pages/signup_selector.html')

def signup_view(request):
    """Handle Devotee registration."""
    log_debug(f"signup_view called with method {request.method}")
    if request.method == 'POST':
        form = DevoteeRegistrationForm(request.POST)
        if form.is_valid():
            log_debug("DevoteeRegistrationForm is valid")
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            fullname = form.cleaned_data['fullname']
            
            # Create User
            username = email.split('@')[0] + "_" + str(User.objects.count())
            user = User.objects.create_user(username=username, email=email, password=password)
            log_debug(f"Created user {username}")
            
            # Create DevoteeProfile
            profile = form.save(commit=False)
            profile.user = user
            profile.save()
            log_debug(f"Saved DevoteeProfile for {fullname}")
            
            # Send Emails
            try:
                log_debug(f"Attempting to send signup welcome emails to {email}...")
                # To User
                send_mail(
                    'Welcome to Karya Siddhi',
                    f'Hello {fullname},\n\nThank you for registering as a Devotee on Karya Siddhi. Your spiritual journey starts here.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                log_debug(f"Devotee welcome email sent to {email}")
                # Notification
                send_mail(
                    'New Devotee Registration',
                    f'A new devotee has registered:\nName: {fullname}\nEmail: {email}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                log_debug("Admin signup notification email sent")
            except Exception as e:
                log_debug(f"Email error during devotee signup: {e}")

            messages.success(request, "Registration successful! Please login with your credentials.")
            log_debug("Redirecting to login")
            return redirect('login')
        else:
            log_debug(f"DevoteeRegistrationForm is INVALID: {form.errors}")
    else:
        form = DevoteeRegistrationForm()
    return render(request, 'pages/signup.html', {'form': form})

def blogs(request):
    """Render the blogs page with pagination."""
    blog_list = Blog.objects.all().order_by('-date', '-created_at')
    paginator = Paginator(blog_list, 6) # 6 blogs per page for the new layout
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pages/blogs.html', {'page_obj': page_obj})

def photos_view(request):
    """Render the photos page with pagination."""
    photo_list = Photo.objects.all().order_by('-created_at')
    paginator = Paginator(photo_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pages/photos.html', {'page_obj': page_obj})

def videos_view(request):
    """Render the videos page with pagination."""
    video_list = Video.objects.all().order_by('-created_at')
    paginator = Paginator(video_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pages/videos.html', {'page_obj': page_obj})

def cart(request):
    """Render the cart/checkout page."""
    if request.user.is_authenticated and hasattr(request.user, 'priest_profile'):
        messages.warning(request, "Purohits cannot access the shopping cart.")
        return redirect('purohit_dashboard')
    return render(request, 'pages/cart.html')

def purohit_login(request):
    """Handle Priest login."""
    next_url = request.GET.get('next') or request.POST.get('next') or ''
    
    if request.user.is_authenticated:
        if hasattr(request.user, 'priest_profile'):
            return redirect('purohit_dashboard')
        else:
            messages.error(request, "You are already logged in as a devotee.")
            return redirect('devotee_dashboard')
            
    if request.method == 'POST':
        form = PriestLoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data['login_id']
            if login_id:
                login_id = login_id.strip()
                
            password = form.cleaned_data['password']
            
            user_obj = None
            if login_id and '@' in login_id:
                # Try as email (case-insensitive)
                user_obj = User.objects.filter(email__iexact=login_id).first()
            else:
                # Try as mobile
                priest_profile = PriestProfile.objects.filter(mobile=login_id).first()
                if priest_profile:
                    user_obj = priest_profile.user

            if user_obj:
                # Use the associated User's username for authentication
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    # Additional check: ensure this user is actually a Purohit
                    if hasattr(user, 'priest_profile'):
                        login(request, user)
                        target = next_url if (next_url and not next_url.startswith('/admin')) else 'purohit_dashboard'
                        return redirect(target)
                    else:
                        messages.error(request, "This account is not registered as a Purohit.")
                else:
                    messages.error(request, "Invalid credentials.")
            else:
                messages.error(request, "Account with this mobile number or email does not exist.")
    else:
        form = PriestLoginForm()
    return render(request, 'pages/purohit_login.html', {'form': form, 'next': next_url})

def purohit_signup(request):
    """Handle Priest registration."""
    log_debug(f"purohit_signup called with method {request.method}")
    if request.method == 'POST':
        form = PriestRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            log_debug("PriestRegistrationForm is valid")
            # Create User
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            fullname = form.cleaned_data.get('fullname') # Correct field name

            username = email.split('@')[0] + "_" + str(User.objects.count()) # Simple unique username
            user = User.objects.create_user(username=username, email=email, password=password)
            log_debug(f"Created user {username}")
            
            # Create PriestProfile
            profile = form.save(commit=False)
            profile.user = user
            
            # Clean whitespaces from services list
            profile.services = [s.strip() for s in request.POST.getlist('services')]
            profile.save()
            log_debug(f"Saved PriestProfile for {fullname}")
            
            # Send Notification Emails
            try:
                log_debug(f"Attempting to send priest registration emails for {email}...")
                # To Priest
                send_mail(
                    'Welcome to Karya Siddhi - Priest Registration',
                    f'Hello {fullname},\n\nYour registration as a Purohit is successful. You can now manage your services and availability from your dashboard.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                log_debug(f"Priest welcome email sent to {email}")
                # To Admin/Notification
                send_mail(
                    'New Priest Registration',
                    f'A new priest has registered:\nName: {fullname}\nEmail: {email}\nMobile: {profile.mobile}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                log_debug("Admin priest registration notification email sent")
            except Exception as e:
                log_debug(f"Email error during priest signup: {e}")

            messages.success(request, "Registration successful! Please login with your credentials.")
            log_debug(f"Redirecting to purohit_login")
            return redirect('purohit_login')
        else:
            log_debug(f"PriestRegistrationForm is INVALID: {form.errors}")
    else:
        form = PriestRegistrationForm()
    services = Puja.objects.filter(is_active=True).order_by('display_order', 'title')
    return render(request, 'pages/purohit_signup.html', {'form': form, 'services': services})
    
def _handle_priest_booking_action(request, profile):
    """
    Shared helper to handle POST actions for booking updates (Accept/Reject/Cancel).
    Used by priest_bookings and purohit_dashboard.
    Returns a redirect response if an action was processed, otherwise None.
    """
    from .models import Booking
    from django.db.models import Q
    from django.utils import timezone
    from datetime import datetime, timedelta
    from django.core.mail import send_mail
    from django.conf import settings
    from django.contrib.auth.models import User
    
    if request.method != 'POST':
        return None

    booking_id = request.POST.get('booking_id')
    action = request.POST.get('action')
    new_status = request.POST.get('status')
    
    if not booking_id:
        return None

    # Determine redirect target based on current URL name
    current_url_name = request.resolver_match.url_name if request.resolver_match else 'priest_bookings'
    redirect_target = current_url_name if current_url_name in ['priest_bookings', 'purohit_dashboard'] else 'priest_bookings'

# Fetch the booking, ensuring it belongs to this priest (as primary or additional)
    # First try as primary priest
    booking = None
    is_additional_priest_action = False
    additional_priest_rel = None

    try:
        booking = Booking.objects.get(Q(pk=booking_id) & Q(priest=profile))
    except Booking.DoesNotExist:
        pass

    if not booking:
        # Try as additional priest via BookingAdditionalPriest
        try:
            additional_priest_rel = BookingAdditionalPriest.objects.get(
                booking_id=booking_id,
                priest=profile
            )
            booking = additional_priest_rel.booking
            is_additional_priest_action = True
        except BookingAdditionalPriest.DoesNotExist:
            messages.error(request, "Booking not found or access denied.")
            return redirect(redirect_target)

    # --- If this priest is an additional priest, handle their individual status ---
    if is_additional_priest_action and additional_priest_rel:
        if action == 'purohit_cancel' or new_status == 'cancelled':
            if additional_priest_rel.status == 'confirmed':
                # 24h guard for confirmed additional priests
                booking_datetime = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
                if booking_datetime < timezone.now() + timedelta(hours=24):
                    messages.error(request, "Cancellations must be made at least 24 hours before the Puja time.")
                    return redirect(redirect_target)

            additional_priest_rel.status = 'cancelled'
            additional_priest_rel.save()
            booking.restore_slot_availability(priest=profile)
            # Notify relevant parties
            try:
                service_title = get_service_title(booking.service)
                admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
                
                # Reassignment URL for Admin
                site_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8001'
                reassign_url = f"{site_url}/admin-bookings/{booking.id}/reassign/?role=extra&relation_id={additional_priest_rel.id}"

                send_mail(
                    f'Additional Priest Removed from Booking #{booking.id}',
                    f"Hello {booking.devotee_name},\n\nPurohit {profile.fullname} has withdrawn from your booking for '{service_title}' on {booking.booking_date}.\n\nOur admin team will follow up if reassignment is needed.\n\nRegards,\nKarya Siddhi Team",
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.devotee.email],
                    fail_silently=True,
                )
                send_mail(
                    f'[Alert] Additional Priest Withdrew from Booking #{booking.id}',
                    f"Purohit {profile.fullname} has withdrawn from Booking #{booking.id} ({service_title}) on {booking.booking_date}.\n"
                    f"Devotee: {booking.devotee_name} ({booking.devotee_phone})\n\n"
                    f"Action Required: Please reassign another additional priest.\n"
                    f"Reassign Link: {reassign_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails,
                    fail_silently=True,
                )
            except Exception as e:
                log_debug(f"Email error on additional priest cancellation: {e}")
            messages.success(request, "You have withdrawn from this booking.")
            return redirect(redirect_target)

        elif new_status == 'confirmed':
            additional_priest_rel.status = 'confirmed'
            additional_priest_rel.save()
            try:
                service_title = get_service_title(booking.service)
                send_mail(
                    f'You confirmed Booking #{booking.id}',
                    f"Hello {profile.fullname},\n\nYou have confirmed your role as additional priest for '{service_title}' on {booking.booking_date}.\n\nDevotee: {booking.devotee_name} ({booking.devotee_phone})\n\nRegards,\nKarya Siddhi Team",
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )
                send_mail(
                    f'Additional Priest Confirmed for Booking #{booking.id}',
                    f"Purohit {profile.fullname} has confirmed their role as additional priest for '{service_title}' on {booking.booking_date}.\nDevotee: {booking.devotee_name}",
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.devotee.email],
                    fail_silently=True,
                )
            except Exception as e:
                log_debug(f"Email error on additional priest confirmation: {e}")
            messages.success(request, "You have confirmed this booking.")
            return redirect(redirect_target)

        messages.error(request, "Unknown action.")
        return redirect(redirect_target)



    # --- Case 1: Purohit explicit cancel action ---
    if action == 'purohit_cancel':
        if booking.status not in ['pending', 'confirmed']:
            messages.error(request, "This booking cannot be cancelled in its current status.")
            return redirect(redirect_target)

        # 24h guard
        booking_datetime = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
        if booking_datetime < timezone.now() + timedelta(hours=24):
            messages.error(request, "Cancellations must be made at least 24 hours before the Puja time.")
            return redirect(redirect_target)
        
        new_status = 'cancelled'

    # --- Case 2: Status update (Accept/Reject) ---
    if not new_status:
        return None

    # STRICT RULE: Priest can only cancel/reject if puja is in valid state
    if new_status == 'cancelled':
        if not (booking.status in ['pending', 'confirmed', 'pending_payment', 'payment_completed']):
            messages.error(request, "Cancellation is not allowed for this booking status.")
            return redirect(redirect_target)
        
        # If already confirmed, enforce 24h rule
        if booking.status == 'confirmed':
            booking_datetime = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
            if booking_datetime < timezone.now() + timedelta(hours=24):
                messages.error(request, "Confirmed bookings can only be cancelled at least 24 hours before the Puja time.")
                return redirect(redirect_target)

    old_status = booking.status
    booking.status = new_status
    booking.save(skip_validation=True)
    
    # Restore availability if priest cancelled/rejected
    if new_status == 'cancelled':
        booking.restore_slot_availability(priest=profile)
    
    # --- Update Priest Performance & Notifications ---
    from .models import Notification, PriestPerformance
    performance, _ = PriestPerformance.objects.get_or_create(priest=profile)
    
    if new_status == 'confirmed' and old_status == 'pending':
        performance.total_assigned += 1
        performance.update_rating()
        # Notify Devotee
        Notification.objects.create(
            user=booking.devotee,
            title='Booking Confirmed!',
            message=f"Priest {profile.fullname} has confirmed your booking for {get_service_title(booking.service)}.",
            notification_type='booking_confirmed'
        )
    elif new_status == 'cancelled': # Priest Cancelled or Rejected
        performance.total_assigned += 1 
        if old_status == 'pending':
            performance.rejected_count += 1
        performance.update_rating()

        # Admin Reassignment URL
        site_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8001'
        reassign_url = f"{site_url}/admin-bookings/{booking.id}/reassign/?role=lead"

        # Notify Admin
        admin_users = User.objects.filter(is_superuser=True)
        admin_emails = list(admin_users.exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
        
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                title='Booking Action by Priest',
                message=f"Priest {profile.fullname} has {new_status}ed/rejected Booking #{booking.id}.",
                notification_type='booking_cancelled'
            )
        
        # Email Admin with Reassignment Link
        try:
            send_mail(
                f'[Alert] Priest {new_status.title()}ed Booking #{booking.id}',
                f"Purohit {profile.fullname} has {new_status}ed/rejected Booking #{booking.id} ({get_service_title(booking.service)}) on {booking.booking_date}.\n\n"
                f"Devotee: {booking.devotee_name} ({booking.devotee_phone})\n\n"
                f"Action Required: Please reassign another priest.\n"
                f"Reassign Link: {reassign_url}",
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
        except Exception as ee:
            log_debug(f"Admin alert email failed: {ee}")
    elif new_status == 'completed' and old_status != 'completed':
        performance.completed_successful += 1
        performance.update_rating()
    
    # If rejected/cancelled, restore availability
    if new_status == 'cancelled':
        booking.restore_slot_availability()
    
    # Send status update email and notify admin
    try:
        service_title = get_service_title(booking.service)
        
        # Link for Admin to reassign
        reassign_url = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/admin-bookings/{booking.id}/reassign/"
        
        # Metadata summary
        data_summary = (
            f"Booking ID: #{booking.id}\n"
            f"Service: {service_title}\n"
            f"Date: {booking.booking_date}\n"
            f"Slot: {booking.get_slot_type_display()}\n"
            f"Time: {format_time_display(booking.start_time)} - {format_time_display(booking.end_time)}\n"
        )
        
        # Contact pair
        contact_details = (
            f"Devotee: {booking.devotee_name} ({booking.devotee_phone})\n"
            f"Priest: {profile.fullname} ({profile.mobile})\n"
        )

        # 1. To Devotee: Direct status update
        if new_status == 'confirmed':
            devotee_subject = 'Booking CONFIRMED – Karya Siddhi'
            devotee_msg = (
                f"Namaste {booking.devotee_name},\n\n"
                f"Great news! Your booking for '{service_title}' has been CONFIRMED by Priest {profile.fullname}.\n\n"
                f"Booking Summary:\n{data_summary}\n"
                f"Priest Contact: {profile.fullname} ({profile.mobile})\n\n"
                f"The priest will reach out to you shortly. You can also view details on your dashboard.\n\n"
                f"Regards,\nKarya Siddhi Team"
            )
        elif new_status == 'cancelled':
            is_rejection = (old_status == 'pending')
            subject_prefix = 'Booking REJECTED' if is_rejection else 'Booking CANCELLED by Priest'
            devotee_subject = f'{subject_prefix} – Karya Siddhi'
            
            if is_rejection:
                reason_part = "could not be confirmed by the priest at this time."
            else:
                reason_part = "has been cancelled by the priest after initial acceptance."

            devotee_msg = (
                f"Namaste {booking.devotee_name},\n\n"
                f"We regret to inform you that your booking for '{service_title}' on {booking.booking_date} {reason_part}\n\n"
                f"Our admin team will reach out to you shortly to either reassign your request to another priest or process a full refund. You don't need to take any action.\n\n"
                f"Regards,\nKarya Siddhi Team"
            )
        else:
            devotee_subject = f'Booking Status Update: {new_status.capitalize()}'
            devotee_msg = (
                f"Namaste {booking.devotee_name},\n\n"
                f"The status of your booking has changed to: {new_status.capitalize()}.\n\n"
                f"Check your dashboard for updates.\n\n"
                f"Regards,\nKarya Siddhi Team"
            )

        send_mail(
            devotee_subject,
            devotee_msg,
            settings.DEFAULT_FROM_EMAIL,
            [booking.devotee.email],
            fail_silently=True,
        )
        
        # 2. To Admin: Report
        admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
        
        if new_status == 'confirmed':
            admin_subject = f'[Confirmed] Booking #{booking.id} - {service_title}'
            admin_body = (
                f"A priest has accepted a booking request.\n\n"
                f"{data_summary}\n"
                f"{contact_details}\n"
                f"Status: CONFIRMED\n\n"
                f"Regards,\nKarya Siddhi System"
            )
        elif new_status == 'cancelled':
            is_rejection = (old_status == 'pending')
            label = "REJECTED" if is_rejection else "CANCELLED BY PRIEST"
            admin_subject = f'[{label}] Booking #{booking.id} - {service_title}'
            admin_body = (
                f"The assigned priest has {label.lower()} the booking.\n\n"
                f"Action Required: Please reassign another priest if possible.\n\n"
                f"Reassign Link: {reassign_url}\n\n"
                f"Summary:\n{data_summary}\n"
                f"{contact_details}\n\n"
                f"Regards,\nKarya Siddhi System"
            )
        else:
            admin_subject = f'Admin Alert: Booking #{booking.id} {new_status.capitalize()}'
            admin_body = (
                f"Booking Status Changed\n\n"
                f"Booking ID: #{booking.id}\n"
                f"Change: {old_status.capitalize()} -> {new_status.capitalize()}\n"
                f"Action By: {profile.fullname}\n"
                f"Devotee: {booking.devotee_name}\n"
                f"Service: {service_title}\n"
                f"Date: {booking.booking_date}\n\n"
            )
        
        send_mail(
            admin_subject,
            admin_body,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=True,
        )

        # 3. To Priest: Confirmation of action
        if new_status == 'confirmed':
            priest_subject = f'Success: You accepted Booking #{booking.id}'
            priest_msg = (
                f"Hello {profile.fullname},\n\n"
                f"You have successfully CONFIRMED the booking for '{service_title}'.\n\n"
                f"{data_summary}\n"
                f"Devotee Contact: {booking.devotee_name} ({booking.devotee_phone})\n\n"
                f"Please ensure you arrive on time. Your dashboard has been updated.\n\n"
                f"Regards,\nKarya Siddhi Team"
            )
        elif new_status == 'cancelled':
            is_rejection = (old_status == 'pending')
            label = "rejected" if is_rejection else "cancelled"
            priest_subject = f'Booking #{booking.id} {label.capitalize()}'
            priest_msg = (
                f"Hello {profile.fullname},\n\n"
                f"You have successfully {label} the booking for '{service_title}' on {booking.booking_date}.\n"
                f"The slot has been freed and the admin team has been notified for reassignment.\n\n"
                f"Regards,\nKarya Siddhi Team"
            )
        else:
            priest_subject = f'Success: Status updated to {new_status.capitalize()}'
            priest_msg = (
                f"Hello {profile.fullname},\n\n"
                f"You have successfully marked Booking #{booking.id} as {new_status.capitalize()}.\n\n"
                f"Your dashboard has been updated to reflect this change.\n\n"
                f"Regards,\nKarya Siddhi Team"
            )
            
        send_mail(
            priest_subject,
            priest_msg,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=True,
        )
    except Exception as e:
        log_debug(f"Error sending priest-side status update emails for Booking #{booking.id}: {e}")

    messages.success(request, f"Booking updated to {new_status.capitalize()}.")
    return redirect(redirect_target)

@login_required
def purohit_dashboard(request):
    """Render the Purohit dashboard."""
    try:
        profile = request.user.priest_profile
    except PriestProfile.DoesNotExist:
        messages.error(request, "You do not have a Purohit profile.")
        return redirect('home')
    
    # Auto-complete due bookings for this priest
    complete_due_bookings(
        Booking.objects.filter(
            Q(priest=profile) |
            Q(additional_priest_relationships__priest=profile)
        ).distinct()
    )
        
    # Handle booking actions (Shared Helper)
    response = _handle_priest_booking_action(request, profile)
    if response:
        return response
        
    # Map service slugs/names to pretty titles for display
    # Map service slugs/names to pretty titles for display
    pretty_services = []
    
    # Handle cases where services might be stored as a string or list
    raw_services = profile.services
    if isinstance(raw_services, str):
        # Try to parse as JSON first in case it's a stringified list
        try:
            parsed = json.loads(raw_services)
            if isinstance(parsed, list):
                raw_services = parsed
            else:
                # Comma separated string
                raw_services = [s.strip() for s in raw_services.split(',') if s.strip()]
        except json.JSONDecodeError:
            # Not JSON, assume comma-separated
            raw_services = [s.strip() for s in raw_services.split(',') if s.strip()]
    
    # Ensure it's a list for iteration
    if not isinstance(raw_services, list):
        raw_services = []

    for s in raw_services:
        service_title = Puja.objects.filter(slug=s).values_list('title', flat=True).first()
        if service_title:
            pretty_services.append(service_title)
        else:
            pretty_services.append(s.strip())
            
    # Add dynamic booking data
    # Analytics for charts
    all_bookings = Booking.objects.filter(
        Q(priest=profile) | Q(additional_priest_relationships__priest=profile)
    ).distinct()
    total_bookings = all_bookings.count()
    completed_bookings = all_bookings.filter(status='completed').count()
    accepted_bookings = all_bookings.filter(status='confirmed').count()
    rejected_bookings = all_bookings.filter(status__in=['cancelled', 'cancelled_by_purohit']).count()
    
    # Completion Rate formula: (Completed / Total) * 100
    completion_rate = 0
    if total_bookings > 0:
        completion_rate = round((completed_bookings / total_bookings) * 100)

    upcoming_bookings = all_bookings.filter(
        booking_date__gte=timezone.now().date()
    ).exclude(
        status__in=['cancelled', 'cancelled_by_purohit']
    ).distinct().order_by('booking_date', 'start_time')[:5]

    upcoming_availabilities = PriestAvailability.objects.filter(
        priest=profile,
        date__gte=timezone.now().date()
    ).order_by('date')[:10]

    # Calculate pending count (Primary + Additional)
    pending_primary = all_bookings.filter(status='pending').count()
    pending_additional = BookingAdditionalPriest.objects.filter(
        priest=profile, 
        status='pending',
        booking__status__in=['pending', 'confirmed', 'pending_payment', 'payment_completed']
    ).count()
    pending_count = pending_primary + pending_additional

    # --- FIX: Define additional_assignments BEFORE using it in the loop below ---
    additional_assignments = BookingAdditionalPriest.objects.filter(
        priest=profile
    ).select_related('booking', 'booking__priest').order_by('-booking__booking_date')

    for b in upcoming_bookings:
        # Determine 24h guard (reused for both lead and assistant)
        booking_datetime = timezone.make_aware(datetime.combine(b.booking_date, b.start_time))
        is_safe_time = booking_datetime >= timezone.now() + timedelta(hours=24)

        if b.priest == profile:
            b.assigned_status = b.status
            b.is_lead = True
            # Lead can cancel if booking.status is confirmed AND it's > 24h away
            b.can_cancel_self = (b.status == 'confirmed' and is_safe_time)
        else:
            # Check assignment through-model
            assignment = additional_assignments.filter(booking=b).first()
            b.assigned_status = assignment.status if assignment else b.status
            b.is_lead = False
            # Assistant can cancel if THEIR status is confirmed AND it's > 24h away
            b.can_cancel_self = (b.assigned_status == 'confirmed' and is_safe_time)

    # Format languages for display
    display_languages = ", ".join(profile.language) if profile.language else "Not specified"

    # --- Enhancement: Total Revenue (completed bookings) ---
    from django.db.models import Sum
    total_revenue = all_bookings.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # --- Enhancement: Average Rating from PriestPerformance ---
    try:
        avg_rating = round(float(profile.performance.rating), 1)
    except Exception:
        avg_rating = 5.0

    # --- Enhancement: Total upcoming availability slots count ---
    total_upcoming_slots = PriestAvailability.objects.filter(
        priest=profile,
        date__gte=timezone.now().date()
    ).count()

    return render(request, 'pages/purohit_dashboard.html', {
        'profile': profile,
        'pretty_services': pretty_services,
        'display_languages': display_languages,
        'gothram': profile.gothram,
        'qualification': profile.qualification,
        'qualification_place': profile.qualification_place,
        'formal_vedic_training': profile.formal_vedic_training,
        'knows_smaardham': profile.knows_smaardham,
        'organize_scientifically': profile.organize_scientifically,
        'can_perform_rituals': profile.can_perform_rituals,
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'accepted_bookings': accepted_bookings,
        'rejected_bookings': rejected_bookings,
        'completion_rate': completion_rate,
        'total_revenue': total_revenue,
        'avg_rating': avg_rating,
        'total_upcoming_slots': total_upcoming_slots,
        'upcoming_bookings': upcoming_bookings,
        'upcoming_availabilities': upcoming_availabilities,
        'additional_assignments': additional_assignments,
        'pending_count': pending_count
    })
    
@login_required
def priest_availability(request):
    """View for managing priest availability."""
    return render(request, 'pages/priest_availability.html', {
        'today_date': timezone.now().date().isoformat()
    })


@login_required
def api_get_availability(request):
    """API to get availability for a specific date."""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date required'}, status=400)
    
    try:
        # Ensure user has a priest profile
        if not hasattr(request.user, 'priest_profile'):
             return JsonResponse({'error': 'Priest profile required'}, status=403)

        availability = PriestAvailability.objects.filter(
            priest=request.user.priest_profile,
            date=date_str
        ).first()
        
        if not availability:
            return JsonResponse({'exists': False})
        
        return JsonResponse({
            'exists': True,
            'morning': {
                'available': availability.morning_available,
                'start': availability.morning_start,
                'end': availability.morning_end
            },
            'afternoon': {
                'available': availability.afternoon_available,
                'start': availability.afternoon_start,
                'end': availability.afternoon_end
            },
            'evening': {
                'available': availability.evening_available,
                'start': availability.evening_start,
                'end': availability.evening_end
            },
            'custom_slots': availability.custom_slots,
            'notes': availability.notes
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_save_availability(request):
    """API to save availability for a specific date."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        # Ensure user has a priest profile
        if not hasattr(request.user, 'priest_profile'):
             return JsonResponse({'error': 'Priest profile required'}, status=403)

        data = json.loads(request.body)
        date_str = data.get('date')
        
        if not date_str:
            return JsonResponse({'error': 'Date required'}, status=400)
        
        # Get or create availability object
        availability, created = PriestAvailability.objects.get_or_create(
            priest=request.user.priest_profile,
            date=date_str
        )
        
        # Update fields
        availability.morning_available = data.get('morning', {}).get('available', False)
        if availability.morning_available:
            availability.morning_start = data.get('morning', {}).get('start')
            availability.morning_end = data.get('morning', {}).get('end')
        else:
            availability.morning_start = None
            availability.morning_end = None
            
        availability.afternoon_available = data.get('afternoon', {}).get('available', False)
        if availability.afternoon_available:
            availability.afternoon_start = data.get('afternoon', {}).get('start')
            availability.afternoon_end = data.get('afternoon', {}).get('end')
        else:
            availability.afternoon_start = None
            availability.afternoon_end = None
            
        availability.evening_available = data.get('evening', {}).get('available', False)
        if availability.evening_available:
            availability.evening_start = data.get('evening', {}).get('start')
            availability.evening_end = data.get('evening', {}).get('end')
        else:
            availability.evening_start = None
            availability.evening_end = None
            
        availability.custom_slots = data.get('custom_slots', [])
        availability.notes = data.get('notes', '')
        
        availability.full_clean() # Run validation logic defined in model
        availability.save()
        
        return JsonResponse({'success': True, 'message': 'Availability saved successfully'})
        
    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_public_priest_availability(request, priest_id):
    """Public API to get availability for a specific priest (for booking)."""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date required'}, status=400)
    
    try:
        priest = get_object_or_404(PriestProfile, pk=priest_id)
        
        availability = PriestAvailability.objects.filter(
            priest=priest,
            date=date_str
        ).first()
        
        if not availability:
            return JsonResponse({'exists': False})

        # Fetch existing bookings for this priest on this date to check exclusivity
        bookings = Booking.objects.filter(
            Q(priest=priest) | Q(additional_priest_relationships__priest=priest),
            booking_date=date_str,
            status__in=['pending', 'confirmed']
        ).exclude(additional_priest_relationships__status='cancelled').distinct()
        
        # Helper to convert string to time if needed
        def to_time(t):
            if not t: return None
            if isinstance(t, str):
                for fmt in ('%H:%M:%S', '%H:%M'):
                    try:
                        from datetime import datetime
                        return datetime.strptime(t, fmt).time()
                    except ValueError:
                        continue
            return t

        # Helper to check if a specific slot is already booked
        def is_slot_booked(start, end):
            # Support Many-to-Many relationships:
            # A Purohit can serve multiple devotees in the same time slot (group pujas)
            return False

        # Get current time for Today's date comparison
        now = timezone.localtime(timezone.now())
        is_today = date_str == now.date().isoformat()
        current_time = now.time()

        forty_eight_hours_later = now + timedelta(hours=48)

        def is_past(t):
            # 1. Base check for past time TODAY
            if is_today:
                t_obj = to_time(t)
                if t_obj and t_obj < current_time:
                    return True
            return False

        def is_48h_blocked(t):
            # 2. Enforce 48-hour booking rule (align with Model)
            if t:
                try:
                    t_obj = to_time(t)
                    b_dt = timezone.make_aware(datetime.combine(datetime.fromisoformat(date_str).date(), t_obj))
                    if b_dt < forty_eight_hours_later:
                        return True
                except:
                    pass
            return False

        # Build custom slots with availability check
        filtered_custom_slots = []
        for slot in availability.custom_slots:
            start_time = slot.get('start')
            slot_booked = is_slot_booked(start_time, slot.get('end'))
            filtered_custom_slots.append({
                'start': start_time,
                'end': slot.get('end'),
                'label': slot.get('label'),
                'available': not slot_booked and not is_past(start_time),
                'forty_eight_blocked': is_48h_blocked(start_time)
            })

        def slot_info(available_flag, start, end):
            """Build a slot dict with availability details and 48h blocking flags."""
            if not available_flag or not start:
                return None
            booked = is_slot_booked(start, end)
            blocked_48h = is_48h_blocked(start)
            return {
                'available': available_flag and not booked and not is_past(start),
                'start': start,
                'end': end,
                'booked': booked,
                'forty_eight_blocked': blocked_48h,
            }

        m = slot_info(availability.morning_available, availability.morning_start, availability.morning_end)
        a = slot_info(availability.afternoon_available, availability.afternoon_start, availability.afternoon_end)
        e = slot_info(availability.evening_available, availability.evening_start, availability.evening_end)

        return JsonResponse({
            'exists': True,
            'morning': m['available'] if m else False,
            'afternoon': a['available'] if a else False,
            'evening': e['available'] if e else False,
            'morning_slot': m,
            'afternoon_slot': a,
            'evening_slot': e,
            'custom_slots': filtered_custom_slots,
            'date': date_str,
            'notes': availability.notes,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_service_availability(request, service_slug):
    """API to get overall availability for a service across all priests, with per-slot counts."""
    try:
        from django.utils import timezone
        date_str = request.GET.get('date')
        if not date_str:
            return JsonResponse({'error': 'Date required'}, status=400)
        
        # Optional slot parameters for filtering the available_priests list
        slot_type = request.GET.get('slot_type')
        start_time_req = request.GET.get('start_time')
        end_time_req = request.GET.get('end_time')
        
        # 1. Find all priests offering this service
        if service_slug and service_slug != 'custom':
            priests = PriestProfile.objects.filter(services__contains=service_slug)
        else:
            priests = PriestProfile.objects.all()
        
        availability_summary = {
            'morning_count': 0,
            'afternoon_count': 0,
            'evening_count': 0,
            'custom_slots': {}, # label: count
            'has_any': False,
            'available_priests': []
        }

        now = timezone.localtime(timezone.now())
        is_today = date_str == now.date().isoformat()
        current_time = now.time()
        forty_eight_hours_later = now + timedelta(hours=48)
        from datetime import datetime

        def to_time(t):
            if not t: return None
            if isinstance(t, str):
                for fmt in ('%H:%M:%S', '%H:%M'):
                    try:
                        return datetime.strptime(t, fmt).time()
                    except ValueError:
                        continue
            return t

        def is_past(t):
            if is_today:
                t_obj = to_time(t)
                if t_obj and t_obj < current_time:
                    return True
            return False

        def is_48h_blocked(t):
            if t:
                try:
                    t_obj = to_time(t)
                    b_dt = timezone.make_aware(datetime.combine(datetime.fromisoformat(date_str).date(), t_obj))
                    if b_dt < forty_eight_hours_later:
                        return True
                except:
                    pass
            return False

        for priest in priests:
            avail = PriestAvailability.objects.filter(priest=priest, date=date_str).first()
            if not avail:
                continue
                
            bookings = Booking.objects.filter(
                Q(priest=priest) | (Q(additional_priest=priest) & Q(extra_priest_cancelled=False)) | Q(additional_priest_relationships__priest=priest, additional_priest_relationships__status__in=['pending', 'confirmed']),
                booking_date=date_str,
                status__in=['pending', 'confirmed']
            ).distinct()

            def is_booked(start, end):
                # Support Many-to-Many relationships:
                # Do not deduct from available pool if already booked by someone else
                return False

            # Determine if slot is 48h blocked
            m_48h = is_48h_blocked(avail.morning_start)
            a_48h = is_48h_blocked(avail.afternoon_start)
            e_48h = is_48h_blocked(avail.evening_start)

            # Track availability even if filtered for modal, to keep counts accurate
            m_avail = avail.morning_available and not is_booked(avail.morning_start, avail.morning_end) and not is_past(avail.morning_start) and not m_48h
            if m_avail: availability_summary['morning_count'] += 1
            
            a_avail = avail.afternoon_available and not is_booked(avail.afternoon_start, avail.afternoon_end) and not is_past(avail.afternoon_start) and not a_48h
            if a_avail: availability_summary['afternoon_count'] += 1
            
            e_avail = avail.evening_available and not is_booked(avail.evening_start, avail.evening_end) and not is_past(avail.evening_start) and not e_48h
            if e_avail: availability_summary['evening_count'] += 1
            
            c_avail_list = []
            for slot in avail.custom_slots:
                ts = slot.get('start')
                te = slot.get('end')
                label = slot.get('label', 'Special')
                if ts and te:
                    if not is_booked(ts, te) and not is_past(ts) and not is_48h_blocked(ts):
                        availability_summary['custom_slots'][label] = availability_summary['custom_slots'].get(label, 0) + 1
                        c_avail_list.append(slot)

            # Filtering logic for the modal (available_priests list)
            is_valid_candidate = False
            if slot_type:
                if slot_type == 'morning' and m_avail: is_valid_candidate = True
                elif slot_type == 'afternoon' and a_avail: is_valid_candidate = True
                elif slot_type == 'evening' and e_avail: is_valid_candidate = True
                elif slot_type == 'custom' and start_time_req:
                    for cs in c_avail_list:
                        if cs.get('start') == start_time_req:
                            is_valid_candidate = True
                            break
            else:
                # If no slot_type provided, return anyone available anytime (default behavior for Step 1 check)
                is_valid_candidate = (m_avail or a_avail or e_avail or len(c_avail_list) > 0)

            if is_valid_candidate:
                availability_summary['available_priests'].append({
                    'id': priest.id,
                    'fullname': priest.fullname,
                    'photo': priest.photo.url if priest.photo else None,
                    'experience': priest.experience,
                    'location': priest.location
                })

        # Fetch required priests for this service to validate slot visibility
        required_purohits = 1
        if service_slug and service_slug != 'custom':
            service_obj = Puja.objects.filter(slug=service_slug).first()
            if service_obj:
                required_purohits = service_obj.required_purohits

        availability_summary['has_any'] = len(availability_summary['available_priests']) >= required_purohits
        
        # Add boolean flags for frontend dropdowns (service_detail_content.html)
        # ONLY show slot if available priest count meets the requirement
        availability_summary['morning'] = availability_summary['morning_count'] >= required_purohits
        availability_summary['afternoon'] = availability_summary['afternoon_count'] >= required_purohits
        availability_summary['evening'] = availability_summary['evening_count'] >= required_purohits
        
        return JsonResponse(availability_summary)
    except Exception as e:
        log_debug(f"API ERROR (service_availability): {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def book_service(request, service_slug):
    """List priests available for a specific service."""
    if service_slug == 'custom':
        service = {
            'title': 'Custom Service',
            'price': 'Agreed Amount',
            'short_description': 'Consult with the priest for a custom ritual or service.'
        }
    else:
        service = Puja.objects.filter(slug=service_slug, is_active=True).first()
        
    if not service:
        # Fallback if not found in data dict (shouldn't happen if slug is valid)
        return redirect('services')
        
    # Find priests who offer this service
    if service_slug == 'custom':
        priests = PriestProfile.objects.all()
    else:
        priests = PriestProfile.objects.filter(services__contains=service_slug)
    
    # Filter by availability if date and slot are provided
    selected_date = request.GET.get('date')
    selected_slot = request.GET.get('slot')
    
    # Devotee details to carry forward
    devotee_data = {
        'name': request.GET.get('devotee_name', ''),
        'gothram': request.GET.get('gothram', ''),
        'nakshatram': request.GET.get('nakshatram', ''),
        'date': selected_date,
        'slot': selected_slot,
        'language': request.GET.get('language', ''),
    }

    # Filter by requirements (Language)
    if devotee_data['language']:
        # Filter priests whose language list or string contains the preferred language
        priests = priests.filter(language__contains=devotee_data['language'])

    # Validation: Prevent past dates/slots
    now = timezone.localtime(timezone.now())
    today = now.date()
    current_time = now.time()

    if selected_date:
        try:
            b_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            if b_date < today:
                messages.error(request, "Selected date is in the past.")
                selected_date = None # Stop filtering by past date
            elif b_date == today and selected_slot:
                # Helper to check slot times (approximate for the dropdown)
                # Morning: 12 PM, Afternoon: 4 PM, Evening: 9 PM
                slot_hours = {'morning': 12, 'afternoon': 16, 'evening': 21}
                if current_time.hour >= slot_hours.get(selected_slot, 0):
                     messages.error(request, "The selected time slot has already passed for today.")
                     selected_slot = None
        except:
            pass

    if selected_date and selected_slot:
        available_priest_ids = []
        for priest in priests:
            # Check availability for the date
            avail = PriestAvailability.objects.filter(priest=priest, date=selected_date).first()
            if avail:
                slot_available = False
                slot_start = None
                slot_end = None
                
                if selected_slot == 'morning':
                    slot_available = avail.morning_available
                    slot_start, slot_end = avail.morning_start, avail.morning_end
                elif selected_slot == 'afternoon':
                    slot_available = avail.afternoon_available
                    slot_start, slot_end = avail.afternoon_start, avail.afternoon_end
                elif selected_slot == 'evening':
                    slot_available = avail.evening_available
                    slot_start, slot_end = avail.evening_start, avail.evening_end
                
                if slot_available and slot_start and slot_end:
                    # Check if already booked (pending or confirmed)
                    booked = Booking.objects.filter(
                        Q(priest=priest) | Q(additional_priest_relationships__priest=priest),
                        booking_date=selected_date,
                        status__in=['pending', 'confirmed'],
                        start_time__lt=slot_end,
                        end_time__gt=slot_start
                    ).exclude(additional_priest_relationships__status='cancelled').distinct().exists()
                    
                    if not booked:
                        available_priest_ids.append(priest.id)
        
        priests = priests.filter(id__in=available_priest_ids)
        
        # Final safety: Block list if we don't have enough priests for the service
        required_purohits = 1
        if service and hasattr(service, 'required_purohits'):
            required_purohits = service.required_purohits
        
        if priests.count() < required_purohits:
            priests = priests.none()
            messages.error(request, "Currently this puja is not available for the selected slot as the required number of purohits are not available.")

    context = {
        'service': service,
        'service_slug': service_slug,
        'priests': priests,
        'devotee_data': devotee_data
    }
    return render(request, 'pages/booking_service_priests.html', context)

# @login_required removed for manual check to handle redirect and messages better
def book_priest(request, priest_id):
    """Show booking form for a specific priest."""
    from .models import PriestProfile, Booking
    if not request.user.is_authenticated:
        messages.info(request, "Please login as a devotee to book a service.")
        return redirect('login')
    priest = get_object_or_404(PriestProfile, pk=priest_id)
    service_slug = request.GET.get('service')
    service = Puja.objects.filter(slug=service_slug, is_active=True).first() if service_slug else None
    
    # Parse minimum service price for form pre-fill
    service_min_price = 0
    service_price = service.price if service else None
    if service_price:
        import re
        nums = re.findall(r'[\d,]+', service_price)
        if nums:
            service_min_price = int(nums[0].replace(',', ''))
    required_purohits = service.required_purohits if service else 1

    context = {
        'priest': priest,
        'service': service,
        'service_slug': service_slug,
        'today_date': timezone.localtime(timezone.now()).date().isoformat(),
        'service_min_price': service_min_price,
        'required_purohits': required_purohits,
        'prefill_data': {
            'name': request.GET.get('devotee_name', ''),
            'gothram': request.GET.get('gothram', ''),
            'nakshatram': request.GET.get('nakshatram', ''),
            'date': request.GET.get('date', ''),
            'slot': request.GET.get('slot', ''),
        }
    }

    if request.method == 'POST':
        # Handle booking submission
        booking_date = request.POST.get('booking_date')
        slot_type = request.POST.get('slot_type')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        special_requests = request.POST.get('special_requests', '')
        # Support multiple additional priests — getlist returns all values for the same key
        additional_priest_ids = request.POST.getlist('additional_priest_id')
        # Filter out empty strings
        additional_priest_ids = [pid for pid in additional_priest_ids if pid]
        
        # Basic validation
        if not all([booking_date, slot_type, start_time, end_time]):
             messages.error(request, "Please fill all required fields.")
        else:
            # Backend Validation: Prevent past dates/times AND enforce 48h lead time
            now = timezone.localtime(timezone.now())
            forty_eight_hours_later = now + timedelta(hours=48)
            try:
                # Convert booking_date string to date object
                b_date = datetime.strptime(booking_date, '%Y-%m-%d').date()
                
                # Convert start_time to time object
                t_start = start_time
                if isinstance(t_start, str):
                    try:
                        if len(t_start.split(':')) == 2:
                            t_start = datetime.strptime(t_start, '%H:%M').time()
                        else:
                            t_start = datetime.strptime(t_start, '%H:%M:%S').time()
                    except:
                        pass
                
                if not isinstance(t_start, time):
                     messages.error(request, "Invalid time format.")
                     return render(request, 'pages/booking_form.html', context)

                booking_datetime = timezone.make_aware(datetime.combine(b_date, t_start))
                
                if booking_datetime < forty_eight_hours_later:
                    messages.error(request, "Bookings must be made at least 48 hours in advance.")
                    return render(request, 'pages/booking_form.html', context)
            except Exception as e:
                messages.error(request, f"Invalid date/time format: {str(e)}")
                return render(request, 'pages/booking_form.html', context)

            # --- Enforce Required Priest Count & Global Availability ---
            selected_total = 1 + len(additional_priest_ids)
            if selected_total < required_purohits:
                # Many-to-many relationship fix: Demote this from a hard error to a warning
                # Allows devotees to book available purohits even if the full required quota isn't met
                messages.warning(request, f"Note: This puja usually suggests {required_purohits} purohits. Proceeding with {selected_total}.")

            try:
                # 1. Total available priests for this service/slot check
                # This ensures the "Currently this puja is not available for the selected slot" rule
                if service_slug and service_slug != 'custom':
                    all_offering_priests = PriestProfile.objects.filter(services__contains=service_slug)
                else:
                    all_offering_priests = PriestProfile.objects.all()
                available_count = 0
                for p_candidate in all_offering_priests:
                    # Many-to-many relationship: no exclusive booking lock checks here either
                        # Also check PriestAvailability
                        from .models import PriestAvailability
                        avail_obj = PriestAvailability.objects.filter(priest=p_candidate, date=booking_date).first()
                        if avail_obj:
                             # Check if any slot matches the requested timeframe
                             # For simplicity, if they have ANY slot that overlaps, we count them as "available"
                             # but strictly we should check morning/afternoon/evening/custom
                             if slot_type == 'morning' and avail_obj.morning_available: available_count += 1
                             elif slot_type == 'afternoon' and avail_obj.afternoon_available: available_count += 1
                             elif slot_type == 'evening' and avail_obj.evening_available: available_count += 1
                             elif slot_type == 'custom':
                                 for cs in avail_obj.custom_slots:
                                     if cs.get('start') == start_time:
                                         available_count += 1
                                         break

                if available_count < required_purohits:
                    messages.error(request, "Currently this puja is not available for the selected slot.")
                    return render(request, 'pages/booking_form.html', context)

                # --- Validate & fetch additional priests ---
                additional_priests = []
                seen_ids = set()
                for ap_id in additional_priest_ids:
                    if ap_id in seen_ids:
                        continue
                    seen_ids.add(ap_id)
                    try:
                        ap = PriestProfile.objects.get(pk=ap_id)
                    except PriestProfile.DoesNotExist:
                        messages.error(request, f"Priest with ID {ap_id} not found.")
                        return render(request, 'pages/booking_form.html', context)
                    if ap == priest:
                        messages.error(request, f"Additional priest cannot be the same as the primary priest.")
                        return render(request, 'pages/booking_form.html', context)
                    # Many-to-many relationship: no exclusive booking lock checks for additional priests either
                    additional_priests.append(ap)

                service_display = 'Custom Service'
                if service and hasattr(service, 'title'):
                    service_display = service.title
                elif service_slug and service_slug != 'custom':
                    service_display = service_slug.replace('-', ' ').title()

                booking = Booking(
                    priest=priest,
                    devotee=request.user,
                    service=service_display,
                    booking_date=booking_date,
                    slot_type=slot_type,
                    start_time=start_time,
                    end_time=end_time,
                    devotee_name=request.POST.get('devotee_name') or request.user.get_full_name() or request.user.username,
                    devotee_phone=request.POST.get('phone', ''),
                    devotee_address=request.POST.get('address', ''),
                    gothram=request.POST.get('gothram', ''),
                    nakshatram=request.POST.get('nakshatram', ''),
                    special_requests=special_requests,
                    amount=request.POST.get('amount') or service_min_price,
                    status='pending_payment'
                )

                booking.full_clean()
                booking.save()

                # Save additional priests via through-model
                for ap in additional_priests:
                    BookingAdditionalPriest.objects.get_or_create(
                        booking=booking,
                        priest=ap,
                        defaults={'status': 'pending'}
                    )
                
                # Send Confirmation Emails
                try:
                    log_debug(f"Attempting to send booking confirmation emails for Booking #{booking.id}...")
                    devotee_email = request.user.email
                    service_title = service.title if service and hasattr(service, 'title') else 'Custom Service'
                    priest_name = priest.fullname

                    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@karyasiddhi.com')

                    extra_names = ', '.join(ap.fullname for ap in additional_priests)
                    priest_info = f"Primary Priest: {priest_name}"
                    if extra_names:
                        priest_info += f"\nAdditional Priest(s): {extra_names}"

                    # 1. To Devotee
                    try:
                        devotee_dashboard_link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/devotee/dashboard/"
                        send_mail(
                            'Booking Request Received – Karya Siddhi',
                            f"Namaste {booking.devotee_name},\n\n"
                            f"Thank you for choosing Karya Siddhi. We have received your booking request for '{service_title}'.\n\n"
                            f"Booking Summary:\n"
                            f"- {priest_info}\n"
                            f"- Date: {booking.booking_date}\n"
                            f"- Time: {format_time_display(booking.start_time)} - {format_time_display(booking.end_time)}\n"
                            f"- Location: {booking.devotee_address}\n\n"
                            f"Status: Awaiting Priest Confirmation\n"
                            f"The priests will review and confirm your request shortly.\n\n"
                            f"You can view your booking details here:\n{devotee_dashboard_link}\n\n"
                            "Regards,\nKarya Siddhi Team",
                            from_email,
                            [devotee_email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        log_debug(f"Devotee email failed: {e}")

                    # 2. To Primary Priest
                    try:
                        priest_dashboard_link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/purohit/dashboard/"
                        priest_message = (
                            f"Hello {priest_name},\n\n"
                            f"A new devotee ({booking.devotee_name}) has requested your service for '{service_title}'.\n\n"
                            f"Schedule Details:\n"
                            f"- Date: {booking.booking_date}\n"
                            f"- Time: {format_time_display(booking.start_time)} - {format_time_display(booking.end_time)}\n"
                            f"- Location: {booking.devotee_address}\n\n"
                            f"Other Priest(s): {extra_names if extra_names else 'None'}\n\n"
                            f"Devotee Details:\n"
                            f"- Phone: {booking.devotee_phone}\n"
                            f"- Special Requests: {booking.special_requests or 'None'}\n\n"
                            f"Please log in to your dashboard to confirm this booking:\n{priest_dashboard_link}\n\n"
                            "Regards,\nKarya Siddhi Team"
                        )
                        send_mail(
                            f'New Service Request: {service_title}',
                            priest_message,
                            from_email,
                            [priest.user.email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        log_debug(f"Primary priest email failed: {e}")

                    # 3. To Each Additional Priest
                    for ap in additional_priests:
                        try:
                            add_priest_dashboard_link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/purohit/dashboard/"
                            add_priest_message = (
                                f"Hello {ap.fullname},\n\n"
                                f"A new devotee ({booking.devotee_name}) has requested you as an additional priest for '{service_title}'.\n\n"
                                f"Primary Priest: {priest_name}\n"
                                f"Schedule Details:\n"
                                f"- Date: {booking.booking_date}\n"
                                f"- Time: {format_time_display(booking.start_time)} - {format_time_display(booking.end_time)}\n"
                                f"- Location: {booking.devotee_address}\n\n"
                                f"Devotee Details:\n"
                                f"- Phone: {booking.devotee_phone}\n"
                                f"- Special Requests: {booking.special_requests or 'None'}\n\n"
                                f"Please log in to your dashboard to confirm this booking:\n{add_priest_dashboard_link}\n\n"
                                "Regards,\nKarya Siddhi Team"
                            )
                            send_mail(
                                f'New Service Request (Additional Priest): {service_title}',
                                add_priest_message,
                                from_email,
                                [ap.user.email],
                                fail_silently=True,
                            )
                        except Exception as e:
                            log_debug(f"Additional priest email failed for {ap.fullname}: {e}")

                    # 4. To Admin
                    try:
                        admin_dashboard_link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/admin-portal/"
                        admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [from_email]
                        extra_lines = ''.join(
                            f"Additional Priest: {ap.fullname} (Phone: {ap.mobile})\n"
                            for ap in additional_priests
                        )
                        admin_message = (
                            f"A new booking (ID #{booking.id}) has been submitted.\n\n"
                            f"Service: {service_title}\n"
                            f"Primary Priest: {priest_name} (Phone: {priest.mobile})\n"
                            + extra_lines +
                            f"Devotee: {booking.devotee_name} (Phone: {booking.devotee_phone})\n"
                            f"Requested Date: {booking.booking_date}\n\n"
                            f"System: Pending action from Priests.\n\n"
                            f"View in Admin Portal: {admin_dashboard_link}\n\n"
                            f"Regards,\nKarya Siddhi System"
                        )
                        send_mail(
                            'New Booking Request Alert',
                            admin_message,
                            from_email,
                            admin_emails,
                            fail_silently=True,
                        )
                    except Exception as e:
                        log_debug(f"Admin email failed: {e}")

                except Exception as e:
                    log_debug(f"Unexpected error in email logic: {e}")

                messages.success(request, "Booking created! please complete the payment to proceed.")
                return redirect('initiate_payment', booking_id=booking.id)
            except ValidationError as e:
                # Handle dictionary errors or simple list errors
                if hasattr(e, 'message_dict'):
                    error_msg = "; ".join([f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()])
                elif hasattr(e, 'messages'):
                    error_msg = e.messages[0]
                else:
                    error_msg = str(e)
                messages.error(request, f"Booking failed: {error_msg}")
            except Exception as e:
                log_debug(f"Unexpected booking error: {e}")
                messages.error(request, f"An unexpected error occurred: {str(e)}")
    
    return render(request, 'pages/booking_form.html', context)
@login_required
def my_bookings(request):
    """List bookings for the logged-in devotee and handle status updates."""
    # Lazy import to avoid circular dependencies
    from .models import Booking, PriestProfile, DevoteeProfile
    from django.conf import settings
    
    try:
        profile = request.user.devotee_profile
    except DevoteeProfile.DoesNotExist:
        if hasattr(request.user, 'priest_profile'):
             bookings = Booking.objects.filter(priest=request.user.priest_profile).order_by('-booking_date', '-start_time')
             return render(request, 'pages/priest_bookings.html', {'bookings': bookings})
        messages.error(request, "Devotee profile not found.")
        return redirect('home')

    # Auto-complete due bookings for this devotee
    complete_due_bookings(Booking.objects.filter(devotee=request.user))
        
    # Handle status updates via POST (Devotee canceling or marking complete)
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        action = request.POST.get('action')
        new_status = request.POST.get('status')


        # --- Partial Cancellation: Extra Priest Only ---
        if booking_id and action == 'cancel_extra':
            booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)
            relation_id = request.POST.get('relation_id')
            
            # Find the specific assignment to cancel
            if relation_id:
                rel = BookingAdditionalPriest.objects.filter(booking=booking, pk=relation_id).first()
            else:
                rel = BookingAdditionalPriest.objects.filter(booking=booking).exclude(status='cancelled').first()

            if rel:
                # Rule: Cancellation must be made at least 24 hours before the Puja time.
                booking_datetime = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
                if booking_datetime < timezone.now() + timedelta(hours=24):
                    messages.error(request, "Cancellations must be made at least 24 hours before the Puja time.")
                    return redirect('my_bookings')

                # STRICT RULE: Prevent cancellation if puja is not in pending/confirmed status
                if not (booking.status in ['pending', 'confirmed']):
                    messages.error(request, "Cancellation is not allowed for this booking status.")
                    return redirect('my_bookings')

                cancelled_priest = rel.priest
                rel.status = 'cancelled'
                rel.save()
                booking.save(skip_validation=True)

                # Restore the cancelled priest's availability slot
                booking.restore_slot_availability(priest=cancelled_priest)

                # Send Emails to ALL parties
                try:
                    admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
                    
                    # 1. To Devotee
                    send_mail(
                        'Extra Priest Cancellation Confirmed',
                        f"Namaste {booking.devotee_name},\n\n"
                        f"Per your request, we have cancelled the additional priest ({cancelled_priest.fullname}) for your booking of '{booking.service}' on {booking.booking_date}.\n\n"
                        f"Note: Your primary priest ({booking.priest.fullname}) remains assigned and the booking is still active.\n\n"
                        f"Regards,\nKarya Siddhi Team",
                        settings.DEFAULT_FROM_EMAIL,
                        [request.user.email],
                        fail_silently=False,
                    )

                    # 2. To Cancelled Priest
                    send_mail(
                        'Schedule Update: Additional Priest Booking Cancelled',
                        f"Hello {cancelled_priest.fullname},\n\n"
                        f"The devotee has cancelled your assignment as an additional priest for '{booking.service}' on {booking.booking_date}.\n\n"
                        f"Your schedule for this time slot is now FREE automatically.\n\n"
                        f"Regards,\nKarya Siddhi Team",
                        settings.DEFAULT_FROM_EMAIL,
                        [cancelled_priest.user.email],
                        fail_silently=False,
                    )

                    # 3. To Primary Priest
                    send_mail(
                        'Booking Update: Additional Priest Cancelled',
                        f"Hello {booking.priest.fullname},\n\n"
                        f"This is an update for your booking of '{booking.service}' on {booking.booking_date}.\n\n"
                        f"The devotee has cancelled the additional priest ({cancelled_priest.fullname}). You are now the sole priest assigned to this service.\n\n"
                        f"The rest of the booking details remain unchanged.\n\n"
                        f"Regards,\nKarya Siddhi Team",
                        settings.DEFAULT_FROM_EMAIL,
                        [booking.priest.user.email],
                        fail_silently=False,
                    )

                    # 4. To Admin
                    send_mail(
                        f'Admin Alert: Partial Cancellation for Booking #{booking.id}',
                        f"A devotee has cancelled the additional priest for Booking #{booking.id}.\n"
                        f"Service: {booking.service}\n"
                        f"Primary Priest: {booking.priest.fullname}\n"
                        f"Cancelled Additional Priest: {cancelled_priest.fullname}\n"
                        f"Date: {booking.booking_date}\n\n"
                        f"Regards,\nKarya Siddhi System",
                        settings.DEFAULT_FROM_EMAIL,
                        admin_emails,
                        fail_silently=False,
                    )
                except Exception as e:
                    log_debug(f"Error sending partial cancellation emails: {str(e)}")

                messages.success(request, f"Additional priest {cancelled_priest.fullname} cancelled successfully.")
            return redirect('my_bookings')

        # --- Regular status update (cancel) ---
        if booking_id and new_status == 'cancelled':
            # Security check: Ensure devotee owns this booking
            booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)
            
            # Validation: Devotees can only change to 'cancelled'
            if new_status == 'cancelled':
                # Rule: A devotee can cancel a booking until the Puja start time.
                # Refund percentage depends on timing: >24h (90%), 0-24h (50%), <0h (None)
                booking_datetime = timezone.make_aware(datetime.combine(booking.booking_date, booking.start_time))
                now = timezone.now()
                
                if now >= booking_datetime:
                    messages.error(request, "Cancellations are not allowed once the ritual has started.")
                    return redirect('my_bookings')

                # STRICT RULE: Cancel ONLY if pending OR confirmed
                if booking.status in ['pending', 'confirmed']:
                    old_status = booking.status
                    booking.status = 'cancelled'
                    booking.save(skip_validation=True)

                    # Restore the priest's availability slot so others can book it
                    booking.restore_slot_availability()

                    # --- Automated Refund Processing ---
                    try:
                        refund_amt = calculate_refund_amount(booking)
                        booking.refund_amount = refund_amt
                        if refund_amt > 0:
                            booking.refund_status = 'pending'
                            booking.save(skip_validation=True)
                            
                            # Initiate PhonePe Refund
                            refund_obj = process_refund(booking, reason='Cancelled by devotee')
                            if refund_obj and refund_obj.refund_status == 'PROCESSED':
                                booking.refund_status = 'completed'
                            elif refund_obj:
                                booking.refund_status = 'initiated'
                            else:
                                booking.refund_status = 'failed'
                        else:
                            booking.refund_status = 'none'
                        booking.save(skip_validation=True)
                    except Exception as re:
                        log_debug(f"Refund automation failed for booking #{booking.id}: {re}")
                        booking.refund_status = 'failed'
                        booking.save(skip_validation=True)
                else:
                    messages.error(request, "Cancellation is not allowed for this booking status.")
                    return redirect('my_bookings')

                # Send detailed emails to all parties
                try:
                    admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]

                    extra_priests_list = list(booking.additional_priest_relationships.exclude(status='cancelled').select_related('priest'))
                    extra_names = ", ".join(rel.priest.fullname for rel in extra_priests_list)
                    
                    booking_summary = (
                        f"  Booking ID   : #{booking.id}\n"
                        f"  Service      : {booking.service}\n"
                        f"  Date         : {booking.booking_date}\n"
                        f"  Time         : {format_time_display(booking.start_time)} - {format_time_display(booking.end_time)}\n"
                        f"  Primary Priest: {booking.priest.fullname}\n"
                        + (f"  Extra Priests: {extra_names}\n" if extra_names else "") +
                        f"  Status       : Fully Cancelled\n"
                    )

                    # 1. To Devotee: Cancellation receipt
                    send_mail(
                        'Booking Cancellation Confirmed – Karya Siddhi',
                        f"Namaste {booking.devotee_name},\n\n"
                        f"Your booking for '{booking.service}' on {booking.booking_date} has been successfully cancelled.\n\n"
                        f"{booking_summary}\n"
                        f"Regards,\nKarya Siddhi Team",
                        settings.DEFAULT_FROM_EMAIL,
                        [booking.devotee.email],
                        fail_silently=True,
                    )

                    # 2. To Primary Priest: Slot is freed
                    send_mail(
                        'Schedule Update: Booking Cancelled by Devotee',
                        f"Hello {booking.priest.fullname},\n\n"
                        f"The devotee ({booking.devotee_name}) has cancelled the booking for '{booking.service}' on {booking.booking_date}.\n\n"
                        f"Your {booking.slot_type} slot for this date has been automatically freed and is now available for other devotees.\n\n"
                        f"Regards,\nKarya Siddhi Team",
                        settings.DEFAULT_FROM_EMAIL,
                        [booking.priest.user.email],
                        fail_silently=True,
                    )

                    # 3. To All Additional Priests (active ones)
                    extra_priests_list = list(booking.additional_priest_relationships.exclude(status='cancelled').select_related('priest'))
                    for rel in extra_priests_list:
                        try:
                            send_mail(
                                'Schedule Update: Additional Priest Assignment Cancelled',
                                f"Hello {rel.priest.fullname},\n\n"
                                f"The booking for '{booking.service}' on {booking.booking_date} has been cancelled by the devotee.\n\n"
                                f"Your schedule is now FREE for this slot.\n\n"
                                f"Regards,\nKarya Siddhi Team",
                                settings.DEFAULT_FROM_EMAIL,
                                [rel.priest.user.email],
                                fail_silently=True,
                            )
                        except Exception as e:
                            log_debug(f"Failed to notify additional priest {rel.priest.fullname}: {e}")

                    # 4. To Admin
                    send_mail(
                        f'[Alert] Devotee Cancelled Booking #{booking.id}',
                        f"A devotee has cancelled a booking.\n"
                        f"The Purohit's availability slot has been automatically restored.\n\n"
                        f"Summary:\n{booking_summary}\n"
                        f"Regards,\nKarya Siddhi System",
                        settings.DEFAULT_FROM_EMAIL,
                        admin_emails,
                        fail_silently=True,
                    )
                except Exception as e:
                    log_debug(f"Error sending devotee cancellation emails for Booking #{booking.id}: {e}")

                messages.success(request, "Booking cancelled successfully. A confirmation email has been sent to you.")
            else:
                messages.error(request, "Invalid status update.")
            return redirect('my_bookings')

    bookings = Booking.objects.filter(devotee=request.user).order_by('-booking_date', '-start_time')
    return render(request, 'pages/my_bookings.html', {
        'profile': profile,
        'bookings': bookings,
        'enquiry_categories': EnquiryCategory.objects.filter(is_active=True).order_by('display_order', 'name')
    })

@login_required
def booking_success(request):
    """Render the booking success page."""
    booking_id = request.GET.get('id')
    booking = None
    if booking_id:
        booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)
        
    return render(request, 'pages/booking_success.html', {'booking': booking})

@login_required
def devotee_dashboard(request):
    """Render the Devotee dashboard."""
    try:
        profile = request.user.devotee_profile
    except DevoteeProfile.DoesNotExist:
        messages.error(request, "Devotee profile not found.")
        return redirect('home')

    # Auto-complete due bookings for this devotee
    complete_due_bookings(Booking.objects.filter(devotee=request.user))

    from django.db.models import Sum
    all_bookings = Booking.objects.filter(devotee=request.user)
    total_bookings = all_bookings.count()
    upcoming_count = all_bookings.filter(
        booking_date__gte=timezone.now().date()
    ).exclude(status__in=['cancelled', 'cancelled_by_purohit']).count()
    completed_count = all_bookings.filter(status='completed').count()
    total_spent = all_bookings.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    upcoming_bookings = all_bookings.filter(
        booking_date__gte=timezone.now().date()
    ).exclude(status__in=['cancelled', 'cancelled_by_purohit']).order_by('booking_date', 'start_time')[:5]

    # Recently completed for "Book Again" feature
    recent_completed = all_bookings.filter(status='completed').order_by('-booking_date')[:3]

    return render(request, 'pages/devotee_dashboard.html', {
        'profile': profile,
        'total_bookings': total_bookings,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'total_spent': total_spent,
        'upcoming_bookings': upcoming_bookings,
        'recent_completed': recent_completed,
        'enquiry_categories': EnquiryCategory.objects.filter(is_active=True).order_by('display_order', 'name')
    })

@login_required
def priest_bookings(request):
    """List bookings for the logged-in priest."""
    if not hasattr(request.user, 'priest_profile'):
        messages.error(request, "Access denied. Priest profile required.")
        return redirect('home')
        
    profile = request.user.priest_profile
    
    # Lazy import
    from .models import Booking, BookingAdditionalPriest
    
    complete_due_bookings(
        Booking.objects.filter(
            Q(priest=profile) |
            Q(additional_priest=profile) |
            Q(additional_priest_relationships__priest=profile)
        ).distinct()
    )
    
    # Handle booking actions (Shared Helper)
    response = _handle_priest_booking_action(request, profile)
    if response:
        return response

    profile = request.user.priest_profile
    # base_query = Q(priest=profile) | Q(additional_priest=profile)
    # bookings = Booking.objects.filter(base_query).order_by('-booking_date', '-start_time')
    
    # pending_count = Booking.objects.filter(base_query, status='pending').count()
    
    # return render(request, 'pages/priest_bookings.html', {
    #     'bookings': bookings,
    #     'pending_count': pending_count
    # })

    # Primary priest bookings
    primary_bookings = Booking.objects.filter(
        Q(priest=profile) | Q(additional_priest=profile)
    ).order_by('-booking_date', '-start_time')

    # Additional priest assignments (new system)
    additional_assignments = BookingAdditionalPriest.objects.filter(
        priest=profile
    ).select_related('booking', 'booking__priest').order_by('-booking__booking_date')

    # Calculate pending count
    pending_primary = Booking.objects.filter(
        (Q(priest=profile) | Q(additional_priest=profile)),
        status='pending'
    ).count()
    
    pending_additional = BookingAdditionalPriest.objects.filter(
        priest=profile, 
        status='pending',
        booking__status__in=['pending', 'confirmed', 'pending_payment', 'payment_completed']
    ).count()
    
    pending_count = pending_primary + pending_additional

    # Process primary bookings for template
    for b in primary_bookings:
        booking_datetime = timezone.make_aware(datetime.combine(b.booking_date, b.start_time))
        b.can_cancel_self = (b.status == 'confirmed' and booking_datetime >= timezone.now() + timedelta(hours=24))

    # Process additional assignments for template
    for assignment in additional_assignments:
        booking_datetime = timezone.make_aware(datetime.combine(assignment.booking.booking_date, assignment.booking.start_time))
        assignment.can_cancel_self = (assignment.status == 'confirmed' and booking_datetime >= timezone.now() + timedelta(hours=24))

    return render(request, 'pages/priest_bookings.html', {
        'bookings': primary_bookings,
        'additional_assignments': additional_assignments,
        'current_priest': profile,
        'pending_count': pending_count
    })
    
def logout_view(request):
    """Handle general logout."""
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def purohit_logout(request):
    """Handle Priest logout."""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')

@login_required
def purohit_edit_profile(request):
    """Handle Priest profile update."""
    try:
        profile = request.user.priest_profile
    except PriestProfile.DoesNotExist:
        messages.error(request, "You do not have a Purohit profile.")
        return redirect('home')
        
    if request.method == 'POST':
        form = PriestEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Handle services update separately as it's a list from checkboxes
            profile = form.save(commit=False)
            # Clean whitespaces from services list
            profile.services = [s.strip() for s in request.POST.getlist('services')]
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('purohit_dashboard')
    else:
        form = PriestEditForm(instance=profile)
        
    return render(request, 'pages/purohit_edit_profile.html', {
        'form': form, 
        'profile': profile, 
        'services': Puja.objects.filter(is_active=True).order_by('display_order', 'title')
    })

def purohit_forgot_password(request):
    """Handle forgot password - step 1: verify email and send OTP."""
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        
        if user and hasattr(user, 'priest_profile'):
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            
            # Store in session
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            # Send Email
            try:
                # Simulate/Log OTP for testing
                log_debug(f"Attempting to send OTP email to {email}...")
                print(f"============================================")
                print(f"DEBUG OTP for {email}: {otp}")
                print(f"============================================")
                
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                log_debug(f"OTP email sent successfully to {email}")
                messages.success(request, "OTP has been sent to your registered email.")
                return redirect('purohit_verify_otp')
            except Exception as e:
                log_debug(f"Error sending OTP email: {e}")
                messages.error(request, f"Error sending email: {str(e)}")
        else:
            messages.error(request, "Email address not registered as a Priest.")
    return render(request, 'pages/purohit_forgot_password.html')

def purohit_verify_otp(request):
    """Handle forgot password - step 2: verify OTP."""
    log_debug(f"purohit_verify_otp called with method {request.method}")
    if 'reset_email' not in request.session:
        log_debug("'reset_email' not in session, redirecting to forgot password")
        return redirect('purohit_forgot_password')
        
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('reset_otp')
        log_debug(f"Entered OTP: {entered_otp}, Session OTP: {session_otp}")
        
        if entered_otp == session_otp:
            log_debug("OTP matches! Setting otp_verified = True")
            request.session['otp_verified'] = True
            return redirect('purohit_reset_password')
        else:
            log_debug("OTP mismatch")
            messages.error(request, "Invalid OTP. Please try again.")
            
    return render(request, 'pages/purohit_verify_otp.html')

def purohit_reset_password(request):
    """Handle forgot password - step 3: reset password."""
    if 'reset_email' not in request.session or 'otp_verified' not in request.session:
        return redirect('purohit_forgot_password')
        
    if request.method == 'POST':
        form = PurohitResetPasswordForm(request.POST)
        if form.is_valid():
            new_pass = form.cleaned_data.get('password')
            email = request.session['reset_email']
            try:
                user = User.objects.get(email=email)
                user.set_password(new_pass)
                user.save()
                
                # Cleanup session
                if 'reset_email' in request.session: del request.session['reset_email']
                if 'reset_otp' in request.session: del request.session['reset_otp']
                if 'otp_verified' in request.session: del request.session['otp_verified']
                
                messages.success(request, "Password reset successful. Please login with new password.")
                return redirect('purohit_login')
            except Exception as e:
                messages.error(request, f"Error resetting password: {str(e)}")
    else:
        form = PurohitResetPasswordForm()
                
    return render(request, 'pages/purohit_reset_password.html', {'form': form})

# Devotee Forgot Password Views
def devotee_forgot_password(request):
    log_debug(f"devotee_forgot_password called with method {request.method}")
    if request.method == 'POST':
        email = request.POST.get('email')
        log_debug(f"Forgot password attempt for email: {email}")
        user = User.objects.filter(email=email).first()
        
        if user:
            otp = str(random.randint(100000, 999999))
            request.session['devotee_reset_email'] = email
            request.session['devotee_reset_otp'] = otp
            log_debug(f"OTP generated and stored in session: {otp}")
            
            try:
                log_debug(f"Attempting to send Devotee OTP email to {email}...")
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                log_debug(f"Devotee OTP email sent successfully to {email}")
                messages.success(request, "OTP has been sent to your registered email.")
                return redirect('devotee_verify_otp')
            except Exception as e:
                log_debug(f"Email error during forgot password: {e}")
                messages.error(request, f"Error sending email: {str(e)}")
        else:
            log_debug("Email not found")
            messages.error(request, "Email address not registered.")
    return render(request, 'pages/devotee_forgot_password.html')

def devotee_verify_otp(request):
    log_debug(f"devotee_verify_otp called with method {request.method}")
    if 'devotee_reset_email' not in request.session:
        log_debug("'devotee_reset_email' not in session, redirecting")
        return redirect('devotee_forgot_password')
        
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('devotee_reset_otp')
        log_debug(f"Entered OTP: {entered_otp}, Session OTP: {session_otp}")
        
        if entered_otp == session_otp:
            log_debug("OTP matches! Setting devotee_otp_verified = True")
            request.session['devotee_otp_verified'] = True
            return redirect('devotee_reset_password')
        else:
            log_debug("OTP mismatch")
            messages.error(request, "Invalid OTP.")
    return render(request, 'pages/devotee_verify_otp.html')

def devotee_reset_password(request):
    if 'devotee_reset_email' not in request.session or 'devotee_otp_verified' not in request.session:
        return redirect('devotee_forgot_password')
        
    if request.method == 'POST':
        form = PurohitResetPasswordForm(request.POST) # Reusing this form as it has the same logic
        if form.is_valid():
            new_pass = form.cleaned_data.get('password')
            email = request.session['devotee_reset_email']
            try:
                user = User.objects.get(email=email)
                user.set_password(new_pass)
                user.save()
                
                # Cleanup
                del request.session['devotee_reset_email']
                del request.session['devotee_reset_otp']
                del request.session['devotee_otp_verified']
                
                messages.success(request, "Password reset successful.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error resetting password: {str(e)}")
    else:
        form = PurohitResetPasswordForm()

    return render(request, 'pages/devotee_reset_password.html', {'form': form})

# ─── Admin Login ────────────────────────────────────────────────────────────
def admin_login_view(request):
    """Dedicated login page for superuser/admin access."""
    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.user.is_authenticated:
        if request.user.is_superuser:
            target = next_url if (next_url and not next_url.startswith('/login')) else 'admin_dashboard'
            return redirect(target)
        else:
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('home')

    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        if email_or_username:
            email_or_username = email_or_username.strip()
            
        password = request.POST.get('password')

        # Try case-insensitive email first
        user_obj = User.objects.filter(email__iexact=email_or_username).first()
        if not user_obj:
            # Then try username (username is usually case-sensitive in Django, but we'll try for compatibility)
            user_obj = User.objects.filter(username=email_or_username).first()

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    target = next_url if (next_url and not next_url.startswith('/login')) else 'admin_dashboard'
                    return redirect(target)
                else:
                    messages.error(request, "Access denied. This portal is for administrators only.")
            else:
                messages.error(request, "Invalid credentials.")
        else:
            messages.error(request, "No administrator account found with this email.")

    return render(request, 'pages/admin_login.html', {'next': next_url})

# Admin Booking Management Views
@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_bookings_manage(request):
    """View for superusers to manage all bookings."""
    from .models import Booking
    status_filter = request.GET.get('status', 'needs_attention')

    # Auto-complete any due bookings
    complete_due_bookings()
    
    bookings = Booking.objects.all().order_by('-booking_date', '-start_time')
    
    if status_filter == 'needs_attention':
        # Show both types of cancellations that might need reassignment
        bookings = bookings.filter(status__in=['cancelled', 'cancelled_by_purohit'])
    elif status_filter:
        bookings = bookings.filter(status=status_filter)
        
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES
    }
    return render(request, 'pages/admin_bookings_manage.html', context)

@user_passes_test(lambda u: u.is_superuser, login_url='admin_login')
def admin_reassign_booking(request, booking_id):
    """View to re-assign a cancelled or slot-vacated booking to a new priest."""
    booking = get_object_or_404(Booking, pk=booking_id)

    # Determine which slot is being reassigned
    target_role = request.GET.get('role') or request.POST.get('role')
    relation_id = request.GET.get('relation_id') or request.POST.get('relation_id')

    if not target_role:
        if booking.lead_priest_cancelled: target_role = 'lead'
        elif booking.extra_priest_cancelled: target_role = 'additional'
        else: target_role = 'lead'

    # Security/Logic Check: Is the slot actually available for reassignment?
    if target_role == 'lead' and not (booking.lead_priest_cancelled or booking.status == 'cancelled'):
         # If lead didn't cancel and booking isn't fully cancelled, maybe they shouldn't reassign lead?
         # But admin might want to swap. Let's allow if they explicitly ask, but prioritize needs.
         pass
    
    # Block reassignment for past dates
    today = timezone.localtime(timezone.now()).date()
    if booking.booking_date < today:
        messages.error(request, "Reassignment is blocked for past dates.")
        return render(request, 'pages/admin_reassign_booking.html', {'booking': booking, 'priests': []})

    # Find priests to exclude (currently assigned to ANY slot in this booking)
    excluded_ids = []
    
    # 1. Primary Priest
    if booking.priest:
        excluded_ids.append(booking.priest.pk)
    
    # 1. Primary Priest
    if booking.priest:
        excluded_ids.append(booking.priest.pk)
    
    # 2. All Through-model Additional Priests (Active ones)
    from .models import BookingAdditionalPriest
    active_extra_priests = list(BookingAdditionalPriest.objects.filter(
        booking=booking
    ).exclude(status='cancelled').values_list('priest_id', flat=True))
    excluded_ids.extend(active_extra_priests)

    # 4. If reassigning a specific extra slot, exclude the priest who just cancelled it
    if target_role == 'extra' and relation_id:
        try:
            rel_to_replace = BookingAdditionalPriest.objects.get(pk=relation_id)
            excluded_ids.append(rel_to_replace.priest.pk)
        except BookingAdditionalPriest.DoesNotExist:
            pass

    # Find candidate priests based on services
    priests = PriestProfile.objects.filter(services__contains=booking.service).exclude(pk__in=excluded_ids).distinct()
    available_priests = []
    for priest in priests:
        avail = PriestAvailability.objects.filter(priest=priest, date=booking.booking_date).first()
        if avail:
            # Check for scheduling conflicts in existing bookings
            has_conflict = Booking.objects.filter(
                Q(priest=priest) | Q(additional_priest_relationships__priest=priest),
                booking_date=booking.booking_date,
                status__in=['pending', 'confirmed'],
                start_time__lt=booking.end_time,
                end_time__gt=booking.start_time
            ).distinct().exists()
            if not has_conflict:
                available_priests.append(priest)

    if request.method == 'POST':
        new_priest_id = request.POST.get('priest_id')
        if new_priest_id:
            new_priest = get_object_or_404(PriestProfile, pk=new_priest_id)
            
            # Track old priest for availability restoration
            old_priest_obj = None
            if target_role == 'lead':
                old_priest_obj = booking.priest
            elif target_role == 'extra' and relation_id:
                rel = BookingAdditionalPriest.objects.filter(pk=relation_id).first()
                if rel: old_priest_obj = rel.priest

            old_priest_name = old_priest_obj.fullname if old_priest_obj else "Unknown"
            
            # Re-assign to the correct slot
            if target_role == 'lead':
                booking.priest = new_priest
                booking.lead_priest_cancelled = False
            elif target_role == 'extra' and relation_id:
                # Through-model reassignment
                rel = get_object_or_404(BookingAdditionalPriest, pk=relation_id)
                old_priest_name = rel.priest.fullname
                rel.priest = new_priest
                rel.status = 'pending'
                rel.save()
            
            # Reset status if it was cancelled
            if booking.status in ['cancelled', 'cancelled_by_purohit'] and target_role == 'lead':
                booking.status = 'pending'
            
            booking.save(skip_validation=True)

            # --- Availability Management during Reassignment ---
            try:
                # 1. Restore for old priest
                if old_priest_obj:
                    booking.restore_slot_availability(priest=old_priest_obj)
                
                # 2. Block for new priest
                booking.block_slot_availability(priest=new_priest)
            except Exception as ae:
                log_debug(f"Availability update failed during reassignment: {ae}")

            # Notify all parties
            try:
                admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
                
                if target_role == 'lead':
                    role_label = "Lead Purohit"
                elif target_role == 'extra':
                    role_label = "Additional Purohit"
                else:
                    role_label = "Purohit"

                # 1. To Devotee
                send_mail(
                    'Update: A New Purohit Has Been Assigned',
                    f"Namaste {booking.devotee_name},\n\n"
                    f"A new {role_label} has been assigned to your booking for '{booking.service}'.\n\n"
                    f"New Purohit: {new_priest.fullname}\n"
                    f"Date: {booking.booking_date}\n\n"
                    f"The new Purohit will confirm shortly. Check your dashboard for updates.\n\n"
                    f"Regards,\nKarya Siddhi Team",
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.devotee.email],
                    fail_silently=True,
                )

                # 2. To New Priest
                send_mail(
                    f'New Assignment: {booking.service} — Booking #{booking.id}',
                    f"Hello {new_priest.fullname},\n\n"
                    f"You have been assigned as {role_label} for Booking #{booking.id}.\n\n"
                    f"Details:\n"
                    f"- Devotee: {booking.devotee_name}\n"
                    f"- Date: {booking.booking_date} at {format_time_display(booking.start_time)}\n\n"
                    f"Please log in to your dashboard to confirm.\n\n"
                    f"Regards,\nKarya Siddhi Team",
                    settings.DEFAULT_FROM_EMAIL,
                    [new_priest.user.email],
                    fail_silently=True,
                )

                # 3. To Existing Priest(s) - Notify all other active partners
                active_partners = []
                
                # Check primary priest (if not the one we just assigned)
                if booking.priest and booking.priest != new_priest and not (target_role == 'lead'):
                    active_partners.append(booking.priest)
                
                # Check all other additional priests (through-model)
                for partner_priest in booking.get_active_additional_priests:
                    if partner_priest != new_priest:
                        active_partners.append(partner_priest)

                # Send individual notification to each active partner
                for partner in list(set(active_partners)): # Deduplicate just in case
                    send_mail(
                        f'Update for Booking #{booking.id} — New Partner Assigned',
                        f"Hello {partner.fullname},\n\n"
                        f"The slot for {role_label} in Booking #{booking.id} has been filled by {new_priest.fullname}.\n\n"
                        f"You will be working together for this Puja.\n\n"
                        f"Regards,\nKarya Siddhi Team",
                        settings.DEFAULT_FROM_EMAIL,
                        [partner.user.email],
                        fail_silently=True,
                    )
            except Exception as e:
                log_debug(f"Error sending multi-slot reassignment emails for Booking #{booking.id}: {e}")

            messages.success(request, f"Successfully re-assigned {role_label} to {new_priest.fullname}.")
            return redirect('admin_bookings_manage')

    # Determine the display label for the role
    role_label = "Lead Purohit"
    if target_role == 'additional':
        role_label = "Additional Purohit (Legacy)"
    elif target_role == 'extra':
        role_label = "Additional Purohit"

    # For 'extra' role, find the specific cancelled relationship
    cancelled_rel = None
    if target_role == 'extra' and relation_id:
        try:
            cancelled_rel = BookingAdditionalPriest.objects.get(pk=relation_id)
        except BookingAdditionalPriest.DoesNotExist:
            pass

    context = {
        'booking': booking,
        'priests': available_priests,
        'target_role': target_role,
        'relation_id': relation_id,
        'role_label': role_label,
        'cancelled_rel': cancelled_rel,
        'old_priest_obj': cancelled_rel.priest if cancelled_rel else (booking.priest if target_role == 'lead' else None)
    }
    return render(request, 'pages/admin_reassign_booking.html', context)

def blog_detail(request, blog_slug):
    """Render the detailed page for a specific blog."""
    blog = get_object_or_404(Blog, slug=blog_slug)
    recent_blogs = Blog.objects.exclude(id=blog.id).order_by('-date', '-created_at')[:3]
    
    context = {
        'blog': blog,
        'blog_slug': blog_slug,
        'recent_blogs': recent_blogs
    }
    return render(request, 'pages/blog_detail.html', context)


@login_required
def generate_booking_pdf(request, booking_id):
    """Generates a role-specific booking confirmation PDF."""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security: Only allow Devotee or Priest of this booking to download
    is_devotee = (request.user == booking.devotee)
    # Check if priest profile exists and matches
    is_priest = False
    if hasattr(request.user, 'priest_profile') and booking.priest == request.user.priest_profile:
        is_priest = True
        
    if not (is_devotee or is_priest):
        messages.error(request, "You do not have permission to download this document.")
        return redirect('home')
    
    # PDF is only for confirmed, in-progress or completed bookings
    if booking.status not in ['confirmed', 'completed']:
        messages.error(request, "Confirmation PDF is only available for confirmed services.")
        if is_priest:
            return redirect('priest_bookings')
        return redirect('my_bookings')

    # Get proper service name from DB
    service_name = get_service_title(booking.service)

    template_path = 'core/pdf_booking.html'
    context = {
        'booking': booking,
        'service_name': service_name,
        'is_priest_view': is_priest,
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="KaryaSiddhi_Booking_{booking.id}.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    # Render PDF
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error generating PDF document', status=500)
        
    return response

def feedback_form(request, token):
    """Secure one-time feedback form for devotees."""
    feedback = get_object_or_404(BookingFeedback, token=token)
    booking = feedback.booking
    
    if request.method == 'POST' and not feedback.is_submitted:
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        
        if rating:
            feedback.rating = int(rating)
            feedback.comments = comments
            feedback.is_submitted = True
            feedback.submitted_at = timezone.now()
            feedback.save()
            
            # Send Emails
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@karyasiddhi.com')
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@karyasiddhi.com')
            service_title = booking.service
            
            # Prepare priest names
            extra_names = ', '.join(ap.priest.fullname for ap in booking.get_active_additional_priests())
            priest_info = f"Lead Priest: {booking.priest.fullname}"
            if extra_names:
                priest_info += f"\nAdditional Priest(s): {extra_names}"

            # 1. Devotee Confirmation
            try:
                send_mail(
                    'Feedback Received – Karya Siddhi',
                    f"Namaste {booking.devotee_name},\n\n"
                    "Thank you for sharing your feedback with us. It helps us maintain the highest standards for our spiritual services.\n\n"
                    f"Ritual: {service_title}\n"
                    f"{priest_info}\n"
                    f"Rating: {feedback.rating}/5\n"
                    f"Comments: {feedback.comments or 'None'}\n\n"
                    "Regards,\nKarya Siddhi Team",
                    from_email,
                    [booking.devotee.email],
                    fail_silently=True
                )
            except: pass

            # 2. Admin Notification
            try:
                send_mail(
                    f'New Feedback Received - Booking #{booking.id}',
                    f"New survey submission for Booking #{booking.id}\n\n"
                    f"Devotee: {booking.devotee_name} ({booking.devotee.email})\n"
                    f"Ritual: {service_title}\n"
                    f"{priest_info}\n"
                    f"Rating: {feedback.rating}/5\n"
                    f"Comments: {feedback.comments or 'None'}\n\n"
                    f"Date: {booking.booking_date}\n",
                    from_email,
                    [admin_email],
                    fail_silently=True
                )
            except: pass

            messages.success(request, "Thank you for your feedback!")
            return redirect('feedback_form', token=token)

    return render(request, 'pages/feedback_form.html', {
        'feedback': feedback,
        'booking': booking,
        'is_read_only': feedback.is_submitted
    })
@login_required
def raise_enquiry(request):
    """Allows devotees to raise an enquiry for a completed booking within a 24h window."""
    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        category_id = request.POST.get('category')
        message = request.POST.get('message')
        
        booking = get_object_or_404(Booking, id=booking_id, devotee=request.user)
        
        # Check if enquiry is allowed via model property (24h rule + status + flag)
        if not booking.can_raise_enquiry:
            if booking.status != 'completed':
                messages.error(request, "Enquiries can only be raised for completed bookings.")
            elif booking.enquiry_raised:
                messages.warning(request, "An enquiry has already been raised for this booking.")
            else:
                messages.error(request, "The 24-hour enquiry window for this ritual has expired.")
            return redirect('my_bookings')
            
        if message:
            category = None
            if category_id:
                category = EnquiryCategory.objects.filter(id=category_id, is_active=True).first()
            if not category:
                messages.error(request, "Please select a valid enquiry category.")
                return redirect('my_bookings')

            # Create the enquiry
            BookingEnquiry.objects.create(booking=booking, category=category, message=message)
            booking.enquiry_raised = True
            booking.save(update_fields=['enquiry_raised'])

            # --- Internal Notification for Admins ---
            from .models import Notification
            admin_users = User.objects.filter(is_superuser=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    title='New Enquiry Raised',
                    message=f"A new enquiry has been raised for booking #{booking.id} by {booking.devotee_name}.",
                    notification_type='enquiry_new'
                )
            
            # --- Email Notifications ---
            try:
                service_title = get_service_title(booking.service)
                admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
                
                # Clerk/Priest details
                priest_info = f"Lead Purohit: {booking.priest.fullname}"
                extra_priests = booking.get_active_additional_priests()
                if extra_priests:
                    extra_names = ", ".join([p.fullname for p in extra_priests])
                    priest_info += f"\nAdditional Purohit(s): {extra_names}"

                # 1. Admin Email (Full Details)
                admin_body = (
                    f"A devotee has raised a new enquiry for a completed ritual.\n\n"
                    f"--- Booking Details ---\n"
                    f"Booking ID: #{booking.id}\n"
                    f"Ritual: {service_title}\n"
                    f"Date: {booking.booking_date}\n"
                    f"Time Slot: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}\n\n"
                    f"--- Devotee Details ---\n"
                    f"Name: {booking.devotee_name}\n"
                    f"Phone: {booking.devotee_phone}\n"
                    f"Email: {booking.devotee.email}\n"
                    f"Gothram: {booking.gothram or 'N/A'}\n\n"
                    f"--- Assigned Purohits ---\n"
                    f"{priest_info}\n\n"
                    f"--- Enquiry Details ---\n"
                    f"Category: {category.name}\n"
                    f"Message: \"{message}\"\n\n"
                    f"Please review this request in the admin dashboard and follow up with the devotee."
                )

                send_mail(
                    f'[ADMIN] New Ritual Enquiry: {booking.devotee_name} (ID #{booking.id})',
                    admin_body,
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails,
                    fail_silently=True
                )

                # 2. Devotee Confirmation Email
                devotee_body = (
                    f"Namaste {booking.devotee_name},\n\n"
                    f"We have received your enquiry regarding the ritual '{service_title}' (Booking ID #{booking.id}) performed on {booking.booking_date}.\n\n"
                    f"Our administrative team is reviewing your message:\n"
                    f"\"{message}\"\n\n"
                    f"We will get back to you within 24-48 hours.\n\n"
                    f"Regards,\n"
                    f"Karya Siddhi Administrative Team"
                )
                
                send_mail(
                    f'Enquiry Received: {service_title} (ID #{booking.id})',
                    devotee_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [booking.devotee.email],
                    fail_silently=True
                )

            except Exception as e:
                log_debug(f"Failed to send enquiry emails for Booking #{booking.id}: {e}")

            messages.success(request, "Your enquiry has been submitted. Our team will contact you soon.")
        else:
            messages.error(request, "Please provide a message for your enquiry.")
            
    return redirect('my_bookings')


@login_required
def get_notifications(request):
    """Fetch recent notifications for the user."""
    from .models import Notification
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'includes/notifications_list.html', {'notifications': notifications})

@login_required
@api_view(['POST'])
def mark_all_notifications_read(request):
    """Mark all unread notifications for the user as read."""
    from .models import Notification
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    # Return empty partial if using HTMX to update the bell area or just success
    if request.headers.get('HX-Request'):
        return render(request, 'includes/notification_bell_area.html')
    return JsonResponse({'status': 'success'})
