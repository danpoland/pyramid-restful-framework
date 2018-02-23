Generic Views
=============

The key advantage of using class-based views is that it allows you to reuse common behavior across many views. PRF
supplies you with a few pre-constructed views that provide commonly used functionality.

The ``GenericAPIView`` class allows you quickly compose an API while keeping your code DRY through class configuration
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

That's all it takes. This provides the same functionality as the ``UserView`` created using the ``APIView`` class
in the :doc:`views` section. It provides two methods. One for **GET** requests, which returns all the Users,
and one for **POST** requests, which allows you to add a new User.

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
For a full list of these classes see the :ref:`Generics API <api-generics-label>` docs.

**Attributes**

Basics:
    - ``model``: The SQLAlchemy model that should be used for returning objects from the view. You must set this attribute or override the ``get_query()`` method.
    - ``schema_class``: The marshmallow Schema class to be used for validating and deserializing request data and for serializing response data.
    - ``lookup_field``: The field on the model used to identify individual instance of an model. Defaults to ``'id'``.

Pagination:
    - ``pagination_class``: The pagination class that is used to paginate list results. This defaults to the of the ``restful.default_pagination_class`` configuration, if set.

Filtering:
    - ``filter_classes``: An iterable of classes that extend ``BaseFilter``. Filtering is pretty primative currently in PRF. Each class in the ``filter_classes`` iterable is passed the query used by the viewset before the query finally executed to produce the data for a response from the view.


