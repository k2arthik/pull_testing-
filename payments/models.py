import uuid
from django.db import models
from django.conf import settings
from core.models import Booking


class Payment(models.Model):
    """Tracks Razorpay payment transactions linked to bookings."""

    STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='payments'
    )
    razorpay_order_id = models.CharField(
        max_length=100, unique=True, db_index=True
    )
    razorpay_payment_id = models.CharField(
        max_length=100, blank=True, null=True
    )
    razorpay_signature = models.CharField(
        max_length=255, blank=True, null=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='upi')
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='CREATED'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['razorpay_order_id']),
            models.Index(fields=['booking', 'status']),
        ]

    def __str__(self):
        return f"Payment #{self.pk} — ₹{self.amount} — {self.status}"


class Refund(models.Model):
    """Tracks refund requests and their processing status."""

    STATUS_CHOICES = [
        ('INITIATED', 'Initiated'),
        ('PROCESSED', 'Processed'),
        ('FAILED', 'Failed'),
    ]

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='refunds'
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name='refunds'
    )
    razorpay_refund_id = models.CharField(
        max_length=100, blank=True, null=True
    )
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='INITIATED'
    )
    refund_reason = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund #{self.pk} — ₹{self.refund_amount} — {self.refund_status}"