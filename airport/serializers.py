from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airport,
    Crew,
    AirplaneType,
    Order,
    Route,
    Airplane,
    Flight,
    Ticket,
)


class Airport(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("name", "closest_big_city")
