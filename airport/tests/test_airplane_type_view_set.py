import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from airport.models import Country, City, Airport, Route, AirplaneType
from airport.serializers import AirplaneTypeSerializer
from config.settings import MEDIA_ROOT


AIRPLANE_TYPE_URL = reverse("airport:airplane-types-list")

def detail_url(type_id: int) -> str:
    return reverse("airport:airplane-type-detail", args=[type_id])

def upload_image_url(type_id: int) -> str:
    return reverse("airport:airplane-type-upload-image", args=[type_id])

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

    def test_retrieve_airplane_type_detail(self):
        airplane_type = sample_airplane_type()

        url = detail_url(airplane_type.pk)
        response = self.client.get(url)

        serializer = AirplaneType(airplane_type)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
    
    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "Test Type",
        }

        response = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_airplane_type_forbidden(self):
        airplane_type = sample_airplane_type()
        payload = {
            "name": "Change Type",
        }

        response = self.client.put(detail_url(airplane_type.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_partial_update_airplane_type_forbidden(self):
        airplane_type = sample_airplane_type()
        payload = {
            "name": "Change Type",
        }

        response = self.client.patch(detail_url(sample_airplane_type.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_airplane_type_forbidden(self):
        airplane_type = sample_airplane_type()

        response = self.client.delete(detail_url(airplane_type.pk))

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
