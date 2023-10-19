from rest_framework import serializers
from accounts.serializers import UserSerializer
from django.utils.timesince import timesince

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField("format_created_at")

    def format_created_at(self, post):
        return timesince(post.created_at)

    class Meta:
        model = Post
        fields = ("id", "created_by", "body", "created_at")
