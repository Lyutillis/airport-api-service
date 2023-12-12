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
router.register("airports", AirportViewSet, "airport")
router.register("crews", CrewViewSet, "crew")
router.register("airplane-types", AirplaneTypeViewSet, "airplane-type")
router.register("orders", OrderViewSet, "order")
router.register("routes", RouteViewSet, "route")
router.register("airplanes", AirplaneViewSet, "airplane")
router.register("flights", FlightViewSet, "flight")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport"
