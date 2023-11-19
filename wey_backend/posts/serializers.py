from rest_framework import serializers
from accounts.serializers import UserSerializer
from django.utils.timesince import timesince

from .models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField("format_created_at")
    likes_count = serializers.SerializerMethodField("get_likes_count")
    comments_count = serializers.SerializerMethodField("get_comments_count")

    def format_created_at(self, post):
        return timesince(post.created_at)

    def get_likes_count(self, post):
        return post.like_set.count()

    def get_comments_count(self, post):
        return post.comment_set.count()

    class Meta:
        model = Post
        fields = (
            "id",
            "created_by",
            "body",
            "created_at",
            "likes_count",
            "comments_count",
        )


class CommentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField("format_created_at")

    def format_created_at(self, post):
        return timesince(post.created_at)

    class Meta:
        model = Comment
        fields = ("id", "body", "created_by", "created_at")


class PostDetailSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    created_by = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField("format_created_at")
    likes_count = serializers.SerializerMethodField("get_likes_count")
    comment_set = CommentSerializer(read_only=True, many=True)
    comments_count = serializers.SerializerMethodField("get_comments_count")

    def format_created_at(self, post):
        return timesince(post.created_at)

    def get_likes_count(self, post):
        return post.like_set.count()

    def get_comments_count(self, post):
        return post.comment_set.count()

    class Meta:
        model = Post
        fields = (
            "id",
            "created_by",
            "body",
            "created_at",
            "comment_set",
            "likes_count",
            "comments_count",
        )
