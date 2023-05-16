from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from cinema.models import MovieSession, CinemaHall, Genre, Actor, Movie
from cinema.serializers import MovieSessionListSerializer

MOVIE_SESSION_URL = reverse("cinema:moviesession-list")


def sample_movie_session(**params):
    cinema_hall = sample_cinema_hall()
    movie = sample_movie()

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "movie": movie,
        "cinema_hall": cinema_hall,
    }
    defaults.update(params)

    return MovieSession.objects.create(**defaults)


def sample_cinema_hall(**params):
    defaults = {
        "name": "Sample name",
        "rows": 20,
        "seats_in_row": 20,
    }
    defaults.update(params)

    return CinemaHall.objects.create(**defaults)


def sample_movie(**params):
    defaults = {
        "title": "Sample movie",
        "description": "Sample description",
        "duration": 90,
    }
    defaults.update(params)

    return Movie.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "George", "last_name": "Clooney"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


def detail_url(movie_session_id):
    return reverse("cinema:moviesession-detail", args=[movie_session_id])


class UnauthenticatedMovieSessionApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(MOVIE_SESSION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMovieSessionApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password"
        )
        self.client.force_authenticate(self.user)

    def test_filter_movie_sessions_by_movie(self):
        movie_session1 = sample_movie_session(
            movie=sample_movie(title="TestTitle1"),
        )
        movie_session2 = sample_movie_session(
            movie=sample_movie(title="TestTitle2")
        )

        print(MovieSession.objects.all())

        response = self.client.get(MOVIE_SESSION_URL, {"movie.title": "TestTitle1"})

        serializer1 = MovieSessionListSerializer(movie_session1)
        serializer2 = MovieSessionListSerializer(movie_session2)

        print(f"serializer1.data: {serializer1.data}, response.data: {response.data}")

        self.assertEqual(serializer1.data.get("movie_title"), response.data[0]["movie_title"])
        self.assertNotEqual(serializer2.data.get("movie_title"), response.data[0]["movie_title"])

    def test_filter_movie_sessions_by_date(self):
        movie_session1 = sample_movie_session(
            show_time="2022-05-02 15:00:00",
        )
        movie_session2 = sample_movie_session()

        response = self.client.get(MOVIE_SESSION_URL, {"date": "2022-05-02"})

        serializer1 = MovieSessionListSerializer(movie_session1)
        serializer2 = MovieSessionListSerializer(movie_session2)

        self.assertEqual(serializer1.data.get("show_time")[:10], response.data[0]["show_time"][:10])
        self.assertNotEqual(serializer2.data.get("show_time")[:10], response.data[0]["show_time"][:10])

    def test_retrieve_movie_session_detail(self):
        movie_session = sample_movie_session()

        url = detail_url(movie_session.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_movie_session_forbidden(self):
        cinema_hall = sample_cinema_hall()
        movie = sample_movie()

        payload = {
            "show_time": "2022-06-02 14:00:00",
            "movie": movie,
            "cinema_hall": cinema_hall,
        }

        response = self.client.post(MOVIE_SESSION_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieSessionApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_movie_session(self):
        cinema_hall = sample_cinema_hall()
        movie = sample_movie()

        payload = {
            "show_time": "2022-06-02 14:00:00",
            "movie": movie.id,
            "cinema_hall": cinema_hall.id,
        }

        response = self.client.post(MOVIE_SESSION_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class MovieSessionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        sample_movie_session()

    def test_show_time_label(self):
        movie_session = MovieSession.objects.get(id=1)
        field_label = movie_session._meta.get_field("show_time").verbose_name
        self.assertEqual(field_label, "show time")

    def test_movie_label(self):
        movie_session = MovieSession.objects.get(id=1)
        field_label = movie_session._meta.get_field("movie").verbose_name
        self.assertEqual(field_label, "movie")

    def test_cinema_hall_label(self):
        movie_session = MovieSession.objects.get(id=1)
        field_label = movie_session._meta.get_field("cinema_hall").verbose_name
        self.assertEqual(field_label, "cinema hall")

    def test_movie_session_str(self):
        movie_session = MovieSession.objects.get(id=1)
        expected_object_name = f"{movie_session.movie.title} {movie_session.show_time}"
        self.assertEqual(str(movie_session), expected_object_name)
