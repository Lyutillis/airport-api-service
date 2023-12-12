import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from airport.models import Country, City, Airport, Route, Airplane, AirplaneType
from airport.serializers import AirportListSerializer, AirportDetailSerializer, AirplaneSerializer, AirplaneImageSerializer
from config.settings import MEDIA_ROOT


AIRPLANE_URL = reverse("airport:airplane-list")

def upload_image_url(airplane_id: int) -> str:
    return reverse("airport:airplane-upload-image", args=[airplane_id])

def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(
        name="Test Type"
    )
    defaults = {
        "name": "Test Airplane",
        "rows": 10,
        "seats_in_row": 8,
        "airplane_type": airplane_type,
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_airplane(self):
        sample_airplane()

        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        airplanes = Airplane.objects.all()
        serializer = AirplaneSerializer(airplanes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_airplane_upload_image_forbidden(self):
        airplane = sample_airplane()

        payload = {
            "image": SimpleUploadedFile(
                name="test_image.jpg",
                content=open(
                    os.path.join(MEDIA_ROOT, "test_image.jpg"), "rb"
                ).read(),
                content_type="image/jpg",
            )
        }

        response = self.client.post(upload_image_url(airplane.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_airplane_forbidden(self):
        airplane_type = AirplaneType.objects.create(
            name="Test Type"
        )
        payload = {
            "name": "Test Airplane",
            "rows": 10,
            "seats_in_row": 8,
            "airplane_type": airplane_type,
        }

        response = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)
    
    def test_create_airplane(self):
        payload_type = AirplaneType.objects.create(
            name="Test Type"
        )
        payload = {
            "name": "Test Airplane",
            "rows": 10,
            "seats_in_row": 8,
            "airplane_type": payload_type.pk,
        }

        response = self.client.post(AIRPLANE_URL, payload)
        airplane = Airplane.objects.get(pk=response.data["id"])
        airplane_type = airplane.airplane_type
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in ("name", "rows", "seats_in_row"):
            self.assertEqual(payload[key], getattr(airplane, key))
        self.assertEqual(payload_type, airplane_type)

    def test_airplane_upload_image(self):
        airplane = sample_airplane()

        payload = {
            "image": SimpleUploadedFile(
                name="test_image.jpg",
                content=open(
                    os.path.join(MEDIA_ROOT, "test_image.jpg"), "rb"
                ).read(),
                content_type="image/jpg",
            )
        }

        response = self.client.post(upload_image_url(airplane.pk), payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(airplane.image)
