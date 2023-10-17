from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.generics import GenericAPIView

from .forms import SignupForm


class SignUpView(GenericAPIView):
    def post(self, request):
        data = request.data
        message = "sucess"

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
            message = "error"

        return JsonResponse({"status": message})
