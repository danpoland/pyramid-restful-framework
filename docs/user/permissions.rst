Permissions
===========

PRF offers a single base class for writing your own permissions, ``BasePermission``. There are two methods that you
can override, ``has_permission()`` and ``has_object_permission()``. The first is checked on every request to a view and
the later is checked when a specific instance of an object is being accessed in a view.

In the example below the request's authenticated user must be an admin::

    from pyramid.response import Response

    from pyramid_restful.viewsets import ModelCRPDViewSet
    from pyramid_restful.permissions import BasePermission

    from .models import User
    from .schemas import UserSchema

    class IsAdminPermission(BasePermission):
        message = 'You must be an admin.'

        def has_permission(self, request, view):
            return request.user.is_admin == True:


    class UserViewSet(ModelCRPDViewSet):
        model = User
        schema = UserSchema
        permission_classes = (IsAdminPermission,)


If you prefer you can still use pyramid's built in authorization and permissions framework. If you are manually routing
a view and using pyramid's authorization framework you would use permissions just as you would normally::

    # config is an instance of pyramid.config.Configurator
    config.add_route('users', '/users/')
    config.add_view(views.UserView.as_view(), route_name='user', permission='view')

If you are routing a ``ViewSet`` and using a ``ViewSetRouter`` you simply set your permission using the ``permission``
kwarg::

    from pyramid.routers import ViewSetRouter

    def includeme(config):
    router = ViewSetRouter(config)
    router.register('users', views.UserViewSet, 'coop', permission='view')

