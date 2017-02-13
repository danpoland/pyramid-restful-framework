import logging

from pyramid.httpexceptions import HTTPClientError, HTTPMethodNotAllowed
from pyramid.response import Response


logger = logging.getLogger('restful_pyramid')


__all__ = ['APIView']


class APIView:
    """
    DOC
    """

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    lookup_url_kwargs = None

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    @classmethod
    def as_view(cls, **initkwargs):
        def view(request):
            self = cls(**initkwargs)
            self.request = request
            self.lookup_url_kwargs = self.request.matchdict

            return self.dispatch(self.request, **self.lookup_url_kwargs)

        return view

    def dispatch(self, request, *args, **kwargs):
        try:
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed

            response = handler(request, *args, **kwargs)
        except Exception as exc:
            response = self.handle_exception(exc)

        return response

    def handle_exception(self, exc):
        if isinstance(exc, HTTPClientError):
            # HTTPClientError, implement both Response and Exception
            return exc

        raise exc

    def http_method_not_allowed(self, request, *args, **kwargs):
        logger.warning(
            'Method Not Allowed (%s): %s', request.method, request.path,
            extra={'status_code': 405, 'request': request}
        )

        raise HTTPMethodNotAllowed()

    def options(self, request, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """

        response = Response()

        response.headers['Allow'] = self.allowed_methods
        response.headers['Content-Length'] = 0

        return response

    @property
    def allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]
