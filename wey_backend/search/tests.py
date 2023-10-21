from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


class SearchViewTest(APITestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create(
            name="user1", email="user1@gmail.com", password="test"
        )
        get_user_model().objects.create(
            name="user2", email="user2@gmail.com", password="test"
        )
        get_user_model().objects.create(
            name="abc", email="abc@gmail.com", password="test"
        )
        user1_refresh_token = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {user1_refresh_token.access_token}"
        )

    def test_search_return_query_result(self):
        url = reverse("search")
        response = self.client.post(url, {"query": "user"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(all("user" in user["name"] for user in response.data))
