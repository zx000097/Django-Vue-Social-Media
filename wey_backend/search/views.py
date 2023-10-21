from rest_framework.views import APIView
from rest_framework.response import Response


class SearchView(APIView):
    def post(self, request):
        data = request.data
        query = data["query"]

        return Response
