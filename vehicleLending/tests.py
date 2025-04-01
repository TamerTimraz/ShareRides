from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.urls import reverse
from .models import User, Vehicle, Collection

class VehicleLendingTests(TestCase):
    def setUp(self):
        """Set up test users, vehicles, and collections"""
        self.client = Client()
        
        # Create a test user (Patron)
        self.user_patron = User.objects.create_user(
            email="patron@example.com",
            password="testpass123",
            name="Test Patron",
            user_type="patron"
        )
        
        # Create a test user (Librarian)
        self.user_librarian = User.objects.create_user(
            email="librarian@example.com",
            password="testpass123",
            name="Test Librarian",
            user_type="librarian"
        )

        # Create a test vehicle
        self.vehicle = Vehicle.objects.create(
            vehicle_type="car",
            lender=self.user_patron,
            make="Toyota",
            model="Corolla",
            year="2020",
            description={"color": "red"},
            is_available=True
        )

        # Create a test collection
        self.collection = Collection.objects.create(
            name="Test Collection",
            description="A sample vehicle collection",
            private_collection=False
        )
        self.collection.vehicles.add(self.vehicle)  # Add vehicle to collection
"""
    def test_homepage_view(self):
        #Check if homepage loads correctly
        response = self.client.get(reverse('vehicleLending:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vehicleLending/select_collection.html')

    def test_login_page_loads(self):
        #Check if login page renders correctly
        response = self.client.get(reverse('vehicleLending:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vehicleLending/login.html')
"""
    """
    def test_add_vehicle_authenticated(self):
        Ensure a logged-in user can add a vehicle
        self.client.login(email="patron@example.com", password="testpass123")

        response = self.client.post(reverse('vehicleLending:add_vehicle'), {
            "vehicle_type": "truck",
            "make": "Ford",
            "model": "F-150",
            "year": "2022",
            "description": '{"color": "blue"}',
            "is_available": True
        })
        self.assertEqual(response.status_code, 302)  #redirect after adding vehicle

        #check if vehicle added
        self.assertTrue(Vehicle.objects.filter(make="Ford", model="F-150").exists())
    
    def test_add_vehicle_unauthenticated(self):
        Ensure unauthenticated users can still add a vehicle (per current behavior)
        response = self.client.post(reverse('vehicleLending:add_vehicle'), {
            "vehicle_type": "van",
            "make": "Honda",
            "model": "Odyssey",
            "year": "2023",
            "description": '{"color": "white"}',
            "is_available": True
        })
        self.assertEqual(response.status_code, 302)  #redirect after adding

        #check if vehicle added
        self.assertTrue(Vehicle.objects.filter(make="Honda", model="Odyssey").exists())
    
    def test_select_vehicle(self):
    #Check if vehicle selection page loads correctly
        response = self.client.get(reverse('vehicleLending:collection', args=["Test Collection"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota Corolla")  #ensure vehicle appears in page

    def test_item_description_page(self):
        #Check if item description page loads correctly
        response = self.client.get(reverse('vehicleLending:details', args=[self.vehicle.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Toyota Corolla")  #ensure vehicle details appear
        """

    def test_logout_functionality(self):
        """Ensure users can log out"""
        self.client.login(email="patron@example.com", password="testpass123")
        response = self.client.get(reverse('vehicleLending:sign_out'))
        self.assertEqual(response.status_code, 302)  #redirect to login page

