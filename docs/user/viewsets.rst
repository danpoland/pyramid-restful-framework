ViewSets
========

A ViewSet is a class-based view that allows you to combine a set of related views into a single class. The most
typical usage of ViewSets is to combine CRUD operations for a particular model in a single class. ViewSets allow you
define methods that handle both detail and list operations in a single class. Unlike a ``APIView`` class that defines
methods such as ``get()`` or ``post()``, an ``APIViewSet`` defines actions like ``retrive()`` and ``create()``.

Example
-------

Below we define a single ``APIViewSet`` that can be used to retrieve a single user or all the users in the system::

    from pyramid.response import Response
    from pyramid.httpexceptions import HTTPNotFound

    from pyramid_restful import viewsets

    from myapp.models import User
    from myyapp.schemas import UserSchema

    class UserViewSet(viewsets.APIViewSet):
        model = User
        schema = UserSchema

        def list(self, request):
            users = request.dbsession.query(User).all()
            schema = UserSchema()
            content = schema.dump(users, many=True)[0]
            return Response(json=content)


        def retrieve(self, request, id):
            user = request.dbsession.query(User).get(id)

            if not user:
                raise HTTPNotFound()

            schema = UserSchema()
            content = schema.dump(user)[0]
            return Response(json=content)


To route this view in Pyramid we bind the view to two different routes::

    from . import views


    def includeme(config):
        config.add_route('user-list', '/users/')
        config.add_view(views.UserViewSet.as_view({'get': 'list'}), route_name='user-list')

        config.add_route('user-detail', '/users/{id}/')
        config.add_view(views.UserViewSet.as_view({'get': 'retrieve'}), route_name='user-detail')


Typically you wont do this. Instead you would use the `ViewSetRouter` to configure the routes for you::

    from pyramid_restful.routers import ViewSetRouter

    from . import views


    def includeme(config):
        router = ViewSetRouter(config)
        router.register('users', views.UserViewSet, 'user')



ViewSet Actions
---------------

The ``ViewSetRouter`` provides defaults for the standard CRUD actions, as shown below::

    class UserViewSet(viewsets.APIViewSet):
        """
        Example empty viewset demonstrating the standard
        actions that will be handled by a router class.
        """

        def list(self, request):
            pass

        def create(self, request):
            pass

        def retrieve(self, request, id=None):
            pass

        def update(self, request, id=None):
            pass

        def partial_update(self, request, id=None):
            pass

        def destroy(self, request, id=None):
            pass



Including extra actions for routing
-----------------------------------

You can add ad-hoc methods to ViewSets that will automatically be routed by the ``ViewSetRouter`` by using the
``@detail_route`` or ``@list_route`` decorators. The ``@detail_route`` includes ``id`` in it's url pattern and is used
for methods that operate on a single instance of model. ``@list_route`` decorator is used for methods that operate on
many instances of a model.

Example::

    from pyramid.response import Response

    from pyramid_restful.viewsets import ModelCRPDViewSet
    from pyramid_restful.decorators import list_route, detail_route

    from .models import User
    from .schemas import UserSchema


    class UserViewSet(ModelCRPDViewSet):
        model = User
        schema = UserSchema

        @detail_route(methods=['post'])
        def lock(request, id):
            user = request.dbsession.query(User).get(id)

            if not user:
                raise HTTPNotFound()

            user.is_locked = True
            return Response(status=204)

        @list_route(methods=['get'])
        def active(request):
            users = request.dbsession.query(User).filter(User.is_active == True).all()
            schema = UserSchema()
            content = schema.dump(users, many=True)[0]
            return Response(json=content)

By default the router will append the name of method to the url pattern generated. The two decorated routes above would
result in the following url patterns::

    '/users/{id}/lock'
    '/users/active'

You can override this behavior by setting the kwarg ``url_path`` on the decorator.


Base ViewSet Classes
--------------------

Generally your not going to need to write your own viewsets. Instead you will use one of the base ViewSet classes
provided by PRF or use a number of mixin classes in your ViewSet to compose a class that only includes the actions you
need for a particular resource.

APIViewSet
^^^^^^^^^^

The ``APIViewSet`` class extends the ``APIView`` class and does not provide any actions by default. You will have to
add the action methods explicitly to the class. You can use the standard ``APIView`` attributes such as ``permissions``.

GenericAPIViewSet
^^^^^^^^^^^^^^^^^

The ``GenericAPIViewSet`` class extends ``GenericAPIView`` and does not provide any actions by default, but does
include the base set of generic view behavior, such as the ``get_object()`` and ``get_query()`` methods. To use
the class you will typically mixin the actions you need from the mixins module or write the action methods explicitly.


The ModelViewSets
^^^^^^^^^^^^^^^^^

PRF provide you with several ModelViewSet implementations. ModelViewSets are simply classes in which several
action mixins are combined with ``GenericAPIViewSet``. They provide all the functionality that comes with a
``GenericAPIView``, such as the ``filter_classes`` and ``permission_classes`` attributes and well as the ``get_query()``
and ``get_object()`` methods. The base ModelViewSets provided by PRF along with their default actions are listed below:

    - ReadOnlyModelViewSet: ``list()``, ``retrieve()``
    - ModelCRUDViewSet: ``list()``, ``create()``, ``retrieve()``, ``update()``, ``destroy()``
    - ModelCRPDViewSet: ``list()``, ``create()``, ``retrieve()``, ``partial_update()``, ``destroy()``
    - ModelCRUPDViewSet: ``list()``, ``create()``, ``retrieve()``, ``update()``, ``partial_update()``, ``destroy()``

Custom ViewSets
^^^^^^^^^^^^^^^

If one of the predefined ViewSets doesn't meet your needs you can always compose your own ViewSet and override its
actions.

Example::

    from pyramid_restful import mixins
    from pyramid_restful import viewsets

    from .models import User
    from .schema import UserSchema


    class UserViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin):

        model = User
        schema = UserSchema

        def get_query():
            """
            Restrict user to the authenticated user.
            """

            return super(UserViewSet, self).get_query() \
                .filter(User.id == request.user.id)
