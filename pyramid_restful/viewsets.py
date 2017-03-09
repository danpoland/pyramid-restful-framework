from .views import APIView
from .generics import GenericAPIView
from . import mixins


class ViewSetMixin:
    """
    Overrides `.as_view()` so that it takes an `actions` keyword that performs
    the binding of HTTP methods to actions on the Resource.

    For example, to create a concrete view binding the 'GET' and 'POST' methods
    to the 'list' and 'create' actions...

    view = MyViewSet.as_view({'get': 'list', 'post': 'create'})
    """

    @classmethod
    def as_view(cls, action_map=None, **initkwargs):
        """
        Allows custom request to method routing based on given action_map.
        Needs to re-implement the method but contains all the things the parent does.
        """

        if not action_map:  # actions must not be empty
            raise TypeError("action_map is a required argument.")

        def view(request):
            self = cls(**initkwargs)
            self.request = request
            self.lookup_url_kwargs = self.request.matchdict
            self.action_map = action_map
            self.action = self.action_map.get(self.request.method.lower())

            for method, action in action_map.items():
                handler = getattr(self, action)
                setattr(self, method, handler)

            return self.dispatch(self.request, **self.request.matchdict)

        return view


class APIViewSet(ViewSetMixin, APIView):
    """
    Does not provide any actions by default.
    """
    pass


class GenericAPIViewSet(ViewSetMixin, GenericAPIView):
    """
    The GenericAPIView class does not provide any actions by default,
    but does include the base set of generic view behavior, such as
    the `get_object` and `get_queryset` methods.
    """
    pass


class ReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           GenericAPIViewSet):
    """
    A viewset that provides default `list()` and `retrieve()` actions.
    """
    pass


class ModelCRUDViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericAPIViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`, `destroy()` and `list()` actions.
    """
    pass


class ModelCRPDViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.PartialUpdateMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       GenericAPIViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `partial_update()`, `destroy()` and `list()` actions.
    """
    pass


class ModelCRUPDViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.PartialUpdateMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        GenericAPIViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `partial_update()`, `'update()`,
    `destroy()` and `list()` actions.
    """
    pass


class ActionSchemaMixin:
    """
    Allows you to use different schema depending on the
    action being taken by the request.

    Defaults to the standard schema_class if no actions are specified.
    """

    def get_schema_class(self):
        if self.action == 'retrieve' and hasattr(self, 'retrieve_schema'):
            return self.retrieve_schema
        elif self.action == 'list' and hasattr(self, 'list_schema'):
            return self.list_schema
        elif self.action == 'update' and hasattr(self, 'update_schema'):
            return self.update_schema
        elif self.action == 'partial_update' and hasattr(self, 'update_schema'):
            return self.update_schema
        elif self.action == 'create' and hasattr(self, 'create_schema'):
            return self.create_schema
        elif self.action == 'destroy' and hasattr(self, 'destroy_schema'):
            return self.destroy_schema

        return self.schema_class
