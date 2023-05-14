from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from cinema.models import (
    CinemaHall,
    Genre,
)
from cinema.serializers import (
    CinemaHallSerializer,
    GenreSerializer,
)


class CinemaHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
