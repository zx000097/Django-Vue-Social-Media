from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Post


class ProfilePostListViewTests(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            name="testuser", email="testuser@gmail.com", password="test"
        )
        self.user2 = get_user_model().objects.create_user(
            name="another testuser", email="anothertestuser@gmail.com", password="test"
        )
        Post.objects.get_or_create(body="Something", created_by=self.user1)
        Post.objects.get_or_create(body="Something2", created_by=self.user1)
        Post.objects.get_or_create(body="Something", created_by=self.user2)
        user1_refresh_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user1_refresh_token.access_token}"
        )

    def test_posts_only_from_current_user(self):
        url = reverse("profile_posts")
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 2)
        for dict in response.data:
            self.assertEquals(dict["created_by"]["id"], str(self.user1.id))
