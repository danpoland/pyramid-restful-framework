Views
=======

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



Any URL pattern matching variables used in the route definition will be passed to the view's method as a kwarg.
::

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


GenericAPIView
--------------

The key advantage of using class-based views is that it allows you to reuse common behavior across many views. PRF
supplies you with a few pre-constructed views that provide commonly used functionality.

The `GenericAPIView` class allows you quickly compose an API while keeping your code DRY through class configuration
rather than redefining view logic every time you need it.

**Examples**

Typically when you use a generic view all you need to do is set some of the class attributes.
::

    from pyramid_restful import generics

    from .models import User
    from .schemas import UserSchema

    class UserView(generics.ListCreateAPIView):
        model = User
        schema_class = UserSchema

That's all it takes. This provides the same functionality as the ``UserView`` created using the `APIView` class. It provides
two methods. One for GET requests, which returns all the Users, and one for POST requests, which allows you to add a new User.

In some cases the default behavior might not meet your needs. In those cases you can override the methods on the view class.
::
    
    from pyramid.response import Response
    
    from pyramid_restful import generics

    from .models import User
    from .schemas import UserSchema

    class UserView(generics.ListCreateAPIView):
        model = User
        schema_class = UserSchema
        
        def list(self, request, *args, **kwargs):
            rows = self.get_query().all()
            schema = UserSchema()
            data, errors = schema.dump(rows)
            
            return Response(data)
            
API Reference
-------------

**GenericAPIView**

This class extends `APIView` adding commonly used functionality for basic list and detail views. Full fledged API views
are constructed by combining ``GenericAPIView`` with mixin classes. A few concrete generic views are provided by PRF.

**Attributes**

Basics:
    - ``model``: The SQLAlchemy model that should be used for returning objects from the view. You must set this attribute or override the ``get_query`` method.
    - ``schema_class``: The marshmallow Schema class to be used for validating and deserializing request data and for serializing response data.
    - ``lookup_field``: The field on the model used to identify individual instance of an model. Defaults to ``'id'``.

Pagination:
    - ``pagination_class``: The pagination class that is used to paginate list results. This defaults to the of the ``restful.default_pagination_class`` configuration, if set.

Filtering:
    - ``filter_classes``: An iterable of classes that extend ``BaseFilter``. Filtering is pretty primative currently in PRF. Each class in the ``filter_classes`` iterable is passed the query used by the viewset before the query finally executed to produce the data for a response from the view.
