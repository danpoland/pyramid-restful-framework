import itertools

from collections import namedtuple

from .exceptions import ImproperlyConfigured


__all__ = ['ViewSetRouter']


Route = namedtuple('Route', ['url', 'mapping', 'name', 'initkwargs'])
DynamicDetailRoute = namedtuple('DynamicDetailRoute', ['url', 'name', 'initkwargs'])
DynamicListRoute = namedtuple('DynamicListRoute', ['url', 'name', 'initkwargs'])


def replace_methodname(format_string, methodname):
    """
    Partially format a format_string, swapping out any
    '{methodname}' or '{methodnamehyphen}' components.
    """

    methodnamehyphen = methodname.replace('_', '-')
    ret = format_string
    ret = ret.replace('{methodname}', methodname)
    ret = ret.replace('{methodnamehyphen}', methodnamehyphen)
    return ret


def flatten(list_of_lists):
    """
    Takes an iterable of iterables, returns a single iterable containing all items
    """

    return itertools.chain(*list_of_lists)


class ViewSetRouter:
    """
    Automatically adds routes and associates views to the Pyramid Configurator for ViewSets, including
    any list_routes and detail_routes.
    """

    routes = [
        # List route.
        Route(
            url=r'/{prefix}{trailing_slash}',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs=dict()
        ),
        # Dynamically generated list routes. Generated using @list_route decorator on methods of the viewset.
        DynamicListRoute(
            url=r'/{prefix}/{methodname}{trailing_slash}',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'/{prefix}/{lookup}{trailing_slash}',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs=dict()
        ),
        # Dynamically generated detail routes. Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'/{prefix}/{lookup}/{methodname}{trailing_slash}',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def __init__(self, configurator, trailing_slash=True):
        """
        :param configurator: pyramid Configurator
        :return: void
        """

        self.configurator = configurator
        self.trailing_slash = trailing_slash and '/' or ''
        self.registry = list()

    def register(self, prefix, viewset, basename):
        lookup = self.get_lookup(viewset)
        routes = self.get_routes(viewset)

        for route in routes:
            # Only actions which actually exist on the viewset will be bound
            mapping = self.get_method_map(viewset, route.mapping)

            if not mapping:
                continue  # empty viewset

            url = route.url.format(
                prefix=prefix,
                lookup=lookup,
                trailing_slash=self.trailing_slash
            )
            view = viewset.as_view(mapping, **route.initkwargs)
            name = route.name.format(basename=basename)

            self.configurator.add_route(name, url)
            self.configurator.add_view(view, route_name=name)

    def get_routes(self, viewset):
        """
        Augment `self.routes` with any dynamically generated routes.
        Returns a list of the Route namedtuple.
        """

        known_actions = list(flatten([route.mapping.values() for route in self.routes if isinstance(route, Route)]))

        # Determine any `@detail_route` or `@list_route` decorated methods on the viewset
        detail_routes = []
        list_routes = []

        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, 'bind_to_methods', None)
            detail = getattr(attr, 'detail', True)

            if httpmethods:
                # check against know actions list
                if methodname in known_actions:
                    raise ImproperlyConfigured('Cannot use @detail_route or @list_route '
                                               'decorators on method "%s" '
                                               'as it is an existing route' % methodname)

                httpmethods = [method.lower() for method in httpmethods]

                if detail:
                    detail_routes.append((httpmethods, methodname))
                else:
                    list_routes.append((httpmethods, methodname))

        def _get_dynamic_routes(route, dynamic_routes):
            ret = []

            for httpmethods, methodname in dynamic_routes:
                method_kwargs = getattr(viewset, methodname).kwargs
                initkwargs = route.initkwargs.copy()
                initkwargs.update(method_kwargs)
                url_path = initkwargs.pop("url_path", None) or methodname

                ret.append(Route(
                    url=replace_methodname(route.url, url_path),
                    mapping={httpmethod: methodname for httpmethod in httpmethods},
                    name=replace_methodname(route.name, url_path),
                    initkwargs=initkwargs,
                ))

            return ret

        ret = []

        for route in self.routes:
            if isinstance(route, DynamicDetailRoute):
                # Dynamic detail routes (@detail_route decorator)
                ret += _get_dynamic_routes(route, detail_routes)
            elif isinstance(route, DynamicListRoute):
                # Dynamic list routes (@list_route decorator)
                ret += _get_dynamic_routes(route, list_routes)
            else:
                # Standard route
                ret.append(route)

        return ret

    def get_lookup(self, viewset):
        base_regex = '{%s}'
        lookup_field = getattr(viewset, 'lookup_field', 'pk')
        lookup_url_kwarg = getattr(viewset, 'lookup_url_kwarg', None) or lookup_field
        return base_regex % lookup_url_kwarg

    def get_method_map(self, viewset, method_map):
        """
        Given a viewset, and a mapping of http methods to actions, return a new mapping which only
        includes any mappings that are actually implemented by the viewset.
        """

        bound_methods = {}

        for method, action in method_map.items():
            if hasattr(viewset, action):
                bound_methods[method] = action

        return bound_methods
