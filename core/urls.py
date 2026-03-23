from django.urls import path
<<<<<<< HEAD
from . import views

urlpatterns = [
=======
from . import views, dashboard_views

urlpatterns = [
    # Dashboard (Advanced)
    path('admin-portal/', dashboard_views.admin_dashboard_overview, name='admin_dashboard'),
    path('admin-portal/pujas/', dashboard_views.admin_puja_list, name='admin_puja_list'),
    path('admin-portal/pujas/add/', dashboard_views.admin_puja_edit, name='admin_puja_add'),
    path('admin-portal/pujas/<slug:slug>/edit/', dashboard_views.admin_puja_edit, name='admin_puja_edit'),
    path('admin-portal/pujas/<slug:slug>/delete/', dashboard_views.admin_puja_delete, name='admin_puja_delete'),
    path('admin-portal/devotees/', dashboard_views.admin_devotee_list, name='admin_devotee_list'),
    path('admin-portal/devotees/<int:user_id>/edit/', dashboard_views.admin_devotee_edit, name='admin_devotee_edit'),
    path('admin-portal/devotees/<int:user_id>/delete/', dashboard_views.admin_devotee_delete, name='admin_devotee_delete'),
    path('admin-portal/purohits/', dashboard_views.admin_purohit_list, name='admin_purohit_list'),
    path('admin-portal/purohits/<int:user_id>/edit/', dashboard_views.admin_purohit_edit, name='admin_purohit_edit'),
    path('admin-portal/purohits/<int:user_id>/delete/', dashboard_views.admin_purohit_delete, name='admin_purohit_delete'),
    path('admin-portal/seo/', dashboard_views.admin_seo_list, name='admin_seo_list'),
    path('admin-portal/seo/add/', dashboard_views.admin_seo_edit, name='admin_seo_add'),
    path('admin-portal/seo/<int:seo_id>/edit/', dashboard_views.admin_seo_edit, name='admin_seo_edit'),
    path('admin-portal/seo/<int:seo_id>/delete/', dashboard_views.admin_seo_delete, name='admin_seo_delete'),
    path('admin-portal/inquiries/', dashboard_views.admin_inquiry_list, name='admin_inquiry_list'),
    
>>>>>>> 2efb7cacf3c38ae4a19cba1052ea6b35cd3fd4d3
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('services/<slug:service_slug>/', views.service_detail, name='service_detail'),
    path('temples/', views.temples, name='temples'),
    path('contact/', views.contact, name='contact'),
<<<<<<< HEAD
    path('blogs/', views.blogs, name='blogs'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('cart/', views.cart, name='cart'),
    path('purohit/login/', views.purohit_login, name='purohit_login'),
    path('purohit/signup/', views.purohit_signup, name='purohit_signup'),
    path('purohit/dashboard/', views.purohit_dashboard, name='purohit_dashboard'),
=======
    path('contact/success/', views.contact_success, name='contact_success'),
    path('subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('blogs/', views.blogs, name='blogs'),
    path('blogs/<slug:blog_slug>/', views.blog_detail, name='blog_detail'),
    path('photos/', views.photos_view, name='photos'),
    path('videos/', views.videos_view, name='videos'),
    path('login/', views.login_view, name='login'),
    path('signup-selector/', views.signup_selector_view, name='signup_selector'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('purohit/login/', views.purohit_login, name='purohit_login'),
    path('purohit/logout/', views.purohit_logout, name='purohit_logout'),
    path('purohit/signup/', views.purohit_signup, name='purohit_signup'),
    path('purohit/dashboard/', views.purohit_dashboard, name='purohit_dashboard'),
    path('purohit/edit-profile/', views.purohit_edit_profile, name='purohit_edit_profile'),
    path('purohit/forgot-password/', views.purohit_forgot_password, name='purohit_forgot_password'),
    path('purohit/verify-otp/', views.purohit_verify_otp, name='purohit_verify_otp'),
    path('purohit/reset-password/', views.purohit_reset_password, name='purohit_reset_password'),
    path('purohit/availability/', views.priest_availability, name='priest_availability'),
    path('purohit/bookings/', views.priest_bookings, name='priest_bookings'),
    path('api/availability/get/', views.api_get_availability, name='api_get_availability'),
    path('api/availability/save/', views.api_save_availability, name='api_save_availability'),
    
    # Booking URLs
    path('book/<slug:service_slug>/', views.book_service, name='book_service'),
    path('book/priest/<int:priest_id>/', views.book_priest, name='book_priest'),
    path('api/availability/public/<int:priest_id>/', views.api_public_priest_availability, name='api_public_priest_availability'),
    path('api/availability/service/<slug:service_slug>/', views.api_service_availability, name='api_service_availability'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('devotee/dashboard/', views.devotee_dashboard, name='devotee_dashboard'),

    # Devotee Forgot Password
    path('devotee/forgot-password/', views.devotee_forgot_password, name='devotee_forgot_password'),
    path('devotee/verify-otp/', views.devotee_verify_otp, name='devotee_verify_otp'),
    path('devotee/reset-password/', views.devotee_reset_password, name='devotee_reset_password'),

    # Admin Booking Management
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('admin-bookings/', views.admin_bookings_manage, name='admin_bookings_manage'),
    path('admin-bookings/<int:booking_id>/reassign/', views.admin_reassign_booking, name='admin_reassign_booking'),
    path('booking/<int:booking_id>/pdf/', views.generate_booking_pdf, name='generate_booking_pdf'),
    path('feedback/<uuid:token>/', views.feedback_form, name='feedback_form'),
    path('raise-enquiry/', views.raise_enquiry, name='raise_enquiry'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('api/notifications/mark-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
>>>>>>> 2efb7cacf3c38ae4a19cba1052ea6b35cd3fd4d3
]
