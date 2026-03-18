from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone
from .models import (
    Puja, DevoteeProfile, PriestProfile, Booking, 
    SEOMetadata, BookingEnquiry, PriestPerformance
)
from .forms import (
    PujaForm, AdminDevoteeEditForm, AdminPurohitEditForm, 
    SEOMetadataForm
)

def is_admin(user):
    return user.is_authenticated and user.is_superuser

# ─── Admin Dashboard Overview ──────────────────────────────────────────────
@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard_overview(request):
    total_bookings = Booking.objects.count()
    total_devotees = DevoteeProfile.objects.count()
    total_revenue = Booking.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_enquiries = BookingEnquiry.objects.count() # Or filter by active if there was a status
    
    recent_bookings = Booking.objects.all().order_by('-created_at')[:10]
    top_priests = PriestPerformance.objects.all().order_by('-rating', '-completed_successful')[:5]
    
    # Map booking.service (slug) to readable title for the template
    for booking in recent_bookings:
        puja = Puja.objects.filter(slug=booking.service).first()
        booking.service_name = puja.title if puja else booking.service

    context = {
        'total_bookings': total_bookings,
        'total_devotees': total_devotees,
        'total_revenue': total_revenue,
        'pending_enquiries': pending_enquiries,
        'recent_bookings': recent_bookings,
        'top_priests': top_priests,
    }
    return render(request, 'dashboard/admin_overview.html', context)

# ─── Puja Management ────────────────────────────────────────────────────────
@user_passes_test(is_admin, login_url='admin_login')
def admin_puja_list(request):
    pujas = Puja.objects.all().order_by('display_order', 'title')
    return render(request, 'dashboard/puja_list.html', {'pujas': pujas})

@user_passes_test(is_admin, login_url='admin_login')
def admin_puja_edit(request, slug=None):
    instance = get_object_or_404(Puja, slug=slug) if slug else None
    if request.method == 'POST':
        form = PujaForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"Puja service {'updated' if instance else 'created'} successfully.")
            return redirect('admin_puja_list')
    else:
        form = PujaForm(instance=instance)
    
    return render(request, 'dashboard/puja_form.html', {'form': form, 'instance': instance})

@user_passes_test(is_admin, login_url='admin_login')
def admin_puja_delete(request, slug):
    puja = get_object_or_404(Puja, slug=slug)
    puja.delete()
    messages.success(request, "Puja service deleted successfully.")
    return redirect('admin_puja_list')

# ─── Devotee Management ──────────────────────────────────────────────────────
@user_passes_test(is_admin, login_url='admin_login')
def admin_devotee_list(request):
    devotees = DevoteeProfile.objects.all().order_by('-created_at')
    return render(request, 'dashboard/devotee_list.html', {'devotees': devotees})

@user_passes_test(is_admin, login_url='admin_login')
def admin_devotee_edit(request, user_id):
    profile = get_object_or_404(DevoteeProfile, user_id=user_id)
    if request.method == 'POST':
        form = AdminDevoteeEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Devotee profile updated successfully.")
            return redirect('admin_devotee_list')
    else:
        form = AdminDevoteeEditForm(instance=profile)
    
    return render(request, 'dashboard/user_form.html', {
        'form': form, 
        'user_obj': profile, 
        'user_type': 'Devotee'
    })

@user_passes_test(is_admin, login_url='admin_login')
def admin_devotee_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "Devotee account deleted successfully.")
    return redirect('admin_devotee_list')

# ─── Purohit Management ──────────────────────────────────────────────────────
@user_passes_test(is_admin, login_url='admin_login')
def admin_purohit_list(request):
    purohits = PriestProfile.objects.all().order_by('-created_at')
    return render(request, 'dashboard/purohit_list.html', {'purohits': purohits})

@user_passes_test(is_admin, login_url='admin_login')
def admin_purohit_edit(request, user_id):
    profile = get_object_or_404(PriestProfile, user_id=user_id)
    if request.method == 'POST':
        form = AdminPurohitEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Purohit profile updated successfully.")
            return redirect('admin_purohit_list')
    else:
        form = AdminPurohitEditForm(instance=profile)
    
    return render(request, 'dashboard/user_form.html', {
        'form': form, 
        'user_obj': profile, 
        'user_type': 'Purohit'
    })

@user_passes_test(is_admin, login_url='admin_login')
def admin_purohit_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "Purohit account deleted successfully.")
    return redirect('admin_purohit_list')

# ─── SEO Management ──────────────────────────────────────────────────────────
@user_passes_test(is_admin, login_url='admin_login')
def admin_seo_list(request):
    seo_records = SEOMetadata.objects.all().order_by('path')
    return render(request, 'dashboard/seo_list.html', {'seo_records': seo_records})

@user_passes_test(is_admin, login_url='admin_login')
def admin_seo_edit(request, seo_id=None):
    instance = get_object_or_404(SEOMetadata, id=seo_id) if seo_id else None
    if request.method == 'POST':
        form = SEOMetadataForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f"SEO record {'updated' if instance else 'created'} successfully.")
            return redirect('admin_seo_list')
    else:
        form = SEOMetadataForm(instance=instance)
    
    return render(request, 'dashboard/seo_form.html', {'form': form, 'instance': instance})

@user_passes_test(is_admin, login_url='admin_login')
def admin_seo_delete(request, seo_id):
    seo = get_object_or_404(SEOMetadata, id=seo_id)
    seo.delete()
    messages.success(request, "SEO record deleted successfully.")
    return redirect('admin_seo_list')

# ─── Inquiry Management ──────────────────────────────────────────────────────
@user_passes_test(is_admin, login_url='admin_login')
def admin_inquiry_list(request):
    inquiries = BookingEnquiry.objects.all().order_by('-created_at')
    return render(request, 'dashboard/inquiry_list.html', {'inquiries': inquiries})
