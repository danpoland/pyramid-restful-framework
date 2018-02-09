Class-based Views
=================

The ``APIView`` serves as the base class for all views in PRF. It replaces the function based views often used
in pyramid applications. Requests are passed to the view from the router and are dispatched to a method in the view
with the same name as the HTTP method from the request. If the view class does not implement a method used by the request
a 405 response is returned.

For example, in the class definition below a **GET** request would routed the class's `get` method and a **POST**
request would be routed to the class's ``post`` method::

    from pyramid.response import Response

    from restful_framework.views import APIView

    from .models import User

    class UserView(ApiView):
        """
        A view to list all the users and to create a new User.
        """

        def get(self, request, *args, **kwargs):
            users = request.dbsession.query(User).all()
            return Response(json_body=users)

        def post(self, request, *args, **kwargs):
            user = User(**request.json_body)
            request.dbsession.add(user)
            return Response(status=201)


You route ``APIView`` classes similar to how you route typical views in pyramid. Below is an example ``routes.py`` file that
routes the view defined above::

    from . import views

    def includeme(config):
        config.add_route('users', '/users/')
        config.add_view(views.UserView.as_view(), route_name='users')



Any URL pattern matching variables used in the route definition will be passed to the view's method as a kwarg.::

    class UserDetailView(ApiView):
        """
        Retrieve a specific User.
        """

        def get(self, request, id, *args, **kwargs):
            user = request.dbsession.query(User).get(id)
            return Response(json_body=user)



    def includeme(config):
        config.add_route('users', '/users/{id}/')
        config.add_view(views.UserDetailView.as_view(), route_name='users')



Permissions
--------------

The ``permission_classes`` class attribute on ``ApiView`` controls which permissions are applied to incoming requests.
By default ``permission_classes`` is set to the value of the configuration variable ``default_permission_classes``. See
:doc:`configuration` and :doc:`permissions` for more details.