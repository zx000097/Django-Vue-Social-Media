from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .models import Post


class PostListViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            name="testuser", email="testuser@gmail.com", password="test"
        )
        self.friend = get_user_model().objects.create_user(
            name="another testuser", email="friend@gmail.com", password="test"
        )
        self.not_friend = get_user_model().objects.create_user(
            name="not friend", email="notfriend@gmail.com", password="test"
        )
        Post.objects.get_or_create(body="By myself", created_by=self.user)
        Post.objects.get_or_create(body="By myself-2", created_by=self.user)
        Post.objects.get_or_create(body="By friend", created_by=self.friend)
        Post.objects.get_or_create(body="By friend-2", created_by=self.friend)
        Post.objects.get_or_create(body="By not friend", created_by=self.not_friend)
        user1_refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user1_refresh_token.access_token}"
        )

    def test_get_self_posts_when_no_friends(self):
        url = reverse("posts")
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data), 2)
        self.assertTrue(
            all(post["created_by"]["id"] == str(self.user.id) for post in response.data)
        )

    def test_get_self_and_friends_post(self):
        self.user.friends.add(self.friend)
        url = reverse("posts")
        response = self.client.get(url)
        self.assertEquals(response.status_code, status.HTTP_200_OK)
        self.assertEquals(len(response.data), 4)
        self.assertTrue(
            all(
                post["created_by"]["id"] != str(self.not_friend.id)
                for post in response.data
            )
        )
        self.assertTrue(
            any(
                post["created_by"]["id"] == str(self.friend.id)
                for post in response.data
            )
        )
        self.assertTrue(
            any(post["created_by"]["id"] == str(self.user.id) for post in response.data)
        )


class ProfilePostListViewTests(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            name="testuser", email="testuser@gmail.com", password="test"
        )
        self.user2 = get_user_model().objects.create_user(
            name="another testuser", email="anothertestuser@gmail.com", password="test"
        )
        Post.objects.get_or_create(body="Something", created_by=self.user1)
        Post.objects.get_or_create(body="Something2", created_by=self.user2)
        Post.objects.get_or_create(body="Something", created_by=self.user2)
        user1_refresh_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user1_refresh_token.access_token}"
        )

    def test_posts_only_from_given_id(self):
        url = reverse("profile_posts", kwargs={"id": self.user2.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data["posts"]), 2)
        for post in response.data["posts"]:
            self.assertEquals(post["created_by"]["id"], str(self.user2.id))
        self.assertEqual(response.data["user"]["id"], str(self.user2.id))

    def test_empty_post_still_return_profile_user(self):
        another_user = get_user_model().objects.create_user(
            name="anotherrrr testuser",
            email="anotherrrtestuser@gmail.com",
            password="test",
        )
        url = reverse("profile_posts", kwargs={"id": another_user.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data["posts"]), 0)
        self.assertEqual(response.data["user"]["id"], str(another_user.id))


class PostCreateViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            name="testuser", email="testuser@gmail.com", password="test"
        )

        user_refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user_refresh_token.access_token}"
        )

    def test_create_post(self):
        url = reverse("create_post")
        response = self.client.post(url, {"created_by": self.user, "body": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["body"], "Hello")
        self.assertEqual(response.data["created_by"]["id"], str(self.user.id))

    def test_create_post_fail_without_token(self):
        self.client.credentials()
        url = reverse("create_post")
        response = self.client.post(url, {"created_by": self.user, "body": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_fail_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer randomtoken12345")
        url = reverse("create_post")
        response = self.client.post(url, {"created_by": self.user, "body": "Hello"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
