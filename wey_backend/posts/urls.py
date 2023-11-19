from django.urls import path

from .views import (
    PostListView,
    PostCreateView,
    ProfilePostListView,
    LikePostView,
    PostDetailView,
    CreateCommentView,
)

urlpatterns = [
    path("", PostListView.as_view(), name="posts"),
    path("profile/<uuid:id>", ProfilePostListView.as_view(), name="profile_posts"),
    path("create", PostCreateView.as_view(), name="create_post"),
    path("<uuid:id>/like/", LikePostView.as_view(), name="like_post"),
    path("<uuid:id>/comment/", CreateCommentView.as_view(), name="create_comment"),
    path("<uuid:id>/", PostDetailView.as_view(), name="post_detail"),
]
