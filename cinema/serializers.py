from rest_framework import serializers

from cinema.models import (
    Genre,
)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")
