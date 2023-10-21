from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import User
from accounts.serializers import UserSerializer
from posts.models import Post
from posts.serializers import PostSerializer


class SearchView(APIView):
    def post(self, request):
        query = request.data["query"]
        users = User.objects.filter(name__icontains=query)
        users_seralizer = UserSerializer(users, many=True)

        posts = Post.objects.filter(body__icontains=query)
        posts_serializer = PostSerializer(posts, many=True)

        return Response(
            {
                "users": users_seralizer.data,
                "posts": posts_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
