from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import PostSerializer
from .models import Post, Like
from accounts.models import User
from accounts.serializers import UserSerializer


class PostListView(APIView):
    def get(self, request):
        ids = [request.user.id]
        for friend in request.user.friends.all():
            ids.append(friend.id)

        posts = Post.objects.filter(created_by_id__in=ids)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


class ProfilePostListView(APIView):
    def get(self, request, id):
        posts = Post.objects.filter(created_by_id=id)
        serializer = PostSerializer(posts, many=True)
        user = User.objects.get(id=id)
        return Response({"posts": serializer.data, "user": UserSerializer(user).data})


class PostCreateView(APIView):
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save(created_by=request.user)
            post.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)


class LikePostView(APIView):
    def post(self, request, id):
        post = get_object_or_404(Post, id=id)

        try:
            like = Like.objects.get(created_by=request.user, post=post)
        except Like.DoesNotExist:
            like = Like.objects.create(created_by=request.user, post=post)
            like.save()

            return Response(
                {
                    "likes": str(post.like_set.count()),
                    "message": "Successfully Liked.",
                },
                status=status.HTTP_200_OK,
            )

        like.delete()
        return Response(
            {"likes": str(post.like_set.count()), "message": "Successfully Unliked."},
            status=status.HTTP_200_OK,
        )
