from django.urls import path

from .views import PostListView, PostCreateView, ProfilePostListView, LikePostView

urlpatterns = [
    path("", PostListView.as_view(), name="posts"),
    path("profile/<uuid:id>", ProfilePostListView.as_view(), name="profile_posts"),
    path("create", PostCreateView.as_view(), name="create_post"),
    path("<uuid:id>/like/", LikePostView.as_view(), name="like_post"),
]
