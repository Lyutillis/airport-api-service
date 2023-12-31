import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer


AIRPLANE_TYPE_URL = reverse("airport:airplane-type-list")

def sample_airplane_type(**params):
    defaults = {
        "name": f"Test AirPlane type",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


class UnauthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane_type(self):
        sample_airplane_type()

        response = self.client.get(AIRPLANE_TYPE_URL)

        types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "Test Type",
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirPlaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
    
    def test_create_airplane_type(self):
        payload = {
            "name": "Test Type",
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        airplane_type = AirplaneType.objects.get(pk=response.data["id"])
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], airplane_type.name)
