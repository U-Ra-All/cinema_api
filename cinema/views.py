from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from cinema.models import Genre
from cinema.serializers import GenreSerializer


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
