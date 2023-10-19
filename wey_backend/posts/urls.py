from django.urls import path

from .views import PostListView, PostCreateView

urlpatterns = [
    path("", PostListView.as_view(), name="posts"),
    path("create", PostCreateView.as_view(), name="create"),
]
