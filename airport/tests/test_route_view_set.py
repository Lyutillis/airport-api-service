import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from airport.models import Country, City, Airport, Route
from airport.serializers import RouteSerializer
from config.settings import MEDIA_ROOT


ROUTE_URL = reverse("airport:route-list")


def sample_route(**params):
    city1 = City.objects.create(
        name=f"Test City 1",
        country=Country.objects.create(
            name=f"Test Country 1"
        )
    )
    city2 = City.objects.create(
        name=f"Test City 2",
        country=Country.objects.create(
            name=f"Test Country 2"
        )
    )
    airport1 = Airport.objects.create(
        name="Test Airport1",
        closest_big_city=city1
    )
    airport2 = Airport.objects.create(
        name="Test Airport2",
        closest_big_city=city2
    )
    defaults = {
        "source": airport1,
        "destination": airport2,
        "distance": 100,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_route(self):
        sample_route()

        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_route_filter(self):
        route1 = sample_route()
        airport1 = route1.source
        airport2 = route1.destination
        Route.objects.create(
            source = airport2,
            destination = airport1,
            distance = 100
        )

        response1 = self.client.get(ROUTE_URL, {"dep_countries": "Test Country 1",})
        response2 = self.client.get(ROUTE_URL, {"dep_cities": "Test City 1",})
        response3 = self.client.get(ROUTE_URL, {"dest_countries": "Test Country 2",})
        response4 = self.client.get(ROUTE_URL, {"dest_cities": "Test City 2",})

        self.assertEqual(len(response1.data), 1)
        self.assertEqual(len(response2.data), 1)
        self.assertEqual(len(response3.data), 1)
        self.assertEqual(len(response4.data), 1)

    def test_create_route_forbidden(self):
        city1 = City.objects.create(
            name=f"Test City 1",
            country=Country.objects.create(
                name=f"Test Country 1"
            )
        )
        city2 = City.objects.create(
            name=f"Test City 2",
            country=Country.objects.create(
                name=f"Test Country 2"
            )
        )
        airport1 = Airport.objects.create(
            name="Test Airport1",
            closest_big_city=city1
        )
        airport2 = Airport.objects.create(
            name="Test Airport2",
            closest_big_city=city2
        )
        payload = {
            "source": airport1,
            "destination": airport2,
            "distance": 100,
        }

        response = self.client.post(ROUTE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
    
    def test_create_route(self):
        city1 = City.objects.create(
            name=f"Test City 1",
            country=Country.objects.create(
                name=f"Test Country 1"
            )
        )
        city2 = City.objects.create(
            name=f"Test City 2",
            country=Country.objects.create(
                name=f"Test Country 2"
            )
        )
        airport1 = Airport.objects.create(
            name="Test Airport1",
            closest_big_city=city1
        )
        airport2 = Airport.objects.create(
            name="Test Airport2",
            closest_big_city=city2
        )
        payload = {
            "source": airport1.pk,
            "destination": airport2.pk,
            "distance": 100,
        }

        response = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(pk=response.data["id"])
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["source"], route.source.pk)
        self.assertEqual(payload["destination"], route.destination.pk)
        self.assertEqual(payload["distance"], route.distance)
        