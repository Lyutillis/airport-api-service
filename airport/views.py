from datetime import datetime
from rest_framework import viewsets, mixins, status
from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from airport.models import (
    Airport,
    Crew,
    AirplaneType,
    Order,
    Route,
    Airplane,
    Flight,
)
from airport.serializers import (
    AirportSerializer,
    AirportListSerializer,
    AirportDetailSerializer,
    CrewSerializer,
    CrewDetailSerializer,
    AirplaneTypeSerializer,
    OrderSerializer,
    OrderListSerializer,
    RouteSerializer,
    RouteListSerializer,
    AirplaneSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    AirportImageSerializer,
    AirplaneImageSerializer,
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly


class OrderPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 100


class AirportViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = (
        Airport.objects
        .select_related("closest_big_city")
        .annotate(
            routes_count=(
                Count("destination_routes")
            )
        )
    )
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_str(qs):
        """Converts a string with names to a list"""
        return [string for string in qs.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer

        if self.action == "retrieve":
            return AirportDetailSerializer
        
        if self.action == "upload_image":
            return AirportImageSerializer

        return AirportSerializer

    def get_queryset(self):
        """Retrieve the airports with filters"""
        dep_countries = self.request.query_params.get("dep_countries")
        dep_cities = self.request.query_params.get("dep_cities")
        dest_countries = self.request.query_params.get("dest_countries")
        dest_cities = self.request.query_params.get("dest_cities")
        
        queryset = self.queryset

        if dep_countries:
            dep_countries = self._params_to_str(dep_countries)
            queryset = queryset.filter(closest_big_city__country__name__in=dep_countries)

        if dep_cities:
            dep_cities = self._params_to_str(dep_cities)
            queryset = queryset.filter(closest_big_city__name__in=dep_cities)
        
        if dest_countries:
            dest_countries = self._params_to_str(dest_countries)
            queryset = queryset.filter(destination_routes__destination__closest_big_city__country__name__in=dest_countries)
        
        if dest_cities:
            dest_cities = self._params_to_str(dest_cities)
            queryset = queryset.filter(destination_routes__destination__closest_big_city__name__in=dest_cities)

        return queryset.distinct()

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific airport"""
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "dep_countries",
                type={"type": "list", "items": {"type": "string"}},
                description=(
                    "List of countries separated by commas that"
                    " resulting airports should be located in."
                ),
            ),
            OpenApiParameter(
                "dep_cities",
                type={"type": "list", "items": {"type": "string"}},
                description=(
                    "List of cities separated by commas that"
                    " resulting airports should be located near."
                ),
            ),
            OpenApiParameter(
                "dest_countries",
                type={"type": "list", "items": {"type": "string"}},
                description=(
                    "List of countries separated by commas that"
                    " resulting airports should have trips to."
                ),
            ),
            OpenApiParameter(
                "dest_cities",
                type={"type": "list", "items": {"type": "string"}},
                description=(
                    "List of cities separated by commas that"
                    " resulting airports should have trips to."
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = (
        Crew.objects
        .prefetch_related("flights")
        .annotate(
            flight_count=(
                Count("flights")
            )
        )
    )
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_int(qs):
        """Converts a string with names to a list"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_serializer_class(self):

        if self.action == "retrieve":
            return CrewDetailSerializer

        return CrewSerializer

    def get_queryset(self):
        """Retrieve the staff with filters"""
        flight_ids = self.request.query_params.get("flights")
        
        queryset = self.queryset

        if flight_ids:
            flight_ids = self._params_to_int(flight_ids)
            queryset = queryset.filter(flights__pk__in=flight_ids)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "flights",
                type={"type": "list", "items": {"type": "number"}},
                description=(
                    "List of flight ids separated by commas that"
                    " resulting staff should be assigned to."
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__route", "tickets__flight__airplane"
    )
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_str(qs):
        """Converts a string with names to a list"""
        return [string for string in qs.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        return RouteSerializer

    def get_queryset(self):
        """Retrieve the routes with filters"""
        dep_countries = self.request.query_params.get("dep_countries")
        dep_cities = self.request.query_params.get("dep_cities")
        dest_countries = self.request.query_params.get("dest_countries")
        dest_cities = self.request.query_params.get("dest_cities")
        
        queryset = self.queryset

        if dep_countries:
            dep_countries = self._params_to_str(dep_countries)
            queryset = queryset.filter(source__closest_big_city__country__name__in=dep_countries)

        if dep_cities:
            dep_cities = self._params_to_str(dep_cities)
            queryset = queryset.filter(source__closest_big_city__name__in=dep_cities)
        
        if dest_countries:
            dest_countries = self._params_to_str(dest_countries)
            queryset = queryset.filter(destination__closest_big_city__country__name__in=dest_countries)
        
        if dest_cities:
            dest_cities = self._params_to_str(dest_cities)
            queryset = queryset.filter(destination__closest_big_city__name__in=dest_cities)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "dep_countries",
                type={"type": "list", "items": {"type": "string"}},
                description=(
                    "List of countries separated by commas that"
                    " resulting routes should start in."
                ),
            ),
            OpenApiParameter(
                "dep_cities",
                type={"type": "list", "items": {"type": "string"}},
                description=(
                    "List of cities separated by commas that"
                    " resulting routes should start in near."
                ),
            ),
            OpenApiParameter(
                "dest_countries",
                type={"type": "list", "items": {"type": "string"}},
                description=(
                    "List of countries separated by commas that"
                    " resulting routes should be destinated to."
                ),
            ),
            OpenApiParameter(
                "dest_cities",
                type={"type": "list", "items": {"type": "string"}},
                description=(
                    "List of cities separated by commas that"
                    " resulting routes should be destinated to."
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific airplane"""
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("route", "airplane")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """Retrieve the flights with filters"""
        date = self.request.query_params.get("date")
        route = self.request.query_params.get("route")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if route:
            queryset = queryset.filter(route__id=int(route))

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                type=str,
                description="Filter flights by departure date.",
                required=False,
            ),
            OpenApiParameter(
                "route",
                type=int,
                description="Filter flights by route id.",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
