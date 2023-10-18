from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .utils import get_dict_values_string
from .forms import SignupForm


class MeView(APIView):
    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "name": request.user.name,
                "email": request.user.email ,
            }
        )


class SignUpView(APIView):
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
