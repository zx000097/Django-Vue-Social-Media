from django.urls import path

from .views import PostListView, PostCreateView, ProfilePostListView

urlpatterns = [
    path("", PostListView.as_view(), name="posts"),
    path("profile/", ProfilePostListView.as_view(), name="profile_posts"),
    path("create", PostCreateView.as_view(), name="create"),
]
