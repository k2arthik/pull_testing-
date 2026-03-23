from django.urls import path
from payments import views
from payments.webhooks import phonepe_webhook

urlpatterns = [
    # ── Payment Flow ─────────────────────────────────────────────────────────
    # Step 1: Initiate payment — creates PhonePe order and redirects to PAY_PAGE
    path('payments/pay/<int:booking_id>/',
         views.initiate_payment_view, name='initiate_payment'),

    # Step 2: PhonePe redirects back here after payment
    path('payments/callback/<int:booking_id>/',
         views.payment_callback, name='payment_callback'),

    # Step 3: Success/Failed pages
    path('payments/success/<int:booking_id>/',
         views.payment_success, name='payment_success'),
    path('payments/failed/<int:booking_id>/',
         views.payment_failed, name='payment_failed'),

    # ── Booking Actions ───────────────────────────────────────────────────────
    # Two-step confirmation after payment
    path('booking/confirm/<int:booking_id>/',
         views.confirm_booking, name='confirm_booking'),

    # Cancellation + refund
    path('booking/cancel/<int:booking_id>/',
         views.cancel_booking, name='cancel_booking_payment'),

    # ── PhonePe Webhook ───────────────────────────────────────────────────────
    path('payments/webhook/', phonepe_webhook, name='phonepe_webhook'),

    # -- Mock Payment (DEBUG ONLY) --
    path('payments/mock/<int:booking_id>/', views.mock_payment_page, name='mock_payment_page'),
    path('payments/mock/<int:booking_id>/success/', views.mock_payment_success, name='mock_payment_success'),
]
