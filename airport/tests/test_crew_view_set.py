import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from airport.models import Country, City, Airport, Route, Crew, Route, Airplane, Flight, AirplaneType
from airport.serializers import CrewSerializer, CrewDetailSerializer, AirportDetailSerializer
from config.settings import MEDIA_ROOT


CREW_URL = reverse("airport:crew-list")

def detail_url(crew_id: int) -> str:
    return reverse("airport:crew-detail", args=[crew_id])


def sample_crew(**params):
    defaults = {
        "first_name": f"Test Crew",
        "last_name": "Test Crew"
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)

def sample_flight():
    city = City.objects.create(
        name="Test City",
        country=Country.objects.create(
            name="Test Country"
        )
    )
    airport1 = Airport.objects.create(
        name="Test Airport 1",
        closest_big_city=city,
    )
    airport2 = Airport.objects.create(
        name="Test Airport 2",
        closest_big_city=city,
    )
    route = Route.objects.create(
        source=airport1,
        destination=airport2,
        distance=100
    )
    airplane = Airplane.objects.create(
        name="Test Airplane",
        rows=10,
        seats_in_row=8,
        airplane_type=AirplaneType.objects.create(
            name="Test type"
        )
    )
    return Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=timezone.now(),
        arrival_time=timezone.now(),
    )


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_crew(self):
        sample_crew()

        response = self.client.get(CREW_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_crew_filter(self):
        flight = sample_flight()
        crew1 = sample_crew(first_name="Crew1")
        sample_crew(first_name="Crew2")
        flight.crews.add(crew1)

        response = self.client.get(CREW_URL, {"flights": flight.pk,})


        self.assertEqual(len(response.data), 1)

    def test_retrieve_crew_detail(self):
        flight = sample_flight()
        crew1 = sample_crew(first_name="Crew1")
        flight.crews.add(crew1)

        url = detail_url(crew1.pk)
        response = self.client.get(url)

        serializer = CrewDetailSerializer(crew1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
    
    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Test Crew",
            "last_name": "Test Crew",
        }

        response = self.client.post(CREW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
    
    def test_create_crew(self):
        payload = {
            "first_name": "Test Crew",
            "last_name": "Test Crew",
        }

        response = self.client.post(CREW_URL, payload)
        crew = Crew.objects.get(pk=response.data["id"])
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["first_name"], crew.first_name)
        self.assertEqual(payload["last_name"], crew.last_name)
