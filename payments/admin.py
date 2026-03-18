from django.contrib import admin
from .models import Payment, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment records."""

    list_display = [
        'id', 'booking', 'razorpay_order_id', 'razorpay_payment_id',
        'amount', 'payment_method', 'status', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'razorpay_order_id', 'razorpay_payment_id',
        'booking__devotee_name', 'booking__service'
    ]
    readonly_fields = [
        'razorpay_order_id', 'razorpay_payment_id',
        'razorpay_signature', 'created_at'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Payment Details', {
            'fields': (
                'booking', 'amount', 'payment_method', 'status',
            )
        }),
        ('Razorpay Data', {
            'fields': (
                'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin interface for Refund records."""

    list_display = [
        'id', 'booking', 'payment', 'razorpay_refund_id',
        'refund_amount', 'refund_status', 'created_at'
    ]
    list_filter = ['refund_status', 'created_at']
    search_fields = [
        'razorpay_refund_id', 'booking__devotee_name',
        'refund_reason'
    ]
    readonly_fields = ['razorpay_refund_id', 'created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Refund Details', {
            'fields': (
                'booking', 'payment', 'refund_amount',
                'refund_status', 'refund_reason',
            )
        }),
        ('Razorpay Data', {
            'fields': ('razorpay_refund_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )