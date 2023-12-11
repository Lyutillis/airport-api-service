from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    CrewViewSet,
    AirplaneTypeViewSet,
    OrderViewSet,
    RouteViewSet,
    AirplaneViewSet,
    FlightViewSet,
)


router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("crews", CrewViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("orders", OrderViewSet)
router.register("routes", RouteViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
