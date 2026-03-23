from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import PriestProfile, Booking
from django.utils import timezone
from datetime import datetime

class PriestDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.priest_user = User.objects.create_user(username='priest', email='priest@test.com', password='password123')
        self.priest_profile = PriestProfile.objects.create(
            user=self.priest_user,
            fullname="Test Priest",
            mobile="1234567890",
            experience=10,
            language=["Telugu"],
            location="Test Temple",
            services=['ganesh-homa']
        )
        self.devotee_user = User.objects.create_user(username='devotee', email='devotee@test.com', password='password123')

    def test_dashboard_booking_count_and_visibility(self):
        # Log in priest
        self.client.login(username='priest', password='password123')
        
        # Check initial count
        response = self.client.get(reverse('purohit_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total Bookings: 0")
        self.assertContains(response, "No upcoming bookings found")

        # Create a booking
        booking = Booking.objects.create(
            priest=self.priest_profile,
            devotee=self.devotee_user,
            service='ganesh-homa',
            booking_date=timezone.now().date() + timedelta(days=1),
            slot_type='morning',
            start_time="08:00:00",
            end_time="10:00:00",
            devotee_name="Test Devotee",
            devotee_phone="9876543210",
            devotee_address="Test Address",
            status='confirmed'
        )

        # Re-check dashboard
        response = self.client.get(reverse('purohit_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"Total Bookings: 1")
        self.assertContains(response, "Test Devotee")
        self.assertContains(response, "Ganesh Homa")
        self.assertContains(response, "Confirmed")

    def test_profile_edit_reflects_on_dashboard(self):
        # Log in priest
        self.client.login(username='priest', password='password123')
        
        # Prepare edit data
        edit_data = {
            'fullname': 'Updated Name',
            'mobile': '9999999999',
            'experience': 15,
            'language': 'Hindi',
            'location': 'Updated Location',
            'specialization': 'Updated Specialization',
            'services': ['satyanarayan-pooja']
        }
        
        # Post to edit profile
        response = self.client.post(reverse('purohit_edit_profile'), edit_data)
        if response.status_code != 302:
            print("Form errors:", response.context['form'].errors)
        self.assertEqual(response.status_code, 302) # Should redirect to dashboard
        
        # Check dashboard for updated values
        response = self.client.get(reverse('purohit_dashboard'))
        self.assertContains(response, 'Updated Name')
        self.assertContains(response, '9999999999')
        self.assertContains(response, '15 Years')
        self.assertContains(response, 'Hindi')
        self.assertContains(response, 'Updated Location')
        self.assertContains(response, 'Updated Specialization')
        self.assertContains(response, 'Satyanarayan Pooja')

    def test_availability_visibility_on_dashboard(self):
        from .models import PriestAvailability
        # Log in priest
        self.client.login(username='priest', password='password123')
        
        # Check initial dashboard
        response = self.client.get(reverse('purohit_dashboard'))
        self.assertContains(response, "No availability set for upcoming dates")

        # Create availability
        tomorrow = timezone.now().date() + timedelta(days=1)
        PriestAvailability.objects.create(
            priest=self.priest_profile,
            date=tomorrow,
            morning_available=True,
            morning_start="06:00:00",
            morning_end="12:00:00",
            notes="Morning shift"
        )

        # Re-check dashboard
        response = self.client.get(reverse('purohit_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saved Availability Slots")
        self.assertContains(response, str(tomorrow))
        self.assertContains(response, "Morning")
        self.assertContains(response, "Morning shift")

