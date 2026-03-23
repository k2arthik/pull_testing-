"""
Refund service layer — PhonePe PG edition.
Calculates refund amounts per policy and calls PhonePe Refund API.
"""
import logging
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from payments.models import Payment, Refund
from payments.services.phonepe_service import process_phonepe_refund

logger = logging.getLogger(__name__)


def calculate_refund_amount(booking) -> Decimal:
    """
    Compute refund amount based on cancellation policy:

        > 24h before ritual  →  90% refund
        0–24h before ritual  →  50% refund
        Past start time      →   0% refund
    """
    now = timezone.now()
    ritual_dt = timezone.make_aware(
        datetime.combine(booking.booking_date, booking.start_time)
    )
    hours_left = (ritual_dt - now).total_seconds() / 3600

    if hours_left > 24:
        return Decimal(str(booking.amount)) * Decimal('0.9')
    elif hours_left > 0:
        return Decimal(str(booking.amount)) * Decimal('0.5')
    else:
        return Decimal('0')


def process_refund(booking, reason: str = 'Cancelled by devotee'):
    """
    Process a refund for a cancelled booking via PhonePe Refund API.

    Steps:
      1. Calculate refund amount.
      2. Find the successful Payment.
      3. Call PhonePe Refund API.
      4. Create a Refund DB record.

    Returns:
        Refund instance, or None if refund amount is 0.

    Raises:
        Exception if PhonePe Refund API call fails (Refund FAILED record is created).
    """
    refund_amount = calculate_refund_amount(booking)

    if refund_amount <= 0:
        logger.info(f"No refund applicable for booking {booking.pk} (0% policy)")
        return None

    payment = Payment.objects.filter(booking=booking, status='SUCCESS').first()
    if not payment:
        logger.warning(f"No successful payment found for booking {booking.pk}")
        return None

    # PhonePe transaction ID is stored in razorpay_order_id field
    original_txn_id  = payment.razorpay_order_id
    refund_amt_paise = int(refund_amount * 100)

    try:
        result = process_phonepe_refund(
            original_transaction_id=original_txn_id,
            refund_amount_paise=refund_amt_paise,
            booking_id=booking.pk,
            reason=reason,
        )

        refund = Refund.objects.create(
            booking=booking,
            payment=payment,
            razorpay_refund_id=result['refund_id'],   # stores PhonePe refund txn id
            refund_amount=refund_amount,
            refund_status='PROCESSED',
            refund_reason=reason,
        )
        logger.info(f"Refund initiated for booking {booking.pk}: ₹{refund_amount}")
        return refund

    except Exception as exc:
        # Always create a FAILED record for audit trail
        Refund.objects.create(
            booking=booking,
            payment=payment,
            refund_amount=refund_amount,
            refund_status='FAILED',
            refund_reason=f"{reason} | Error: {exc}",
        )
        logger.error(f"PhonePe refund failed for booking {booking.pk}: {exc}")
        raise