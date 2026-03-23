"""
PhonePe Payment Gateway service layer.
Implements PAY_PAGE flow per PhonePe PG API v1.
"""
import json
import base64
import hashlib
import uuid
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# ─── PhonePe API Config ──────────────────────────────────────────────────────
PHONEPE_BASE_URL_UAT  = 'https://api-preprod.phonepe.com/apis/pg-sandbox'
PHONEPE_BASE_URL_PROD = 'https://api.phonepe.com/apis/hermes'
PAY_ENDPOINT          = '/pg/v1/pay'
STATUS_ENDPOINT       = '/pg/v1/status'
REFUND_ENDPOINT       = '/pg/v1/refund'


def _base_url():
    """Return correct PhonePe base URL based on environment."""
    if getattr(settings, 'PHONEPE_ENV', 'UAT') == 'PROD':
        return PHONEPE_BASE_URL_PROD
    return PHONEPE_BASE_URL_UAT


def _merchant_id():
    return settings.PHONEPE_MERCHANT_ID


def _salt_key():
    return settings.PHONEPE_SALT_KEY


def _salt_index():
    return getattr(settings, 'PHONEPE_SALT_INDEX', '1')


# ─── Signature ───────────────────────────────────────────────────────────────

def generate_phonepe_signature(base64_payload: str, endpoint: str) -> str:
    """
    Generate X-VERIFY header value.

    Formula: SHA256(base64_payload + endpoint + SALT_KEY) + "###" + SALT_INDEX
    """
    raw = base64_payload + endpoint + _salt_key()
    sha256_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    return f"{sha256_hash}###{_salt_index()}"


def verify_phonepe_signature(base64_payload: str, endpoint: str, x_verify: str) -> bool:
    """Verify a response X-VERIFY header from PhonePe."""
    expected = generate_phonepe_signature(base64_payload, endpoint)
    return expected == x_verify


# ─── Payment Request ─────────────────────────────────────────────────────────

def create_phonepe_payment(booking, redirect_url: str, callback_url: str) -> dict:
    """
    Create a PhonePe PAY_PAGE payment request.

    Returns:
        dict with keys:
          - redirect_url   : URL to redirect the user to PhonePe page
          - transaction_id : merchantTransactionId stored in Payment record
          - success        : bool

    Raises:
        Exception on API failure.
    """
    merchant_id      = _merchant_id()
    transaction_id   = f"TXN-{booking.pk}-{uuid.uuid4().hex[:10].upper()}"
    merchant_user_id = f"USER-{booking.devotee_id}"
    amount_paise     = int(booking.amount * 100)

    payload = {
        "merchantId": merchant_id,
        "merchantTransactionId": transaction_id,
        "merchantUserId": merchant_user_id,
        "amount": amount_paise,
        "redirectUrl": redirect_url,
        "redirectMode": "REDIRECT",
        "callbackUrl": callback_url,
        "mobileNumber": booking.devotee_phone or "",
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }

    payload_json   = json.dumps(payload)
    payload_b64    = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
    x_verify       = generate_phonepe_signature(payload_b64, PAY_ENDPOINT)

    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': x_verify,
        'X-MERCHANT-ID': merchant_id,
    }

    request_body = {"request": payload_b64}

    logger.info(f"PhonePe payment request: txn={transaction_id}, amount={amount_paise}")

    response = requests.post(
        f"{_base_url()}{PAY_ENDPOINT}",
        headers=headers,
        json=request_body,
        timeout=30,
    )

    resp_data = response.json()
    logger.info(f"PhonePe response: {resp_data}")

    if not resp_data.get('success'):
        raise Exception(
            f"PhonePe API error: {resp_data.get('code')} — {resp_data.get('message')}"
        )

    pay_page_url = (
        resp_data
        .get('data', {})
        .get('instrumentResponse', {})
        .get('redirectInfo', {})
        .get('url', '')
    )

    # UAT Simulator Bypass: Skip the 'merchant-simulator' middle page
    if pay_page_url and 'mercury-uat.phonepe.com/transact/simulator' in pay_page_url:
        if 'token=' in pay_page_url:
            # Reconstruct to direct simulator if needed, 
            # but usually just stripping the merchant-simulator part works if the URL structure allows.
            # User specifically asked to navigate to https://mercury-uat.phonepe.com/transact/simulator?token=...
            pay_page_url = pay_page_url.replace('/merchant-simulator', '')

    if not pay_page_url:
        raise Exception("PhonePe did not return a redirect URL.")

    return {
        'redirect_url': pay_page_url,
        'transaction_id': transaction_id,
        'success': True,
    }


# ─── Payment Status ───────────────────────────────────────────────────────────

def check_payment_status(transaction_id: str) -> dict:
    """
    Verify payment status via PhonePe Status API.

    Returns:
        dict with keys:
          - success         : bool
          - status          : 'SUCCESS' | 'FAILED' | 'PENDING'
          - transaction_id  : str
          - amount_paise    : int (if available)
          - payment_instrument : dict (raw data)

    Raises:
        Exception on network error.
    """
    merchant_id = _merchant_id()
    endpoint    = f"{STATUS_ENDPOINT}/{merchant_id}/{transaction_id}"
    x_verify    = generate_phonepe_signature('', endpoint)

    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': x_verify,
        'X-MERCHANT-ID': merchant_id,
    }

    response = requests.get(
        f"{_base_url()}{endpoint}",
        headers=headers,
        timeout=30,
    )

    resp_data = response.json()
    logger.info(f"PhonePe status check for {transaction_id}: {resp_data}")

    pg_data = resp_data.get('data', {})
    code    = resp_data.get('code', '')

    if code == 'PAYMENT_SUCCESS':
        status = 'SUCCESS'
    elif code in ('PAYMENT_PENDING', 'PAYMENT_INITIATED'):
        status = 'PENDING'
    else:
        status = 'FAILED'

    return {
        'success': code == 'PAYMENT_SUCCESS',
        'status': status,
        'code': code,
        'transaction_id': transaction_id,
        'amount_paise': pg_data.get('amount', 0),
        'payment_instrument': pg_data.get('paymentInstrument', {}),
        'raw': resp_data,
    }


# ─── Refund ───────────────────────────────────────────────────────────────────

def process_phonepe_refund(
    original_transaction_id: str,
    refund_amount_paise: int,
    booking_id: int,
    reason: str = 'Cancelled by devotee',
) -> dict:
    """
    Initiate refund via PhonePe Refund API.

    Returns:
        dict with keys: success, refund_id, message

    Raises:
        Exception on API failure.
    """
    merchant_id    = _merchant_id()
    refund_txn_id  = f"REFUND-{booking_id}-{uuid.uuid4().hex[:10].upper()}"

    payload = {
        "merchantId": merchant_id,
        "merchantUserId": f"BOOKING-{booking_id}",
        "originalTransactionId": original_transaction_id,
        "merchantTransactionId": refund_txn_id,
        "amount": refund_amount_paise,
        "callbackUrl": "",
    }

    payload_json = json.dumps(payload)
    payload_b64  = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
    x_verify     = generate_phonepe_signature(payload_b64, REFUND_ENDPOINT)

    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': x_verify,
        'X-MERCHANT-ID': merchant_id,
    }

    response = requests.post(
        f"{_base_url()}{REFUND_ENDPOINT}",
        headers=headers,
        json={"request": payload_b64},
        timeout=30,
    )

    resp_data = response.json()
    logger.info(f"PhonePe refund response: {resp_data}")

    if not resp_data.get('success'):
        raise Exception(
            f"PhonePe refund error: {resp_data.get('code')} — {resp_data.get('message')}"
        )

    return {
        'success': True,
        'refund_id': refund_txn_id,
        'message': resp_data.get('message', 'Refund initiated'),
    }