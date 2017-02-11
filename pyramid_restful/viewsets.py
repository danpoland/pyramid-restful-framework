from .views import APIView


__all__ = ['ViewSet', 'ApiViewSet']


class ViewSetMixin:
    """
    DOC GOES HERE
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
            self.url_lookup_kwargs = self.request.matchdict
            self.action_map = action_map

            for method, action in action_map.items():
                handler = getattr(self, action)
                setattr(self, method, handler)

            return self.dispatch(self.request, **self.request.matchdict)

        return view


class ApiViewSet(ViewSetMixin, APIView):
    pass
