from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import uuid

from .models import User, FriendshipRequest


class UserManagerTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="normal@abc.com", name="normal", password="foo"
        )
        self.assertEqual(user.email, "normal@abc.com")
        self.assertEqual(user.name, "normal")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        with self.assertRaises(ValueError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="foo")

    def test_create_superuser(self):
        User = get_user_model()
        super_user = User.objects.create_superuser(
            email="super@abc.com", name="super", password="boo"
        )
        self.assertEqual(super_user.email, "super@abc.com")
        self.assertEqual(super_user.name, "super")
        self.assertTrue(super_user.is_active)
        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)

        with self.assertRaises(ValueError):
            User.objects.create_superuser(email="", password="foo")
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="some@email.com", name="some", password="foo", is_staff=False
            )
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="some@email.com", name="some", password="foo", is_superuser=False
            )


class SignUpViewTest(APITestCase):
    def test_create_user(self):
        url = reverse("signup")
        data = {
            "name": "hoho",
            "email": "hoho@gmail.com",
            "password1": "qpalzm102938",
            "password2": "qpalzm102938",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().name, "hoho")
        self.assertEqual(User.objects.get().email, "hoho@gmail.com")


class AddFriendViewTest(APITestCase):
    def setUp(self):
        self.to_be_added = User.objects.create_user(
            email="friend@abc.com", name="friend", password="foo"
        )
        self.myself = User.objects.create_user(
            email="myself@abc.com", name="myself", password="foo"
        )
        user_refresh_token = RefreshToken.for_user(self.myself)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_refresh_token.access_token}"
        )

    def test_add_friend(self):
        url = reverse("add_friend", kwargs={"id": self.to_be_added.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendshipRequest.objects.count(), 1)
        self.assertEqual(FriendshipRequest.objects.get().created_by.id, self.myself.id)
        self.assertEqual(
            FriendshipRequest.objects.get().created_for.id, self.to_be_added.id
        )
        self.assertEqual(self.myself.created_friendship_requests.count(), 1)
        self.assertEqual(self.myself.received_friendship_requests.count(), 0)
        self.assertEqual(self.to_be_added.created_friendship_requests.count(), 0)
        self.assertEqual(self.to_be_added.received_friendship_requests.count(), 1)

    def test_resend_friend_request(self):
        FriendshipRequest.objects.create(
            created_by=self.myself, created_for=self.to_be_added
        )
        url = reverse("add_friend", kwargs={"id": self.to_be_added.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sending_request_to_someone_that_has_sent_request_to_us(self):
        FriendshipRequest.objects.create(
            created_by=self.to_be_added, created_for=self.myself
        )
        url = reverse("add_friend", kwargs={"id": self.to_be_added.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sending_request_to_self(self):
        url = reverse("add_friend", kwargs={"id": self.myself.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetFriendsViewTest(APITestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(
            email="friend@abc.com", name="friend", password="foo"
        )
        self.user_b = User.objects.create_user(
            email="myself@abc.com", name="myself", password="foo"
        )
        FriendshipRequest.objects.create(
            created_for=self.user_a, created_by=self.user_b
        )
        user_b_refresh_token = RefreshToken.for_user(self.user_b)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_b_refresh_token.access_token}"
        )

    def test_get_requested_user(self):
        url = reverse("friends", kwargs={"id": self.user_a.id})
        response = self.client.get(url)
        user = response.data["user"]
        self.assertEqual(user["id"], str(self.user_a.id))

    def test_user_b_empty_friendship_request(self):
        url = reverse("friends", kwargs={"id": self.user_b.id})
        response = self.client.get(url)
        user = response.data["user"]
        requests = response.data["requests"]
        self.assertEqual(user["id"], str(self.user_b.id))
        self.assertTrue(not requests)

    def test_viewing_a_friendship_request_from_b_show_empty(self):
        url = reverse("friends", kwargs={"id": self.user_a.id})
        response = self.client.get(url)
        requests = response.data["requests"]
        self.assertTrue(not requests)

    def test_viewing_a_friendship_request_from_a_show_requests(self):
        user_refresh_token = RefreshToken.for_user(self.user_a)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_refresh_token.access_token}"
        )
        url = reverse("friends", kwargs={"id": self.user_a.id})
        response = self.client.get(url)
        requests = response.data["requests"]
        self.assertTrue(requests)
        self.assertTrue(requests[0]["created_for"]["id"], str(self.user_b.id))
        self.assertTrue(requests[0]["created_by"]["id"], str(self.user_a.id))
