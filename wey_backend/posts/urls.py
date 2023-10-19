from django.urls import path

from .views import PostListView

urlpatterns = [path("all-posts/", PostListView.as_view(), name="posts")]
