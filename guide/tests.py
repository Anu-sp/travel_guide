from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import District, UserProfile , Place

class SimpleTest(TestCase):
    
    def test_home_template_for_logged_out_user(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guide/home.html')
        self.assertContains(response, 'Login')  # Ensure the "Login" button is present



class DistrictsPageTests(TestCase):
    
    def setUp(self):
        self.district1 = District.objects.create(name='District 1', image='path/to/image1.jpg')
        self.district2 = District.objects.create(name='District 2', image='path/to/image2.jpg')

    
    def test_districts_page_display(self):
        response = self.client.get('/district/')  # Adjust the URL according to your districts view
        self.assertEqual(response.status_code, 200)  # Ensure the page loads successfully
        self.assertContains(response, 'District 1')  # Check for presence of District 1
        self.assertContains(response, 'District 2')  # Check for presence of District 2


class DistrictPageTests(TestCase):

    def setUp(self):
        self.district = District.objects.create(name='Test District', image='path/to/image.jpg')
        self.place1 = Place.objects.create(name='Test Place 1', district=self.district)
        self.place2 = Place.objects.create(name='Test Place 2', district=self.district)


    def test_district_page_with_logged_out_user(self):
        # Access the district page without logging in
        response = self.client.get(reverse('district_detail', kwargs={'district_id': self.district.id}))

        # Check if the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check if the district name is in the response
        self.assertContains(response, 'Places to visit in Test District')

        # Check if the places are listed
        self.assertContains(response, 'Test Place 1')
        self.assertContains(response, 'Test Place 2')

        # Check if the login link is present
        self.assertContains(response, 'Login')

    def test_no_places_available(self):
        # Create a new district with no places
        empty_district = District.objects.create(name='Empty District', image='path/to/image.jpg')

       
        # Access the empty district page
        response = self.client.get(reverse('district_detail', kwargs={'district_id': empty_district.id}))

        # Check if the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check for the message when no places are available
        self.assertContains(response, 'No places available for this district.')


class PlaceDetailsTestCase(TestCase):
    def setUp(self):
        self.place = Place.objects.create(
            name='Test Place',
            description='A beautiful place to visit.',
            distance='10 km',
            best_time_to_visit='Spring',
            things_to_do='Hiking, Swimming',
            entry_fee='Free',
            timings='9 AM - 5 PM',
            how_to_reach='Bus, Car'
        )

    def test_place_details_view(self):
        # Test that the place details view works and renders the correct template
        url = reverse('place_detail', args=[self.place.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'place_details.html')
        self.assertContains(response, self.place.name)