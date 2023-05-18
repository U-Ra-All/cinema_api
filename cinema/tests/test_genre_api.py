from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cinema.models import Genre
from cinema.serializers import GenreSerializer

GENRE_URL = reverse("cinema:genre-list")


def sample_genre(**params):
    defaults = {
        "name": "Sample name",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


class UnauthenticatedGenreApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(GENRE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedGenreApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_genres(self):
        sample_genre()
        sample_genre(name="Sample1 name")
        sample_genre(name="Sample2 name")

        response = self.client.get(GENRE_URL)
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_genre_forbidden(self):
        payload = {
            "name": "Sample name",
        }

        response = self.client.post(GENRE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminGenreApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_genre(self):
        payload = {
            "name": "Sample name",
        }

        response = self.client.post(GENRE_URL, payload)
        genre = Genre.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(genre, key))


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        sample_genre()

    def test_name_label(self):
        genre = Genre.objects.get(id=1)
        field_label = genre._meta.get_field("name").verbose_name
        self.assertEqual(field_label, "name")

    def test_name_max_length(self):
        genre = Genre.objects.get(id=1)
        max_length = genre._meta.get_field("name").max_length
        self.assertEqual(max_length, 255)

    def test_genre_str(self):
        genre = Genre.objects.get(id=1)
        expected_object_name = f"{genre.name}"
        self.assertEqual(str(genre), expected_object_name)

    def test_genre_name_is_unique(self):
        Genre.objects.create(name="Test")
        with self.assertRaises(IntegrityError):
            Genre.objects.create(name="Test")
