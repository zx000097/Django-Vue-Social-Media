from rest_framework import serializers

from .models import User, FriendshipRequest


class UserSerializer(serializers.ModelSerializer):
    friends_count = serializers.SerializerMethodField("get_friends_count")

    def get_friends_count(self, user):
        return user.friends.count()

    class Meta:
        model = User
        fields = ("id", "name", "email", "friends_count")


class FrienshipRequestSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    created_for = UserSerializer(read_only=True)

    class Meta:
        model = FriendshipRequest
        fields = ("id", "created_by", "created_for")
