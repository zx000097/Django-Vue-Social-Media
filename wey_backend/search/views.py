from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.models import User
from accounts.serializers import UserSerializer


class SearchView(APIView):
    def post(self, request):
        users = User.objects.filter(name__icontains=request.data["query"])
        users_seralizer = UserSerializer(users, many=True)

        return Response(users_seralizer.data, status=status.HTTP_200_OK)
