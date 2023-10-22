from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils import get_dict_values_string
from .forms import SignupForm
from .models import FriendshipRequest, User
from .serializers import UserSerializer, FrienshipRequestSerializer


class MeView(APIView):
    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "name": request.user.name,
                "email": request.user.email,
            }
        )


class SignUpView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data

        form = SignupForm(
            {
                "email": data.get("email"),
                "name": data.get("name"),
                "password1": data.get("password1"),
                "password2": data.get("password2"),
            }
        )

        if form.is_valid():
            form.save()
        else:
            return Response(
                {"errors": f"{get_dict_values_string(form.errors)}!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"status": "Successfully created user."}, status=status.HTTP_201_CREATED
        )


class AddFriendView(APIView):
    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        FriendshipRequest.objects.create(created_for=user, created_by=request.user)
        return Response(
            {"message": "friendship request created"},
            status=status.HTTP_201_CREATED,
        )


class GetFriendsView(APIView):
    def get(self, request, id):
        user = get_object_or_404(User, id=id)
        requests = []
        if user == request.user:
            requests = FriendshipRequest.objects.filter(created_for=request.user)
        friends = user.friends.all()
        return Response(
            {
                "user": UserSerializer(user).data,
                "friends": UserSerializer(friends, many=True).data,
                "requests": FrienshipRequestSerializer(requests, many=True).data,
            },
            status=status.HTTP_200_OK,
        )
