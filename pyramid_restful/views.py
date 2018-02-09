import logging

from pyramid.httpexceptions import HTTPClientError, HTTPMethodNotAllowed, HTTPForbidden
from pyramid.response import Response

from pyramid_restful.settings import api_settings

logger = logging.getLogger('restful_pyramid')

__all__ = ['APIView']


class APIView:
    """
    Base for class based views. Requests are routed to a view's
    method with the same name as the HTTP method of the request.
    """

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    lookup_url_kwargs = None
    #: An iterable of permissions classes. Defaults to ``default_permission_classes`` from the pyramid_restful
    #: configuration. Override this attribute to provide view specific permissions.
    permission_classes = api_settings.default_permission_classes

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

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """

        self.check_permissions(request)  # Ensure that the incoming request is permitted

    def dispatch(self, request, *args, **kwargs):
        try:
            self.initial(request, *args, **kwargs)

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

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """

        return [permission() for permission in self.permission_classes]

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.

        :param request: Pyramid Request object.
        """

        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                self.permission_denied(request, message=getattr(permission, 'message', None))

    def check_object_permissions(self, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.

        :param request: Pyramid Request object.
        :param obj: The SQLAlchemy model instance that permissions will be evaluated against.
        """

        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(request, message=getattr(permission, 'message', None))

    def permission_denied(self, request, message):
        # Todo figure out how to determine if this is a authorization vs authentication error.
        raise HTTPForbidden(detail=message)

    def options(self, request, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """

        response = Response()

        response.headers['Allow'] = ', '.join(self.allowed_methods)
        response.headers['Content-Length'] = '0'

        return response

    @property
    def allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]
