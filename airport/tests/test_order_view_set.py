import os
import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from airport.models import Country, City, Airport, Route, Flight, Route, AirplaneType, Airplane, Crew, Order, Ticket
from airport.serializers import OrderSerializer, OrderListSerializer, TicketSerializer
from config.settings import MEDIA_ROOT


ORDER_URL = reverse("airport:order-list")


def sample_order(**params):
    defaults = {
        "user": None,
    }
    defaults.update(params)
    return Order.objects.create(**defaults)

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
        departure_time=timezone.now() + timezone.timedelta(days=2),
        arrival_time=timezone.now(),
    )

class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_orders(self):
        sample_order(user=self.user)

        response = self.client.get(ORDER_URL)
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    # def test_create_order(self):
    #     flight = sample_flight()
    #     payload = {
    #         "tickets": [1, 2],
    #     }

    #     response = self.client.post(ORDER_URL, payload)
    #     print(response.__dict__)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
