from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PostSerializer
from .models import Post


class PostListView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
