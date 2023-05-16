from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from cinema.models import Actor
from cinema.serializers import ActorSerializer

ACTOR_URL = reverse("cinema:actor-list")


def sample_actor(**params):
    defaults = {
        "first_name": "Sample first name",
        "last_name": "Sample last name",
    }
    defaults.update(params)

    return Actor.objects.create(**defaults)


class UnauthenticatedActorApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ACTOR_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedActorApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password"
        )
        self.client.force_authenticate(self.user)

    def test_list_actors(self):
        sample_actor()
        sample_actor(
            first_name="Sample1 first name",
            last_name="Sample1 last name",
        )
        sample_actor(
            first_name="Sample2 first name",
            last_name="Sample2 last name",
        )

        response = self.client.get(ACTOR_URL)
        actors = Actor.objects.all()
        serializer = ActorSerializer(actors, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_actor_forbidden(self):
        payload = {
            "first_name": "Sample first name",
            "last_name": "Sample last name",
        }

        response = self.client.post(ACTOR_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminActorApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test_password",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_actor(self):
        payload = {
            "first_name": "Sample first name",
            "last_name": "Sample last name",
        }

        response = self.client.post(ACTOR_URL, payload)
        actor = Actor.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(actor, key))


class ActorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        sample_actor()

    def test_first_name_label(self):
        actor = Actor.objects.get(id=1)
        field_label = actor._meta.get_field("first_name").verbose_name
        self.assertEqual(field_label, "first name")

    def test_last_name_label(self):
        actor = Actor.objects.get(id=1)
        field_label = actor._meta.get_field("last_name").verbose_name
        self.assertEqual(field_label, "last name")

    def test_first_name_max_length(self):
        actor = Actor.objects.get(id=1)
        max_length = actor._meta.get_field("first_name").max_length
        self.assertEqual(max_length, 255)

    def test_last_name_max_length(self):
        actor = Actor.objects.get(id=1)
        max_length = actor._meta.get_field("last_name").max_length
        self.assertEqual(max_length, 255)

    def test_actor_str(self):
        actor = Actor.objects.get(id=1)
        expected_object_name = f"{actor.first_name} {actor.last_name}"
        self.assertEqual(str(actor), expected_object_name)

    def test_actor_full_name(self):
        actor = Actor.objects.get(id=1)
        expected_full_name = actor.full_name
        self.assertEqual(expected_full_name, f"{actor.first_name} {actor.last_name}")
