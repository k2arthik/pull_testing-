"""
Payment views — PhonePe PG edition.
Flow: initiate → PhonePe PAY_PAGE → callback → verify via API → success → confirm
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse

from core.models import Booking
from payments.models import Payment
from payments.services.payment_service import initiate_payment, verify_and_record_payment
from payments.services.refund_service import process_refund, calculate_refund_amount

logger = logging.getLogger(__name__)


# ─── 1. Initiate Payment ─────────────────────────────────────────────────────

@login_required
def initiate_payment_view(request, booking_id):
    """
    Create a PhonePe PAY_PAGE request and redirect the user to PhonePe.
    """
    booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)

    if booking.status != 'pending_payment':
        messages.error(request, "This booking is not awaiting payment.")
        return redirect('my_bookings')

    if booking.amount <= 0:
        messages.error(request, "Invalid booking amount. Please contact support.")
        return redirect('my_bookings')

    try:
        redirect_url  = request.build_absolute_uri(
            reverse('payment_callback', kwargs={'booking_id': booking_id})
        )
        callback_url  = request.build_absolute_uri(reverse('phonepe_webhook'))

        result = initiate_payment(booking, redirect_url, callback_url)

        # Store transaction_id in session so callback can use it
        request.session[f'phonepe_txn_{booking_id}'] = result['transaction_id']

        logger.info(f"Redirecting booking {booking_id} to PhonePe: {result['transaction_id']}")
        return redirect(result['redirect_url'])

    except Exception as exc:
        logger.error(f"PhonePe initiation failed for booking {booking_id}: {exc}")
        messages.error(request, "Unable to initiate payment. Please try again.")
        return redirect('my_bookings')


# ─── 2. Payment Callback (after PhonePe redirects back) ──────────────────────

@login_required
def payment_callback(request, booking_id):
    """
    PhonePe redirects here after user completes / cancels payment.
    We verify payment status via PhonePe Status API — never trust the redirect.
    """
    booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)

    # Get transaction_id: prefer URL param (PhonePe may send it),
    # fall back to session.
    transaction_id = (
        request.GET.get('transactionId')
        or request.GET.get('merchantTransactionId')
        or request.session.get(f'phonepe_txn_{booking_id}')
    )

    if not transaction_id:
        # Try to find it from latest CREATED Payment
        payment = Payment.objects.filter(
            booking=booking, status='CREATED'
        ).order_by('-created_at').first()
        if payment:
            transaction_id = payment.razorpay_order_id

    if not transaction_id:
        messages.error(request, "Payment reference not found. Please contact support.")
        return redirect('my_bookings')

    try:
        result = verify_and_record_payment(transaction_id)

        if result['success']:
            # Clean up session
            request.session.pop(f'phonepe_txn_{booking_id}', None)
            return redirect('payment_success', booking_id=booking_id)
        else:
            code = result.get('code', 'UNKNOWN')
            logger.warning(f"PhonePe payment not successful for booking {booking_id}: {code}")
            return redirect('payment_failed', booking_id=booking_id)

    except Exception as exc:
        logger.error(f"Payment verification error for booking {booking_id}: {exc}")
        messages.error(request, "Payment verification failed. Our team will follow up.")
        return redirect('payment_failed', booking_id=booking_id)


# ─── 3. Success Page ─────────────────────────────────────────────────────────

@login_required
def payment_success(request, booking_id):
    """Show payment success page with 'Confirm Booking' button."""
    booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)
    payment = Payment.objects.filter(booking=booking, status='SUCCESS').first()
    return render(request, 'payments/payment_success.html', {
        'booking': booking,
        'payment': payment,
    })


# ─── 4. Failed Page ──────────────────────────────────────────────────────────

@login_required
def payment_failed(request, booking_id):
    """Show payment failed page with retry option."""
    booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)
    return render(request, 'payments/payment_failed.html', {'booking': booking})


# ─── 5. Confirm Booking (Two-Step) ───────────────────────────────────────────

@require_POST
@login_required
def confirm_booking(request, booking_id):
    """
    POST — Confirm booking after the user manually clicks 'Confirm Booking'.
    Guard: booking must be in payment_completed state with a SUCCESS Payment.
    """
    booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)

    if booking.status == 'confirmed':
        messages.info(request, "This booking is already confirmed.")
        return redirect('my_bookings')

    if booking.status != 'payment_completed' and booking.status != 'confirmed':
        # Since we now confirm automatically, it's rare to be in payment_completed
        # but let's allow it just in case.
        pass

    has_payment = Payment.objects.filter(booking=booking, status='SUCCESS').exists()
    if not has_payment:
        messages.error(request, "No verified payment found for this booking.")
        return redirect('my_bookings')

    booking.status = 'confirmed'
    booking.save(skip_validation=True)

    messages.success(request, "\U0001f389 Booking confirmed! The purohit has been notified.")
    return redirect('my_bookings')


# ─── 6. Cancel & Refund ──────────────────────────────────────────────────────

@require_POST
@login_required
def cancel_booking(request, booking_id):
    """Cancel booking and trigger refund via PhonePe Refund API."""
    booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)

    if booking.status not in ('pending_payment', 'payment_completed', 'confirmed'):
        messages.error(request, "This booking cannot be cancelled.")
        return redirect('my_bookings')

    refund_amount = calculate_refund_amount(booking)

    try:
        refund = None
        if booking.status in ('payment_completed', 'confirmed'):
            refund = process_refund(booking, reason='Cancelled by devotee')

        booking.status = 'cancelled'
        booking.save(skip_validation=True)
        booking.restore_slot_availability()

        if refund:
            messages.success(
                request,
                f"Booking cancelled. Refund of \u20b9{refund.refund_amount} initiated."
            )
        elif refund_amount <= 0:
            messages.warning(
                request,
                "Booking cancelled. No refund applicable per cancellation policy."
            )
        else:
            messages.success(request, "Booking cancelled successfully.")

    except Exception as exc:
        logger.error(f"Cancel/refund error for booking {booking_id}: {exc}")
        booking.status = 'cancelled'
        booking.save(skip_validation=True)
        booking.restore_slot_availability()
        messages.warning(
            request,
            "Booking cancelled. There was a refund issue — our team will follow up."
        )

    return redirect('my_bookings')


# ─── 7. Mock Payment (Debug) ────────────────────────────────────────────────

@login_required
def mock_payment_page(request, booking_id):
    """
    A simple debug page to simulate a payment.
    """
    booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)
    return render(request, 'payments/mock_payment_page.html', {'booking': booking})


@login_required
def mock_payment_success(request, booking_id):
    """
    Simulate a successful payment for testing.
    """
    booking = get_object_or_404(Booking, pk=booking_id, devotee=request.user)

    # 1. Create a successful payment record
    Payment.objects.create(
        booking=booking,
        razorpay_order_id=f"MOCK_ORD_{booking_id}",
        razorpay_payment_id=f"MOCK_PAY_{booking_id}",
        amount=booking.amount,
        status='SUCCESS'
    )

    # 2. Update booking status to confirmed (following our auto-confirm logic)
    booking.status = 'confirmed'
    booking.save(skip_validation=True)

    messages.success(request, "Mock Payment Successful! Booking is now Confirmed.")
    return redirect('payment_success', booking_id=booking_id)

