from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.text import slugify
from datetime import datetime, timedelta, time

from django.db.models.signals import post_save
from django.dispatch import receiver

def validate_mobile(value):
    if not value.isdigit():
        raise ValidationError("Mobile number must contain only digits.")
    if len(value) != 10:
        raise ValidationError("Mobile number must be exactly 10 digits.")

def validate_hyderabad(value):
    if not value:
        return
    if "hyderabad" not in value.strip().lower():
        raise ValidationError("Service location must be in Hyderabad only.")

class PriestProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='priest_profile')
    fullname = models.CharField(max_length=255)
    
    mobile = models.CharField(max_length=10, validators=[validate_mobile])
    
    experience = models.IntegerField()
    language = models.JSONField(default=list)
    
    location = models.TextField(validators=[validate_hyderabad])
    specialization = models.CharField(max_length=255, blank=True, null=True)
    
    # New Fields
    gothram = models.TextField(default="")
    qualification = models.TextField(default="", help_text="Highest Educational Qualification")
    qualification_place = models.TextField(default="", help_text="Gurukulam / Vedic Institution")
    
    formal_vedic_training = models.BooleanField(default=False, help_text="Have you formally undergone Vedic training?")
    knows_smaardham = models.BooleanField(default=False, help_text="Have you know of the Veda called Smaardham?")
    organize_scientifically = models.BooleanField(default=False, help_text="Can you organize the program scientifically?")
    
    can_perform_rituals = models.BooleanField(default=True, help_text="Can perform as per scriptures?")
    
    photo = models.ImageField(upload_to='priest_photos/', blank=True, null=True)
    certificate = models.FileField(upload_to='priest_certificates/', blank=True, null=True)
    id_proof = models.FileField(upload_to='priest_id_proofs/', blank=True, null=True)
    services = models.JSONField(default=list)  # Storing selected services as a list
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname
    
    def clean(self):
        # Existing validation could go here, but validators=[] handles it mostly.
        # We call it explicitly to be sure and for consistent implementation.
        validate_hyderabad(self.location)
        super().clean()

class DevoteeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='devotee_profile')
    fullname = models.CharField(max_length=255)
    mobile = models.CharField(max_length=10, validators=[validate_mobile])
    address = models.TextField(default="", validators=[validate_hyderabad])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname

    def clean(self):
        validate_hyderabad(self.address)
        super().clean()


class PriestAvailability(models.Model):
    """Manages priest availability for specific dates and time slots."""
    priest = models.ForeignKey(PriestProfile, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    
    # Time slot availability flags
    morning_available = models.BooleanField(default=False)
    morning_start = models.TimeField(null=True, blank=True, help_text="Morning slot start time (e.g., 06:00)")
    morning_end = models.TimeField(null=True, blank=True, help_text="Morning slot end time (e.g., 12:00)")
    
    afternoon_available = models.BooleanField(default=False)
    afternoon_start = models.TimeField(null=True, blank=True, help_text="Afternoon slot start time (e.g., 12:00)")
    afternoon_end = models.TimeField(null=True, blank=True, help_text="Afternoon slot end time (e.g., 18:00)")
    
    evening_available = models.BooleanField(default=False)
    evening_start = models.TimeField(null=True, blank=True, help_text="Evening slot start time (e.g., 18:00)")
    evening_end = models.TimeField(null=True, blank=True, help_text="Evening slot end time (e.g., 21:00)")
    
    # Custom time slots stored as JSON: [{"start": "14:00", "end": "16:00", "label": "Special Pooja"}, ...]
    custom_slots = models.JSONField(default=list, blank=True)
    
    notes = models.TextField(blank=True, help_text="Any special notes or instructions for this date")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['priest', 'date']
        ordering = ['date']
        verbose_name_plural = 'Priest Availabilities'
    
    def __str__(self):
        return f"{self.priest.fullname} - {self.date}"
    
    @property
    def is_morning_visible(self):
        """Check if morning slot should be visible."""
        if not self.morning_available or not self.morning_start: return False
        now = timezone.now()
        slot_dt = timezone.make_aware(datetime.combine(self.date, self.morning_start))
        return slot_dt >= now

    @property
    def is_afternoon_visible(self):
        """Check if afternoon slot should be visible."""
        if not self.afternoon_available or not self.afternoon_start: return False
        now = timezone.now()
        slot_dt = timezone.make_aware(datetime.combine(self.date, self.afternoon_start))
        return slot_dt >= now

    @property
    def is_evening_visible(self):
        """Check if evening slot should be visible."""
        if not self.evening_available or not self.evening_start: return False
        now = timezone.now()
        slot_dt = timezone.make_aware(datetime.combine(self.date, self.evening_start))
        return slot_dt >= now

    @property
    def has_visible_slots(self):
        """Check if any slot is available and visible on this date."""
        return any([self.is_morning_visible, self.is_afternoon_visible, self.is_evening_visible])
    
    @property
    def has_slots(self):
        """Check if any slot is available on this date (regardless of time)."""
        return any([self.morning_available, self.afternoon_available, self.evening_available])
    
    def clean(self):
        """Validate that availability slots are not in the past."""
        now = timezone.now()
        
        if self.date:
            # Past dates are never allowed
            if self.date < now.date():
                raise ValidationError("Availability cannot be set for past dates.")
            
            # Check standard slots
            slots = [
                ('Morning', self.morning_available, self.morning_start),
                ('Afternoon', self.afternoon_available, self.afternoon_start),
                ('Evening', self.evening_available, self.evening_start),
            ]
            
            for name, available, start_time in slots:
                if available and start_time:
                    slot_datetime = timezone.make_aware(datetime.combine(self.date, start_time))
                    if slot_datetime < now:
                        raise ValidationError(f"The {name} slot on {self.date} at {start_time} is in the past.")
            
            # Check custom slots
            if self.custom_slots and isinstance(self.custom_slots, list):
                for i, slot in enumerate(self.custom_slots):
                    try:
                        start_str = slot.get('start')
                        if start_str:
                            c_start = datetime.strptime(start_str, "%H:%M").time()
                            c_datetime = timezone.make_aware(datetime.combine(self.date, c_start))
                            if c_datetime < now:
                                raise ValidationError(f"Custom slot {i+1} starting at {start_str} is in the past.")
                    except (ValueError, TypeError):
                        pass

        # Basic time validation
        if self.morning_available and (not self.morning_start or not self.morning_end):
            raise ValidationError("Morning slot requires both start and end times.")
        if self.morning_start and self.morning_end and self.morning_start >= self.morning_end:
            raise ValidationError("Morning start time must be before end time.")
            
        if self.afternoon_available and (not self.afternoon_start or not self.afternoon_end):
            raise ValidationError("Afternoon slot requires both start and end times.")
        if self.afternoon_start and self.afternoon_end and self.afternoon_start >= self.afternoon_end:
            raise ValidationError("Afternoon start time must be before end time.")
            
        if self.evening_available and (not self.evening_start or not self.evening_end):
            raise ValidationError("Evening slot requires both start and end times.")
        if self.evening_start and self.evening_end and self.evening_start >= self.evening_end:
            raise ValidationError("Evening start time must be before end time.")


class Booking(models.Model):
    """Manages bookings made by devotees for priest services."""
    STATUS_CHOICES = [
        ('pending_payment', 'Pending Payment'),
        ('pending', 'Pending Confirmation'),
        ('payment_completed', 'Payment Completed'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('cancelled_by_purohit', 'Cancelled by Purohit'),
    ]
    
    SLOT_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('custom', 'Custom Time'),
    ]
    
    # Core booking information
    priest = models.ForeignKey(PriestProfile, on_delete=models.CASCADE, related_name='bookings')
    additional_priest = models.ForeignKey(PriestProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='additional_bookings')
    devotee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.CharField(max_length=100, help_text="Service slug from Puja table")
    
    # Date and time
    booking_date = models.DateField()
    slot_type = models.CharField(max_length=20, choices=SLOT_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    lead_priest_cancelled = models.BooleanField(default=False)
    extra_priest_cancelled = models.BooleanField(default=False)
    
    # Devotee contact details
    devotee_name = models.CharField(max_length=255)
    devotee_phone = models.CharField(max_length=15)
    devotee_address = models.TextField(validators=[validate_hyderabad])
    gothram = models.CharField(max_length=100, blank=True, null=True)
    nakshatram = models.CharField(max_length=100, blank=True, null=True)
    # Payment
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Service amount in rupees")
     
    # Additional information
    special_requests = models.TextField(blank=True, help_text="Any special requirements or requests")
    enquiry_raised = models.BooleanField(default=False, help_text="True if devotee has raised an enquiry")
    puja_completed_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when status was set to completed")
    
    # Refund tracking
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_status = models.CharField(max_length=20, default='none', choices=[
        ('none', 'No Refund'),
        ('pending', 'Refund Pending'),
        ('initiated', 'Refund Initiated'),
        ('completed', 'Refund Completed'),
        ('failed', 'Refund Failed'),
    ])
    refund_initiated_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def can_raise_enquiry(self):
        """Check if devotee can raise an enquiry (Completed status, <24h ago, not already raised)."""
        if self.status != 'completed' or self.enquiry_raised:
            return False
        
        # Determine completion reference time
        ref_time = self.puja_completed_at
        if not ref_time:
            # Fallback to booking_date + end_time if completed_at is missing
            ref_time = timezone.make_aware(datetime.combine(self.booking_date, self.end_time))
            
        return timezone.now() <= ref_time + timedelta(hours=24)

    class Meta:
        ordering = ['-booking_date', '-start_time']
        indexes = [
            models.Index(fields=['priest', 'booking_date', 'status']),
            models.Index(fields=['additional_priest', 'booking_date', 'status']),
            models.Index(fields=['devotee', 'status']),
        ]
    
    def __str__(self):
        return f"{self.devotee_name} - {self.priest.fullname} - {self.booking_date}"
    
    def clean(self):
        """Validate booking basic requirements (relaxed for flexibility)."""
        now = timezone.now()

        # Strict 48h advance booking rule
        if self.booking_date and self.start_time:
            booking_datetime = timezone.make_aware(datetime.combine(self.booking_date, self.start_time))
            if booking_datetime < now + timedelta(hours=48):
                raise ValidationError("Bookings must be made at least 48 hours in advance.")
        
        if self.devotee_address:
            validate_hyderabad(self.devotee_address)
        
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        
        # Overlapping checks removed to support Many-to-Many group bookings
        pass
    
    @property
    def get_active_additional_priests(self):
        """Retrieve all priests from the through-model that are NOT cancelled."""
        return [rel.priest for rel in self.additional_priest_relationships.exclude(status='cancelled').select_related('priest')]

    @property
    def can_cancel_extra(self):
        """Check if at least one additional priest can be cancelled."""
        if self.status not in ['pending', 'confirmed']:
            return False
        
        # Check if there are any active additional priests
        has_active = self.additional_priest_relationships.exclude(status='cancelled').exists()
        if not has_active:
            return False

        booking_datetime = timezone.make_aware(datetime.combine(self.booking_date, self.start_time))
        return booking_datetime >= timezone.now() + timedelta(hours=24)

    @property
    def can_purohit_cancel(self):
        """Check if the primary/lead priest can cancel a confirmed booking (at least 24h before)."""
        if self.status != 'confirmed':
            return False
        
        booking_datetime = timezone.make_aware(datetime.combine(self.booking_date, self.start_time))
        return booking_datetime >= timezone.now() + timedelta(hours=24)
    
    def block_slot_availability(self, priest=None):
        """Disable the priest's availability slot after a booking or reassignment."""
        target_priest = priest if priest else self.priest
        try:
            avail = PriestAvailability.objects.get(priest=target_priest, date=self.booking_date)
            slot = str(self.slot_type).lower()
            if 'morning' in slot:
                avail.morning_available = False
            elif 'afternoon' in slot:
                avail.afternoon_available = False
            elif 'evening' in slot:
                avail.evening_available = False
            avail.save()
        except PriestAvailability.DoesNotExist:
            pass

    def restore_slot_availability(self, priest=None):
        """Re-enable the priest's availability slot after a Devotee cancellation."""
        target_priest = priest if priest else self.priest
        try:
            avail = PriestAvailability.objects.get(priest=target_priest, date=self.booking_date)
            slot = str(self.slot_type).lower()
            if 'morning' in slot:
                avail.morning_available = True
            elif 'afternoon' in slot:
                avail.afternoon_available = True
            elif 'evening' in slot:
                avail.evening_available = True
            avail.save()
        except PriestAvailability.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        """Override save to run validation. Skip for status/completion-only updates."""
        skip_validation = kwargs.pop('skip_validation', False)
        if not skip_validation:
            self.full_clean()
        super().save(*args, **kwargs)

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Photo(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='photos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    youtube_iframe = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='blogs/')
    category = models.CharField(max_length=100, default='Spiritual')
    excerpt = models.TextField(help_text="Short summary of the blog post")
    content = RichTextUploadingField()
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date', '-created_at']
class PujaCategory(models.Model):
    """Category for grouping Puja services (e.g., Peace, Wealth, Protection)."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = "Puja Categories"

    def __str__(self):
        return self.name

class Puja(models.Model):
    """Represents a specific Puja/Service provided by the system."""
    slug = models.SlugField(max_length=100, unique=True, primary_key=True)
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        PujaCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pujas'
    )
    short_description = models.TextField(blank=True)
    full_description = RichTextUploadingField(blank=True)
    page_description = models.TextField(blank=True)
    benefits = models.TextField(
        blank=True, 
        help_text="Enter benefits, one per line."
    )
    inclusions = models.TextField(
        blank=True, 
        help_text="Enter Seva inclusions, one per line."
    )
    image = models.ImageField(upload_to='pujas/main/', blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True)
    price = models.CharField(max_length=100, blank=True)
    pandits = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    deity = models.CharField(max_length=100, blank=True)
    required_purohits = models.PositiveIntegerField(default=1)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Generate slug from title if not set
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        
        # Guard against null created_at which was causing IntegrityError in some environments
        if not self.created_at:
            self.created_at = timezone.now()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['display_order', 'title']
        verbose_name_plural = "Pujas"

class PujaGalleryImage(models.Model):
    """Gallery images for a specific Puja."""
    puja = models.ForeignKey(Puja, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='pujas/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Puja Gallery Image"
        verbose_name_plural = "Puja Gallery Images"

    def __str__(self):
        return f"Gallery for {self.puja.title}"
class BookingAdditionalPriest(models.Model):
    """Through-model for multiple additional priests on a single booking."""

    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='additional_priest_relationships'
    )
    priest = models.ForeignKey(
        PriestProfile,
        on_delete=models.CASCADE,
        related_name='additional_priest_assignments'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('booking', 'priest')]
        verbose_name_plural = 'Booking Additional Priests'

    def __str__(self):
        return f"{self.booking_id} – {self.priest.fullname} ({self.status})"
import uuid

class BookingFeedback(models.Model):
    """Stores feedback for specific bookings."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='feedback')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    # Survey data
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Rating from 1 to 5")
    comments = models.TextField(blank=True, null=True)
    
    # State tracking
    is_sent = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Feedback for Booking #{self.booking.id} - {self.booking.devotee_name}"

    class Meta:
        verbose_name_plural = 'Booking Feedbacks'

class BookingEnquiry(models.Model):
    """Stores enquiries raised by devotees for specific bookings."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='enquiry')
    category = models.ForeignKey(
        'EnquiryCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enquiries'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        category = self.category.name if self.category else "General"
        return f"Enquiry ({category}) for Booking #{self.booking.id} - {self.booking.devotee_name}"

    class Meta:
        verbose_name_plural = 'Booking Enquiries'

class EnquiryCategory(models.Model):
    """Dropdown categories for booking enquiries (e.g., Refund, Service Issue)."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name_plural = 'Enquiry Categories'

    def __str__(self):
        return self.name
class HomeHeroConfig(models.Model):
    """Singleton-like model for Home Hero section configuration."""
    title_gold = models.CharField(max_length=255, default="BRINGING SACRED")
    title_ivory = models.CharField(max_length=255, default="RITUALS TO YOUR HOME")
    subtitle = models.TextField(default="Experience the sanctity of Authentic Vedic Rituals performed by verified Pandits.")
    quote_text = models.CharField(max_length=255, default="Dharmo Rakshati Rakshitah")
    watermark_text = models.CharField(max_length=100, default="ॐ नमः शिवाय")
    
    # Hero Background Images (handled via a related model if multiple needed, or fields here)
    hero_bg_1 = models.ImageField(upload_to='home/hero/', blank=True, null=True)
    hero_bg_2 = models.ImageField(upload_to='home/hero/', blank=True, null=True)
    hero_bg_3 = models.ImageField(upload_to='home/hero/', blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Home Hero Configuration"
        verbose_name_plural = "Home Hero Configuration"

    def __str__(self):
        return "Home Hero Config"

class SpiritualJourneyStep(models.Model):
    """Steps for the 'Your Path to Divine' section."""
    step_number = models.CharField(max_length=10, help_text="e.g., 01, 02")
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(max_length=100, help_text="FontAwesome class, e.g., fas fa-hand-holding-heart")
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'step_number']
        verbose_name = "Spiritual Journey Step"
        verbose_name_plural = "Spiritual Journey Steps"

    def __str__(self):
        return f"Step {self.step_number}: {self.title}"

class SankalpPillar(models.Model):
    """Cards for the 'Three Pillars of Purity' section."""
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    description = models.TextField()
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'title']
        verbose_name = "Sankalp Pillar"
        verbose_name_plural = "Sankalp Pillars"

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    """Devotee stories/testimonials."""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    text = models.TextField()
    image = models.ImageField(upload_to='home/testimonials/', blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    date_added = models.DateField(default=timezone.now)

    class Meta:
        ordering = ['display_order', '-date_added']

    def __str__(self):
        return f"Testimonial by {self.name}"

class HomeAboutConfig(models.Model):
    """Configuration for the 'Authentic & Divine' home about section."""
    title = models.CharField(max_length=255, default="Authentic & Divine")
    subtitle = models.TextField(default="We bring traditional Vedic rituals to your doorstep with utmost devotion.")
    badge_text = models.CharField(max_length=100, default="Why Choose Us")
    main_image = models.ImageField(upload_to='home/about/', blank=True, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Home About Configuration"
        verbose_name_plural = "Home About Configuration"

    def __str__(self):
        return "Home About Config"

class SEOMetadata(models.Model):
    """Stores SEO related metadata for specific URL paths."""
    path = models.CharField(max_length=255, unique=True, help_text="The URL path (e.g., '/', '/services/')")
    title_tag = models.CharField(max_length=255)
    meta_description = models.TextField()
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords")
    og_image = models.ImageField(upload_to='seo/og_images/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "SEO Metadata"
        verbose_name_plural = "SEO Metadata"

    def __str__(self):
        return self.path

class Notification(models.Model):
    """System-wide notification for users (devotees, purohits, admins)."""
    NOTIFICATION_TYPES = [
        ('booking_new', 'New Booking Request'),
        ('booking_confirmed', 'Booking Confirmed'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('enquiry_new', 'New Enquiry Raised'),
        ('system_alert', 'System Alert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.username}"

class PriestPerformance(models.Model):
    """Tracks performance metrics for each purohit."""
    priest = models.OneToOneField(PriestProfile, on_delete=models.CASCADE, related_name='performance')
    total_assigned = models.PositiveIntegerField(default=0)
    completed_successful = models.PositiveIntegerField(default=0)
    rejected_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    
    updated_at = models.DateTimeField(auto_now=True)

    def update_rating(self):
        """Calculate rating based on completion vs total assigned."""
        if self.total_assigned > 0:
            # Simple formula: (completed / total) * 5
            # We can refine this based on user feedback (e.g., rejections penalize more)
            base_rating = (self.completed_successful / self.total_assigned) * 5
            self.rating = round(base_rating, 2)
        else:
            self.rating = 5.00
        self.save()

    def __str__(self):
        return f"Performance: {self.priest.fullname}"

@receiver(post_save, sender=PriestProfile)
def create_priest_performance(sender, instance, created, **kwargs):
    if created:
        PriestPerformance.objects.create(priest=instance)
