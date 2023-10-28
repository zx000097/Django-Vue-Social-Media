from rest_framework import serializers
from accounts.serializers import UserSerializer
from django.utils.timesince import timesince

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField("format_created_at")
    likes_count = serializers.SerializerMethodField("get_likes_count")

    def format_created_at(self, post):
        return timesince(post.created_at)

    def get_likes_count(self, post):
        return post.like_set.count()

    class Meta:
        model = Post
        fields = ("id", "created_by", "body", "created_at", "likes_count")
