from django.test import TestCase

# Create your tests here.
from django.test import Client
from django.urls import reverse
from .models import User, Vehicle, Collection, BorrowRequest, Review

from django.test.utils import override_settings

from django.conf import settings
settings.STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

class TestSetupMixin:
    """
    Mixin to set up common test data for all tests.
    """
    def setUp(self):
        self.client = Client()

        # Create test users: one patron and one librarian.
        self.patron = User.objects.create_user(
            email="patron@example.com",
            password="testpass123",
            name="Test Patron",
            user_type="patron"
        )

        self.patron2 = User.objects.create_user(
            email="patron2@example.com",
            password="testpass123",
            name="Test Patron2",
            user_type="patron"
        )

        self.librarian = User.objects.create_user(
            email="librarian@example.com",
            password="testpass123",
            name="Test Librarian",
            user_type="librarian"
        )

        # Create a vehicle (lender is librarian)
        self.vehicle = Vehicle.objects.create(
            vehicle_type="car",
            lender=self.librarian,
            make="Toyota",
            model="Corolla",
            year="2022",
            description="A reliable car",
            location="Charlottesville",
            is_available=True
        )

        # Create two collections: one public and one private.
        self.public_collection = Collection.objects.create(
            name="Public Cars",
            description="Public vehicles available to all",
            private_collection=False,
            creator=self.librarian
        )
        self.private_collection = Collection.objects.create(
            name="Private Cars",
            description="Private collection only accessible by permitted users",
            private_collection=True,
            creator=self.librarian
        )
        self.public_collection.vehicles.add(self.vehicle)
        self.private_collection.vehicles.add(self.vehicle)
        # Give the patron access to the private collection.
        self.private_collection.users_with_access.add(self.patron)

class TestAuthentication(TestSetupMixin, TestCase):
    def test_logout_functionality(self):
        """
        Ensure that a logged in user can log out.
        """
        self.client.login(email="patron@example.com", password="testpass123")
        response = self.client.get(reverse('vehicleLending:sign_out'))
        self.assertEqual(response.status_code, 302)
        
class TestCollections(TestSetupMixin, TestCase):
    # def test_homepage_collection_visibility(self):
    #     """
    #     Ensure that the homepage (select_collection view) shows public collections.
    #     """
    #     response = self.client.get(reverse('vehicleLending:home'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, self.public_collection.name)

    def test_patron_cannot_create_private_collection(self):
        """
        A patron trying to create a collection should not be allowed to mark it private.
        (Based on current behavior, the private flag is only enabled if the creator is a librarian.)
        """
        self.client.login(email="patron@example.com", password="testpass123")
        response = self.client.post(reverse('vehicleLending:add_collection'), {
            "name": "New Collection",
            "description": "Test Description",
            "private_collection": True  # Patron should not be able to create a private collection
        })
        new_coll = Collection.objects.filter(name="New Collection").first()
        self.assertIsNotNone(new_coll)
        # Ensure that the new collection is not private since the creator is a patron.
        self.assertFalse(new_coll.private_collection)

    def test_librarian_can_create_private_collection(self):
        """
        A librarian should be able to create a private collection.
        """
        self.client.login(email="librarian@example.com", password="testpass123")
        response = self.client.post(reverse('vehicleLending:add_collection'), {
            "name": "Librarian Private Collection",
            "description": "Secret Vehicles",
            "private_collection": True
        })
        coll = Collection.objects.filter(name="Librarian Private Collection").first()
        self.assertIsNotNone(coll)
        self.assertTrue(coll.private_collection)

class TestVehicles(TestSetupMixin, TestCase):
    def test_patron_add_vehicle_fail(self):
        # Patron should be redirected/denied.
        self.client.login(email="patron@example.com", password="testpass123")
        response = self.client.get(reverse('vehicleLending:add_vehicle'))
        self.assertEqual(response.status_code, 302)

    def test_librarian_can_add_vehicle(self):
        """
        Ensure that only a librarian can add a vehicle.
        """
        # Librarian can add a vehicle.
        self.client.login(email="librarian@example.com", password="testpass123")
        response = self.client.post(reverse('vehicleLending:add_vehicle'), {
            "vehicle_type": "Car",
            "make": "Honda",
            "model": "Civic",
            "year": "2023",
            "location": "NY",
            "description": "Economical ride"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(make="Honda", model="Civic").exists())

class TestBorrowing(TestSetupMixin, TestCase):
    def test_borrow_request_flow_and_return(self):
        """
        Test that a patron can request a vehicle, the librarian can accept the request,
        and then the patron can return the vehicle.
        """
        # Patron requests to borrow.
        self.client.login(email="patron@example.com", password="testpass123")
        borrow_url = reverse('vehicleLending:request_borrow', args=[self.vehicle.id])
        response = self.client.get(borrow_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BorrowRequest.objects.filter(vehicle=self.vehicle, requester=self.patron).exists())

        # Librarian accepts the borrow request.
        borrow_request = BorrowRequest.objects.get(vehicle=self.vehicle, requester=self.patron)
        self.client.login(email="librarian@example.com", password="testpass123")
        response = self.client.get(reverse('vehicleLending:respond_to_request', args=[borrow_request.id, 'accept']))
        self.assertEqual(response.status_code, 302)
        borrow_request.refresh_from_db()
        self.assertEqual(borrow_request.status, 'accepted')
        self.vehicle.refresh_from_db()
        self.assertFalse(self.vehicle.is_available)

        # Patron returns the vehicle.
        self.client.login(email="patron@example.com", password="testpass123")
        return_url = reverse('vehicleLending:return_vehicle', args=[self.vehicle.id])
        response = self.client.get(return_url)
        self.assertEqual(response.status_code, 302)
        self.vehicle.refresh_from_db()
        self.assertTrue(self.vehicle.is_available)

class TestReviews(TestSetupMixin, TestCase):
    # def test_only_borrowers_can_leave_review(self):
    #     """
    #     Ensure that only users who have borrowed (and returned) the vehicle can leave a review.
    #     """
    #     self.client.login(email="patron2@example.com", password="testpass123")
    #     review_url = reverse('vehicleLending:details', args=[self.vehicle.id])
    #     # Attempt to leave a review without borrowing first.
    #     response = self.client.post(review_url, {"rating": 3, "comment": "Not allowed review"})
    #     print(Review.objects)
    #     self.assertEqual(Review.objects.count(), 0)

    def test_only_one_review_per_user(self):
        """
        Test that a patron who has borrowed and returned the vehicle can only submit one review.
        """
        # Simulate that the patron borrowed and returned the vehicle.
        borrow_request = BorrowRequest.objects.create(
            vehicle=self.vehicle, requester=self.patron, lender=self.librarian, status="accepted"
        )
        self.vehicle.is_available = False
        self.vehicle.save()
        # Patron returns the vehicle.
        self.client.login(email="patron@example.com", password="testpass123")
        self.client.get(reverse('vehicleLending:return_vehicle', args=[self.vehicle.id]))
        self.vehicle.refresh_from_db()
        self.assertTrue(self.vehicle.is_available)

        # Submit a review.
        review_url = reverse('vehicleLending:details', args=[self.vehicle.id])
        response = self.client.post(review_url, {"rating": 5, "comment": "Excellent ride!"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.filter(vehicle=self.vehicle, reviewer=self.patron).count(), 1)

        # Attempt a second review.
        response = self.client.post(review_url, {"rating": 4, "comment": "Trying to update."})
        self.assertEqual(Review.objects.filter(vehicle=self.vehicle, reviewer=self.patron).count(), 1)

    def test_review_visibility_and_deletion(self):
        """
        Test that a review is visible on the vehicle detail page and that the owner of the review
        can delete it.
        """
        # Make sure the patron has borrowed and returned (so review eligibility is met).
        BorrowRequest.objects.create(
            vehicle=self.vehicle, requester=self.patron, lender=self.librarian, status="accepted"
        )
        self.vehicle.is_available = False
        self.vehicle.save()
        self.client.login(email="patron@example.com", password="testpass123")
        self.client.get(reverse('vehicleLending:return_vehicle', args=[self.vehicle.id]))

        # Create a review.
        review = Review.objects.create(
            vehicle=self.vehicle,
            reviewer=self.patron,
            rating=5,
            comment="Great vehicle!"
        )
        # # Check that the review is on the detail page.
        # detail_url = reverse('vehicleLending:details', args=[self.vehicle.id])
        # response = self.client.get(detail_url)
        # self.assertContains(response, "Great vehicle!")

        # Delete the review.
        delete_url = reverse('vehicleLending:delete_review', args=[review.id])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

class TestPromotion(TestSetupMixin, TestCase):
    def test_promote_patron_to_librarian(self):
        """
        Test that a librarian can promote a patron.
        """
        self.client.login(email="librarian@example.com", password="testpass123")
        promote_url = reverse('vehicleLending:promote_patron')
        response = self.client.post(promote_url, {"patron_id": self.patron.id})
        self.assertEqual(response.status_code, 302)
        self.patron.refresh_from_db()
        self.assertEqual(self.patron.user_type, "librarian")

    def test_non_librarian_cannot_access_promotion(self):
        """
        Ensure that a non-librarian cannot access the promote patron view.
        """
        self.client.login(email="patron@example.com", password="testpass123")
        promote_url = reverse('vehicleLending:promote_patron')
        response = self.client.get(promote_url)
        # Should redirect (or show error), so status code should not be 200.
        self.assertNotEqual(response.status_code, 200)


print("Tests generated in tests.py")

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