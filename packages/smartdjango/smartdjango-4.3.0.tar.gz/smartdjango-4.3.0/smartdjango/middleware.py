from django.http import HttpResponse

from smartdjango.error import Error, OK
from smartdjango.utils import io


class APIPacker:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        response = self.get_response(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            return response

        return self.pack(response)

    @classmethod
    def process_exception(cls, _, error):
        if isinstance(error, Error):
            return cls.pack(error)
        return None

    @staticmethod
    def pack(response):
        if isinstance(response, Error):
            body, error = None, response
        else:
            body, error = response, OK

        response = error.json()
        response['body'] = body

        response = io.json_dumps(response, indent=False)
        response = HttpResponse(
            response,
            status=error.code,
            content_type="application/json; encoding=utf-8",
        )
        return response
