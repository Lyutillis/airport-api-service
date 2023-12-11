from django.db import models
from django.contrib.auth import get_user_model


class Airport(models.Model):
    name = models.CharField(max_length=133)
    closest_big_city = models.CharField(max_length=133)


class Crew(models.Model):
    first_name = models.CharField(max_length=83)
    last_name = models.CharField(max_length=83)


class AirplaneType(models.Model):
    name = models.CharField(max_length=133)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE)
    distance = models.IntegerField()


class Airplane(models.Model):
    name = models.CharField(max_length=133)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.SET_NULL, null=True)


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.DO_NOTHING)
    airplane = models.ForeignKey(Airplane, on_delete=models.DO_NOTHING)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
