from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Country,
    City,
    Airport,
    Crew,
    AirplaneType,
    Order,
    Route,
    Airplane,
    Flight,
    Ticket,
)


class AirportSerializer(serializers.ModelSerializer):
    country = serializers.CharField(
        max_length=83, source="closest_big_city.country.name", read_only=True
    )

    class Meta:
        model = Airport
        fields = ("id", "name", "country", "closest_big_city",)


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(
        many=False, slug_field="name", read_only=True
    )
    routes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "country",
            "closest_big_city",
            "routes_count",
            "image",
        )


class CrewSerializer(serializers.ModelSerializer):
    flight_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "flight_count",)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name",)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class RouteListSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class AirportRouteSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = serializers.CharField(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance",)


class AirportDetailSerializer(AirportSerializer):
    closest_big_city = serializers.SlugRelatedField(
        many=False, slug_field="name", read_only=True
    )
    source_routes = AirportRouteSerializer(many=True, read_only=True)
    destination_routes = AirportRouteSerializer(many=True, read_only=True)

    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "country",
            "closest_big_city",
            "source_routes",
            "destination_routes",
            "image",
        )


class AirportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "image",)


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image",)


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "image",
        )


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crews",
        )


class FlightListSerializer(FlightSerializer):
    airplane_name = serializers.CharField(
        source="airplane.name",
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)
    airplane_image = serializers.ImageField(
        source="airplane.image",
        read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "airplane_name",
            "airplane_image",
            "tickets_available",
        )


class CrewDetailSerializer(CrewSerializer):
    flights = FlightSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "flights",)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight",)


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(FlightSerializer):
    airplane = AirplaneSerializer(
        many=False,
        read_only=True
    )
    taken_places = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )
    route = RouteSerializer(
        many=False, read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "airplane",
            "route",
            "taken_places",
        )


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
