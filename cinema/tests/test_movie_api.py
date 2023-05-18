from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from cinema.models import Movie, MovieSession, CinemaHall, Genre, Actor
from cinema.serializers import MovieListSerializer, MovieDetailSerializer

MOVIE_URL = reverse("cinema:movie-list")
MOVIE_SESSION_URL = reverse("cinema:moviesession-list")


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


def sample_movie_session(**params):
    cinema_hall = CinemaHall.objects.create(
        name="Blue", rows=20, seats_in_row=20
    )

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "movie": None,
        "cinema_hall": cinema_hall,
    }
    defaults.update(params)

    return MovieSession.objects.create(**defaults)


def image_upload_url(movie_id):
    """Return URL for recipe image upload"""
    return reverse("cinema:movie-upload-image", args=[movie_id])


def detail_url(movie_id):
    return reverse("cinema:movie-detail", args=[movie_id])


class UnauthenticatedMovieApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(MOVIE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMovieApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password"
        )
        self.client.force_authenticate(self.user)

    def test_filter_movies_by_title(self):
        movie1 = sample_movie(title="Title1")
        movie2 = sample_movie(title="Title2")

        response = self.client.get(MOVIE_URL, {"title": "Title1"})

        serializer1 = MovieListSerializer(movie1)
        serializer2 = MovieListSerializer(movie2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_filter_movies_by_actors(self):
        movie1 = sample_movie(title="Title1")
        movie2 = sample_movie(title="Title2")

        actor1 = Actor.objects.create(
            first_name="TestFirstName1",
            last_name="TestLastName1"
        )

        actor2 = Actor.objects.create(
            first_name="TestFirstName2",
            last_name="TestLastName2"
        )

        movie1.actors.add(actor1, actor2)

        response = self.client.get(MOVIE_URL, {"actors": f"{actor1.id},{actor2.id}"})

        serializer1 = MovieListSerializer(movie1)
        serializer2 = MovieListSerializer(movie2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_filter_movies_by_genres(self):
        movie1 = sample_movie(title="Title1")
        movie2 = sample_movie(title="Title2")

        genre1 = Genre.objects.create(
            name="TestName1",
        )

        genre2 = Genre.objects.create(
            name="TestName2",
        )

        movie1.genres.add(genre1, genre2)

        response = self.client.get(MOVIE_URL, {"genres": f"{genre1.id},{genre2.id}"})

        serializer1 = MovieListSerializer(movie1)
        serializer2 = MovieListSerializer(movie2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_retrieve_movie_detail(self):
        movie = sample_movie()
        movie.actors.add(Actor.objects.create(
            first_name="TestFirstName",
            last_name="TestLastName"
        ))
        movie.genres.add(Genre.objects.create(
            name="TestName1",
        ))

        url = detail_url(movie.id)
        response = self.client.get(url)
        serializer = MovieDetailSerializer(movie)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_movie_forbidden(self):
        payload = {
            "title": "Sample movie",
            "description": "Sample description",
            "duration": 90,
        }

        response = self.client.post(MOVIE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_movie(self):
        payload = {
            "title": "Sample movie",
            "description": "Sample description",
            "duration": 90,
        }

        response = self.client.post(MOVIE_URL, payload)
        movie = Movie.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))

    def test_create_movie_with_actors(self):
        actor1 = Actor.objects.create(
            first_name="TestFirstName1",
            last_name="TestLastName1"
        )

        actor2 = Actor.objects.create(
            first_name="TestFirstName2",
            last_name="TestLastName2"
        )

        payload = {
            "title": "Sample movie",
            "description": "Sample description",
            "duration": 90,
            "actors": [actor1.id, actor2.id]
        }

        response = self.client.post(MOVIE_URL, payload)
        movie = Movie.objects.get(id=response.data["id"])
        actors = movie.actors.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(actors.count(), 2)
        self.assertIn(actor1, actors)
        self.assertIn(actor2, actors)

    def test_create_movie_with_genres(self):
        genre1 = Genre.objects.create(
            name="TestName1",
        )

        genre2 = Genre.objects.create(
            name="TestName2",
        )

        payload = {
            "title": "Sample movie",
            "description": "Sample description",
            "duration": 90,
            "genres": [genre1.id, genre2.id]
        }

        response = self.client.post(MOVIE_URL, payload)
        movie = Movie.objects.get(id=response.data["id"])
        genres = movie.genres.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(genres.count(), 2)
        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)

    def test_create_movie_with_actors_and_genres(self):
        actor1 = Actor.objects.create(
            first_name="TestFirstName1",
            last_name="TestLastName1"
        )

        actor2 = Actor.objects.create(
            first_name="TestFirstName2",
            last_name="TestLastName2"
        )

        genre1 = Genre.objects.create(
            name="TestName1",
        )

        genre2 = Genre.objects.create(
            name="TestName2",
        )

        payload = {
            "title": "Sample movie",
            "description": "Sample description",
            "duration": 90,
            "actors": [actor1.id, actor2.id],
            "genres": [genre1.id, genre2.id]
        }

        response = self.client.post(MOVIE_URL, payload)
        movie = Movie.objects.get(id=response.data["id"])
        actors = movie.actors.all()
        genres = movie.genres.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(actors.count(), 2)
        self.assertIn(actor1, actors)
        self.assertIn(actor2, actors)
        self.assertEqual(genres.count(), 2)
        self.assertIn(genre1, genres)
        self.assertIn(genre2, genres)

    def test_delete_movie_not_allowed(self):
        movie = sample_movie()
        url = detail_url(movie.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class MovieModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        sample_movie()

    def test_title_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field("title").verbose_name
        self.assertEqual(field_label, "title")

    def test_description_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field("description").verbose_name
        self.assertEqual(field_label, "description")

    def test_duration_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field("duration").verbose_name
        self.assertEqual(field_label, "duration")

    def test_genres_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field("genres").verbose_name
        self.assertEqual(field_label, "genres")

    def test_actors_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field("actors").verbose_name
        self.assertEqual(field_label, "actors")

    def test_image_label(self):
        movie = Movie.objects.get(id=1)
        field_label = movie._meta.get_field("image").verbose_name
        self.assertEqual(field_label, "image")

    def test_title_max_length(self):
        movie = Movie.objects.get(id=1)
        max_length = movie._meta.get_field("title").max_length
        self.assertEqual(max_length, 255)

    def test_movie_str(self):
        movie = Movie.objects.get(id=1)
        expected_object_name = f"{movie.title}"
        self.assertEqual(str(movie), expected_object_name)
