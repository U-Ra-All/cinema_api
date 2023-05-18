from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cinema.models import CinemaHall
from cinema.serializers import CinemaHallSerializer

CINEMA_HALL_URL = reverse("cinema:cinemahall-list")


def sample_cinema_hall(**params):
    defaults = {
        "name": "Sample name",
        "rows": 20,
        "seats_in_row": 20,
    }
    defaults.update(params)

    return CinemaHall.objects.create(**defaults)


class UnauthenticatedCinemaHallApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(CINEMA_HALL_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCinemaHallApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_cinema_halls(self):
        sample_cinema_hall()
        sample_cinema_hall(name="Sample1 name", rows=10, seats_in_row=20)
        sample_cinema_hall(name="Sample2 name", rows=20, seats_in_row=30)

        response = self.client.get(CINEMA_HALL_URL)
        cinema_halls = CinemaHall.objects.all()
        serializer = CinemaHallSerializer(cinema_halls, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_cinema_hall_forbidden(self):
        payload = {
            "name": "Sample name",
            "rows": 20,
            "seats_in_row": 20,
        }

        response = self.client.post(CINEMA_HALL_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCinemaHallApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_cinema_hall(self):
        payload = {
            "name": "Sample name",
            "rows": 20,
            "seats_in_row": 20,
        }

        response = self.client.post(CINEMA_HALL_URL, payload)
        cinema_hall = CinemaHall.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(cinema_hall, key))


class CinemaHallModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        sample_cinema_hall()

    def test_name_label(self):
        cinema_hall = CinemaHall.objects.get(id=1)
        field_label = cinema_hall._meta.get_field("name").verbose_name
        self.assertEqual(field_label, "name")

    def test_rows_label(self):
        cinema_hall = CinemaHall.objects.get(id=1)
        field_label = cinema_hall._meta.get_field("rows").verbose_name
        self.assertEqual(field_label, "rows")

    def test_seats_in_row_label(self):
        cinema_hall = CinemaHall.objects.get(id=1)
        field_label = cinema_hall._meta.get_field("seats_in_row").verbose_name
        self.assertEqual(field_label, "seats in row")

    def test_name_max_length(self):
        cinema_hall = CinemaHall.objects.get(id=1)
        max_length = cinema_hall._meta.get_field("name").max_length
        self.assertEqual(max_length, 255)

    def test_cinema_hall_str(self):
        cinema_hall = CinemaHall.objects.get(id=1)
        expected_object_name = f"{cinema_hall.name}"
        self.assertEqual(str(cinema_hall), expected_object_name)

    def test_cinema_hall_capacity(self):
        cinema_hall = CinemaHall.objects.get(id=1)
        expected_capacity = cinema_hall.capacity
        self.assertEqual(expected_capacity, cinema_hall.rows * cinema_hall.seats_in_row)
