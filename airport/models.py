import os
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.core.validators import MinValueValidator


def airport_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airports/", filename)


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/airplanes/", filename)


class Country(models.Model):
    name = models.CharField(max_length=83, unique=True)

    class Meta:
        verbose_name_plural = "countries"
        ordering = ["name"]

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=83, unique=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities"
    )

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}/{self.country}"


class Airport(models.Model):
    name = models.CharField(max_length=133, unique=True)
    closest_big_city = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        related_name="airports"
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=airport_image_file_path
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.closest_big_city}: {self.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=83)
    last_name = models.CharField(max_length=83)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=133, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.DO_NOTHING,
        related_name="orders"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="destination_routes"
    )
    distance = models.IntegerField(validators=[MinValueValidator(10)])

    class Meta:
        unique_together = ("source", "destination")

    def __str__(self):
        return (
            f"{self.source.name} - "
            f"{self.destination.name} ({self.distance} km)"
        )


class Airplane(models.Model):
    name = models.CharField(max_length=133, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="airplanes"
    )
    image = models.ImageField(
        null=True, blank=True, upload_to=airplane_image_file_path
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def capacity(self):
        return self.rows * self.seats_in_row


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.DO_NOTHING, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.DO_NOTHING, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        unique_together = (
            "route", "airplane", "departure_time", "arrival_time"
        )
        ordering = ["departure_time"]

    def __str__(self):
        return f"{self.route} {self.departure_time}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight, on_delete=models.DO_NOTHING, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    def __str__(self):
        return str(self.flight)

    @staticmethod
    def validate_ticket(row, seat, flight, error_to_raise):
        for ticket_attr_value, ticket_attr_name, flight_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(flight, flight_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {flight_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )
