from django.contrib import admin

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


admin.site.register(Country)
admin.site.register(City)
admin.site.register(Airport)
admin.site.register(Crew)
admin.site.register(AirplaneType)
admin.site.register(Order)
admin.site.register(Route)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Ticket)
