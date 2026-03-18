"""
PhonePe webhook handler.
Receives server-to-server callbacks from PhonePe and updates Payment records.
"""
import json
import base64
import hashlib
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from payments.models import Payment, Refund
from payments.services.phonepe_service import (
    _salt_key, _salt_index, check_payment_status
)

logger = logging.getLogger(__name__)


def _verify_webhook_checksum(x_verify: str, response_base64: str) -> bool:
    """
    Verify PhonePe webhook X-VERIFY header.
    Formula: SHA256(response_base64 + "/pg/v1/pay" + SALT_KEY) + ### + SALT_INDEX
    PhonePe uses the same formula for webhook verification.
    """
    try:
        raw = response_base64 + _salt_key()
        expected_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        expected = f"{expected_hash}###{_salt_index()}"
        return expected == x_verify
    except Exception:
        return False


@csrf_exempt
@require_POST
def phonepe_webhook(request):
    """
    Handle PhonePe server-to-server callback.

    PhonePe sends a POST with a base64-encoded response payload.
    We decode it, verify the checksum, then update our DB.
    """
    try:
        x_verify = request.headers.get('X-VERIFY', '')
        body_data = json.loads(request.body)

        response_b64 = body_data.get('response', '')
        if not response_b64:
            logger.warning("PhonePe webhook: empty response payload")
            return JsonResponse({'status': 'error'}, status=400)

        # Verify checksum
        if x_verify and not _verify_webhook_checksum(x_verify, response_b64):
            logger.warning("PhonePe webhook: checksum verification failed")
            return JsonResponse({'status': 'error'}, status=400)

        # Decode payload
        decoded = json.loads(base64.b64decode(response_b64).decode('utf-8'))
        logger.info(f"PhonePe webhook payload: {decoded}")

        code           = decoded.get('code', '')
        data           = decoded.get('data', {})
        transaction_id = data.get('merchantTransactionId', '')

        if not transaction_id:
            return JsonResponse({'status': 'ok'})

        if code == 'PAYMENT_SUCCESS':
            _handle_payment_success(transaction_id)
        elif code in ('PAYMENT_ERROR', 'PAYMENT_DECLINED', 'TIMED_OUT'):
            _handle_payment_failure(transaction_id)
        else:
            logger.info(f"PhonePe webhook: unhandled code {code}")

        return JsonResponse({'status': 'ok'})

    except Exception as exc:
        logger.error(f"PhonePe webhook error: {exc}")
        return JsonResponse({'status': 'ok'})   # always 200 to stop retries


def _handle_payment_success(transaction_id: str):
    """Mark Payment SUCCESS and Booking PENDING via shared service — idempotent."""
    try:
        from payments.services.payment_service import process_payment_success
        payment = Payment.objects.select_related('booking').get(
            razorpay_order_id=transaction_id
        )
        process_payment_success(payment, transaction_id)
        logger.info(f"Webhook successfully processed payment/booking for txn {transaction_id}")

    except Payment.DoesNotExist:
        logger.warning(f"Webhook: no payment found for txn {transaction_id}")


def _handle_payment_failure(transaction_id: str):
    """Mark Payment FAILED."""
    try:
        payment = Payment.objects.get(razorpay_order_id=transaction_id)
        if payment.status == 'SUCCESS':
            return  # don't downgrade a SUCCESS
        payment.status = 'FAILED'
        payment.save()
        logger.info(f"Webhook: Payment {payment.pk} → FAILED")

    except Payment.DoesNotExist:
        logger.warning(f"Webhook: no payment found for txn {transaction_id}")
