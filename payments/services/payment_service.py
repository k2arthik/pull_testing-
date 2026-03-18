"""
Payment service layer — PhonePe PG edition.
Thin wrapper that delegates to phonepe_service and manages DB records.
"""
import logging
from payments.models import Payment
from payments.services.phonepe_service import (
    create_phonepe_payment,
    check_payment_status,
)

logger = logging.getLogger(__name__)


def initiate_payment(booking, redirect_url: str, callback_url: str) -> dict:
    """
    Create a PhonePe PAY_PAGE request and a CREATED Payment record.

    Returns:
        dict: { redirect_url, transaction_id }
    """
    result = create_phonepe_payment(booking, redirect_url, callback_url)
    transaction_id = result['transaction_id']

    # Persist Payment record in CREATED state
    Payment.objects.create(
        booking=booking,
        razorpay_order_id=transaction_id,      # repurposed — stores PhonePe transactionId
        amount=booking.amount,
        payment_method='upi',
        status='CREATED',
    )

    return result


def verify_and_record_payment(transaction_id: str) -> dict:
    """
    Call PhonePe Status API, then update Payment and Booking records.
    """
    status_data = check_payment_status(transaction_id)

    payment = Payment.objects.select_related('booking').get(
        razorpay_order_id=transaction_id
    )

    if status_data['success']:
        process_payment_success(payment, transaction_id)
        return {'success': True, 'payment': payment}
    else:
        if payment.status != 'SUCCESS':
            payment.status = 'FAILED' if status_data['status'] == 'FAILED' else 'CREATED'
            payment.save()
        return {'success': False, 'payment': payment, 'code': status_data.get('code')}


def process_payment_success(payment, transaction_id):
    """
    Shared logic to mark payment as SUCCESS, update booking to PENDING,
    and send detailed notifications.
    """
    if payment.status == 'SUCCESS':
        return

    payment.razorpay_payment_id = transaction_id
    payment.status = 'SUCCESS'
    payment.save()

    booking = payment.booking
    if booking.status == 'pending_payment':
        booking.status = 'pending'
        booking.save(skip_validation=True)
        
        # Send detailed notifications
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            from django.contrib.auth.models import User
            from core.services_data import services as services_data
            
            service_title = services_data.get(booking.service, {}).get('title', booking.service)
            priest = booking.priest
            
            # Common data
            data_summary = (
                f"Booking ID: #{booking.id}\n"
                f"Service: {service_title}\n"
                f"Date: {booking.booking_date}\n"
                f"Slot: {booking.get_slot_type_display()}\n"
                f"Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}\n"
                f"Amount: ₹{booking.amount}\n"
                f"Payment Status: PAID\n"
            )
            
            contact_info = (
                f"Devotee: {booking.devotee_name} ({booking.devotee_phone})\n"
                f"Priest: {priest.fullname} ({priest.mobile})\n"
            )

            # 1. To Devotee
            devotee_dashboard_link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/devotee/dashboard/"
            send_mail(
                'Booking Received & Payment Confirmed — Karya Siddhi',
                f"Namaste {booking.devotee_name},\n\n"
                f"Thank you for your payment. Your booking request for '{service_title}' has been received.\n\n"
                f"Your request is now PENDING CONFIRMATION by the Priest. We will notify you as soon as they accept.\n\n"
                f"{data_summary}\n"
                f"Priest Contact: {priest.fullname} ({priest.mobile})\n\n"
                f"You can view your booking details here:\n{devotee_dashboard_link}\n\n"
                f"Regards,\nKarya Siddhi Team",
                settings.DEFAULT_FROM_EMAIL,
                [booking.devotee.email],
                fail_silently=True
            )

            # 2. To Priest
            priest_dashboard_link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/purohit/dashboard/"
            send_mail(
                'Action Required: New Booking Request Received',
                f"Hello {priest.fullname},\n\n"
                f"A new booking request has been received and paid for.\n\n"
                f"Please log in to your dashboard to ACCEPT or REJECT this request.\n\n"
                f"{data_summary}\n"
                f"Devotee Contact: {booking.devotee_name} ({booking.devotee_phone})\n\n"
                f"Dashboard: {priest_dashboard_link}\n\n"
                f"Regards,\nKarya Siddhi Team",
                settings.DEFAULT_FROM_EMAIL,
                [priest.user.email],
                fail_silently=True
            )

            # 3. To Admin
            admin_dashboard_link = f"{settings.SITE_URL if hasattr(settings, 'SITE_URL') else ''}/admin-portal/"
            admin_emails = list(User.objects.filter(is_superuser=True).exclude(email='').values_list('email', flat=True)) or [settings.DEFAULT_FROM_EMAIL]
            send_mail(
                f'[New Booking] #{booking.id} Paid for {service_title}',
                f"A new booking has been fully paid and is awaiting priest confirmation.\n\n"
                f"{data_summary}\n"
                f"{contact_info}\n"
                f"View in Admin Portal: {admin_dashboard_link}\n\n"
                f"Regards,\nKarya Siddhi System",
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Error sending detailed payment success emails: {e}")

    else:
        if payment.status != 'SUCCESS':
            payment.status = 'FAILED' if status_data['status'] == 'FAILED' else 'CREATED'
            payment.save()
        return {'success': False, 'payment': payment, 'code': status_data.get('code')}