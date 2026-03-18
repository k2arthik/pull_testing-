from django.contrib import admin
from django.utils.html import format_html
from .models import (
    PriestProfile, PriestAvailability, Booking, Photo, Video, Blog,
    Puja, PujaCategory, BookingEnquiry, EnquiryCategory, PujaGalleryImage,
    HomeHeroConfig, SpiritualJourneyStep, SankalpPillar, Testimonial, HomeAboutConfig,
    SEOMetadata, Notification, PriestPerformance, DevoteeProfile
)
admin.site.site_header = "Karya Siddhi Admin"
admin.site.site_title = "Karya Siddhi Admin Portal"
admin.site.index_title = "Welcome to Karya Siddhi Administration"
@admin.register(PriestProfile)
class PriestProfileAdmin(admin.ModelAdmin):
    """Custom admin for PriestProfile with proper service display."""
    
    list_display = ['fullname', 'user', 'mobile', 'experience', 'location', 'get_services_display', 'photo_preview', 'certificate_preview', 'id_proof_preview', 'created_at']
    list_filter = ['experience', 'created_at']
    search_fields = ['fullname', 'mobile', 'user__email', 'location']
    readonly_fields = ['created_at', 'get_services_display', 'photo_preview', 'certificate_preview', 'id_proof_preview']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'fullname', 'mobile')
        }),
        ('Professional Details', {
            'fields': ('experience', 'language', 'location', 'specialization')
        }),
        ('Services', {
            'fields': ('services', 'get_services_display'),
            'description': 'Services are stored as slugs but displayed as readable titles below.'
        }),
        ('Documents', {
            'fields': ('photo', 'photo_preview', 'certificate', 'certificate_preview', 'id_proof', 'id_proof_preview')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
    
    def get_services_display(self, obj):
        """Convert service slugs to readable titles for display."""
        if not obj.services:
            return "No services selected"
        
        pretty_services = []
        for slug in obj.services:
            service_title = Puja.objects.filter(slug=slug).values_list('title', flat=True).first()
            if service_title:
                pretty_services.append(service_title)
            else:
                pretty_services.append(slug.replace('-', ' ').title())
        
        return ", ".join(pretty_services)
    
    get_services_display.short_description = 'Offered Services'

    def photo_preview(self, obj):
        """Show photo thumbnail in admin."""
        print(f"DEBUG: photo for {obj.fullname}: {obj.photo}, url: {obj.photo.url if obj.photo else 'None'}")
        if obj.photo:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height:80px;width:80px;object-fit:cover;border-radius:6px;"/>'
                '</a>',
                obj.photo.url, obj.photo.url
            )
        return '(No photo)'
    photo_preview.short_description = 'Photo Preview'

    def certificate_preview(self, obj):
        """Show a clickable link for the Vedic certificate."""
        if obj.certificate and hasattr(obj.certificate, 'url'):
            return format_html(
                '<a href="{}" target="_blank" style="color:#2563eb;font-weight:bold;">'
                '📄 View / Download Certificate</a>',
                obj.certificate.url
            )
        return format_html('<span style="color:#999;">(No certificate)</span>')
    certificate_preview.short_description = 'Certificate Preview'

    def id_proof_preview(self, obj):
        """Show a clickable link for the ID proof."""
        if obj.id_proof and hasattr(obj.id_proof, 'url'):
            return format_html(
                '<a href="{}" target="_blank" style="color:#2563eb;font-weight:bold;">'
                '🪪 View / Download ID Proof</a>',
                obj.id_proof.url
            )
        return format_html('<span style="color:#999;">(No ID proof)</span>')
    id_proof_preview.short_description = 'ID Proof Preview'

@admin.register(DevoteeProfile)
class DevoteeProfileAdmin(admin.ModelAdmin):
    """Custom admin for DevoteeProfile."""
    list_display = ['fullname', 'user', 'mobile', 'created_at']
    search_fields = ['fullname', 'mobile', 'user__email']
    list_filter = ['created_at']
    readonly_fields = ['created_at']


@admin.register(PriestAvailability)
class PriestAvailabilityAdmin(admin.ModelAdmin):
    """Custom admin for PriestAvailability."""
    
    list_display = ['priest', 'date', 'get_available_slots', 'created_at']
    list_filter = ['date', 'morning_available', 'afternoon_available', 'evening_available']
    search_fields = ['priest__fullname', 'notes']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('priest', 'date', 'notes')
        }),
        ('Morning Slot', {
            'fields': ('morning_available', 'morning_start', 'morning_end')
        }),
        ('Afternoon Slot', {
            'fields': ('afternoon_available', 'afternoon_start', 'afternoon_end')
        }),
        ('Evening Slot', {
            'fields': ('evening_available', 'evening_start', 'evening_end')
        }),
        ('Custom Slots', {
            'fields': ('custom_slots',),
            'description': 'Add custom time slots as JSON: [{"start": "14:00", "end": "16:00", "label": "Special"}]'
        }),
    )
    
    def get_available_slots(self, obj):
        """Display which slots are available."""
        slots = []
        if obj.morning_available:
            slots.append('Morning')
        if obj.afternoon_available:
            slots.append('Afternoon')
        if obj.evening_available:
            slots.append('Evening')
        if obj.custom_slots:
            slots.append(f'{len(obj.custom_slots)} Custom')
        return ', '.join(slots) if slots else 'No slots'
    
    get_available_slots.short_description = 'Available Slots'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Custom admin for Booking."""
    
    list_display = ['devotee_name', 'priest', 'service_title', 'booking_date', 'slot_type', 'status', 'created_at']
    list_filter = ['status', 'slot_type', 'booking_date', 'created_at']
    search_fields = ['devotee_name', 'devotee_phone', 'priest__fullname', 'service']
    date_hierarchy = 'booking_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('priest', 'devotee', 'service', 'status')
        }),
        ('Date & Time', {
            'fields': ('booking_date', 'slot_type', 'start_time', 'end_time')
        }),
        ('Devotee Details', {
            'fields': ('devotee_name', 'devotee_phone', 'devotee_address')
        }),
        ('Additional Information', {
            'fields': ('special_requests',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    def service_title(self, obj):
        title = Puja.objects.filter(slug=obj.service).values_list('title', flat=True).first()
        return title or obj.service
    service_title.short_description = 'Service'
    
    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = 'Mark selected bookings as Confirmed'
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = 'Mark selected bookings as Completed'
    
    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = 'Mark selected bookings as Cancelled'

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'photo_preview', 'created_at']
    readonly_fields = ['photo_preview']

    def photo_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;width:50px;object-fit:cover;"/>', obj.image.url)
        return "No Image"
    photo_preview.short_description = 'Preview'

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'video_type', 'created_at']

    def video_type(self, obj):
        if obj.video_file:
            return "Local File"
        if obj.youtube_iframe:
            return "YouTube Embed"
        return "N/A"
    video_type.short_description = 'Type'

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'category', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', 'excerpt')
    list_filter = ('category', 'date')

@admin.register(PujaCategory)
class PujaCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')

class PujaGalleryImageInline(admin.TabularInline):
    model = PujaGalleryImage
    extra = 1
    fields = ('image', 'alt_text', 'display_order', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;width:50px;object-fit:cover;border-radius:4px;"/>', obj.image.url)
        return "No Image"

@admin.register(Puja)
class PujaAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'category', 'is_featured', 'display_order', 'is_active')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('title', 'slug', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('display_order', 'title')
    inlines = [PujaGalleryImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'short_description', 'display_order', 'is_active', 'is_featured')
        }),
        ('Detailed Content', {
            'fields': ('full_description', 'page_description', 'benefits', 'inclusions'),
            'description': "Use 'Benefits' and 'Inclusions' boxes to enter items, one per line."
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
        }),
        ('Puja Specifications', {
            'fields': ('duration', 'price', 'pandits', 'location', 'deity', 'required_purohits'),
        }),
    )
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:100px;width:100px;object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return "No Image"


@admin.register(EnquiryCategory)
class EnquiryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')

@admin.register(BookingEnquiry)
class BookingEnquiryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('booking__devotee_name', 'booking__devotee_phone', 'message')

@admin.register(HomeHeroConfig)
class HomeHeroConfigAdmin(admin.ModelAdmin):
    list_display = ['title_gold', 'updated_at', 'is_active']
    fieldsets = (
        ('Text Content', {
            'fields': ('title_gold', 'title_ivory', 'subtitle', 'quote_text', 'watermark_text')
        }),
        ('Background Images', {
            'fields': ('hero_bg_1', 'hero_bg_2', 'hero_bg_3')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(SpiritualJourneyStep)
class SpiritualJourneyStepAdmin(admin.ModelAdmin):
    list_display = ['step_number', 'title', 'display_order']
    list_editable = ['display_order']

@admin.register(SankalpPillar)
class SankalpPillarAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'display_order']
    list_editable = ['display_order']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    search_fields = ['name', 'location', 'text']

@admin.register(HomeAboutConfig)
class HomeAboutConfigAdmin(admin.ModelAdmin):
    list_display = ['title', 'updated_at']

    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(SEOMetadata)
class SEOMetadataAdmin(admin.ModelAdmin):
    list_display = ('path', 'title_tag', 'updated_at')
    search_fields = ('path', 'title_tag', 'keywords')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')

@admin.register(PriestPerformance)
class PriestPerformanceAdmin(admin.ModelAdmin):
    list_display = ('priest', 'total_assigned', 'completed_successful', 'rejected_count', 'rating')
    readonly_fields = ('rating',)
    search_fields = ('priest__fullname',)
