import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from airport.models import Country, City, Airport, Route
from airport.serializers import AirportDetailSerializer
from config.settings import BASE_DIR


AIRPORT_URL = reverse("airport:airport-list")

def detail_url(airport_id: int) -> str:
    return reverse("airport:airport-detail", args=[airport_id])

def upload_image_url(airport_id: int) -> str:
    return reverse("airport:airport-upload-image", args=[airport_id])

def sample_airport(**params):
    city_count = City.objects.count()
    city = City.objects.create(
        name=f"Test City {city_count}",
        country=Country.objects.create(
            name=f"Test Country {city_count}"
        )
    )
    defaults = {
        "name": f"Test Airport {city_count}",
        "closest_big_city": city
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airport(self):
        sample_airport()

        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_airport_filter(self):
        city1 = City.objects.create(
            name="City1",
            country=Country.objects.create(
                name="Country1"
            )
        )
        city2 = City.objects.create(
            name="City2",
            country=Country.objects.create(
                name="Country2"
            )
        )

        airport1 = sample_airport(name="Test Airport 1", closest_big_city=city1)
        airport2 = sample_airport(name="Test Airport 2", closest_big_city=city2)

        Route.objects.create(
            source = airport1,
            destination = airport2,
            distance = 100
        )
        Route.objects.create(
            source = airport2,
            destination = airport1,
            distance = 100
        )

        response1 = self.client.get(AIRPORT_URL, {"dep_countries": "Country1",})
        response2 = self.client.get(AIRPORT_URL, {"dep_cities": "City1",})
        response3 = self.client.get(AIRPORT_URL, {"dest_countries": "Country2",})
        response4 = self.client.get(AIRPORT_URL, {"dest_cities": "City2",})

        self.assertEqual(len(response1.data), 1)
        self.assertEqual(len(response2.data), 1)
        self.assertEqual(len(response3.data), 1)
        self.assertEqual(len(response4.data), 1)

    def test_retrieve_airport_detail(self):
        city1 = City.objects.create(
            name="City1",
            country=Country.objects.create(
                name="Country1"
            )
        )
        city2 = City.objects.create(
            name="City2",
            country=Country.objects.create(
                name="Country2"
            )
        )

        airport1 = sample_airport(name="Test Airport 1", closest_big_city=city1)
        airport2 = sample_airport(name="Test Airport 2", closest_big_city=city2)

        Route.objects.create(
            source = airport1,
            destination = airport2,
            distance = 100
        )
        Route.objects.create(
            source = airport2,
            destination = airport1,
            distance = 100
        )

        url = detail_url(airport1.pk)
        response = self.client.get(url)

        serializer = AirportDetailSerializer(airport1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_airport_upload_image_forbidden(self):
        airport = sample_airport()

        payload = {
            "image": SimpleUploadedFile(
                name="test_image.jpg",
                content=open(
                    os.path.join(BASE_DIR, "media", "test_image.jpg"), "rb"
                ).read(),
                content_type="image/jpg",
            )
        }

        response = self.client.post(upload_image_url(airport.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_airport_forbidden(self):
        payload = {
            "name": "Test Airport",
            "closest_big_city": City.objects.create(
                name="Test City",
                country=Country.objects.create(
                    name="Test Country"
                )
            )
        }

        response = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
    
    def test_create_airport(self):
        city = City.objects.create(
            name="Test City",
            country=Country.objects.create(
                name="Test Country"
            )
        )
        payload = {
            "name": "Test Airport",
            "closest_big_city": city.pk,
        }

        response = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(pk=response.data["id"])
        airport_city = airport.closest_big_city
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], airport.name)
        self.assertEqual(city, airport_city)

    def test_airport_upload_image(self):
        airport = sample_airport()

        payload = {
            "image": SimpleUploadedFile(
                name="test_image.jpg",
                content=open(
                    os.path.join(BASE_DIR, "media", "test_image.jpg"), "rb"
                ).read(),
                content_type="image/jpg",
            )
        }

        response = self.client.post(upload_image_url(airport.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(airport.image)
