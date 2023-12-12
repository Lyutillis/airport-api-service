import os
import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from airport.models import Country, City, Airport, Route, Flight, Route, AirplaneType, Airplane, Crew
from airport.serializers import FlightListSerializer, FlightDetailSerializer
from config.settings import MEDIA_ROOT


FLIGHT_URL = reverse("airport:flight-list")

def detail_url(flight_id: int) -> str:
    return reverse("airport:flight-detail", args=[flight_id])

def sample_flights():
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
    route1 = Route.objects.create(
        source=airport1,
        destination=airport2,
        distance=100
    )
    route2 = Route.objects.create(
        source=airport2,
        destination=airport1,
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
        route=route1,
        airplane=airplane,
        departure_time=timezone.now() + timezone.timedelta(days=2),
        arrival_time=timezone.now(),
    ), Flight.objects.create(
        route=route2,
        airplane=airplane,
        departure_time=timezone.now(),
        arrival_time=timezone.now(),
    )


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_flight(self):
        sample_flights()

        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_flight_filter(self):
        flight1, flight2 = sample_flights()

        response1 = self.client.get(FLIGHT_URL, {
                "date": datetime.datetime.strftime(flight1.departure_time, "%Y-%m-%d"),
            })
        response2 = self.client.get(FLIGHT_URL, {"route": flight2.route.pk,})
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response1.data), 1)
        self.assertEqual(len(response2.data), 1)

    def test_retrieve_flight_detail(self):
        flight, _ = sample_flights()

        url = detail_url(flight.pk)
        response = self.client.get(url)

        serializer = FlightDetailSerializer(flight)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_flight_forbidden(self):
        flight, _ = sample_flights()
        payload = {
            "route":flight.route,
            "airplane": flight.airplane,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now(),
        }

        response = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_flight_forbidden(self):
        flight, update_data = sample_flights()
        payload = {
            "route": update_data.route,
            "airplane": update_data.airplane,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now(),
        }

        response = self.client.put(detail_url(flight.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_partial_update_flight_forbidden(self):
        flight, update_data = sample_flights()
        payload = {
            "route": update_data.route,
        }

        response = self.client.patch(detail_url(flight.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_flight_forbidden(self):
        flight, _ = sample_flights()

        response = self.client.delete(detail_url(flight.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
    
    def test_create_flight(self):
        flight, _ = sample_flights()
        payload = {
            "route":flight.route.pk,
            "airplane": flight.airplane.pk,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now(),
            "crews": [Crew.objects.create(
                first_name="Test",
                last_name="Crew",
            ).pk],
        }

        response = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.get(pk=response.data["id"])
        route = flight.route
        airplane = flight.airplane
        crews = flight.crews
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["departure_time"], flight.departure_time)
        self.assertEqual(payload["arrival_time"], flight.arrival_time)
        self.assertEqual(payload["route"], route.pk)
        self.assertEqual(payload["airplane"], airplane.pk)
        self.assertEqual(payload["crews"], [crew.pk for crew in flight.crews.all()])
        

    def test_update_flight(self):
        flight, update_data = sample_flights()
        payload = {
            "route": update_data.route.pk,
            "airplane": update_data.airplane.pk,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now(),
            "crews": [
                Crew.objects.create(
                    first_name="Test",
                    last_name="Crew",
                ).pk
            ]
        }

        response = self.client.put(detail_url(flight.pk), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_partial_update_flight(self):
        flight, update_data = sample_flights()
        payload = {
            "route": update_data.route.pk,
        }

        response = self.client.patch(detail_url(flight.pk), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_flight(self):
        flight, _ = sample_flights()

        response = self.client.delete(detail_url(flight.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
