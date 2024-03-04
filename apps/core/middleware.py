from copy import deepcopy

from django.utils import timezone
from rest_framework.response import Response


class OCPIResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        data = deepcopy(response)

        response.data = {
            "data": data,
            "status_code": 1000,
            "status_message": "Generic success code",
            "timestamp": timezone.now().isoformat()
        }
        return response
