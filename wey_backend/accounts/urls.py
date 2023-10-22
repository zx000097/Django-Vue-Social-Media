from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import SignUpView, MeView, AddFriendView, GetFriendsView

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("friends/<uuid:id>", GetFriendsView.as_view(), name="friends"),
    path("friends/<uuid:id>/request", AddFriendView.as_view(), name="add_friend"),
]
