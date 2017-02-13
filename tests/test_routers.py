from unittest import TestCase
from unittest.mock import MagicMock

from pyramid.config import Configurator

from pyramid_restful.routers import ViewSetRouter, Route
from pyramid_restful.viewsets import CrudViewSet, ApiViewSet
from pyramid_restful.exceptions import ImproperlyConfigured


class MyCrudViewSet(CrudViewSet):
    pass


class ReadOnlyViewSet(ApiViewSet):

    def list(self):
        pass

    def retrieve(self):
        pass


class ViewSetRouterTests(TestCase):
    def setUp(self):
        self.config = MagicMock(spec=Configurator)
        self.router = ViewSetRouter(self.config)

    # def viewsetrouter_test(self):
    #     router = ViewSetRouter(self.config)
    #
    #     with patch.object(CrudViewSet) as viewset:
    #         router.register('myobjects', viewset, 'myobject')
    #
    #     router

    def test_get_routes(self):
        viewset = MyCrudViewSet()

        # add mock detail_route and list_route methods
        def detail_route():
            pass

        viewset.detail_route = detail_route
        viewset.detail_route.bind_to_methods = ['GET']
        viewset.detail_route.kwargs = {}
        viewset.detail_route.detail = True

        def list_route():
            pass

        viewset.list_route = list_route
        viewset.list_route.bind_to_methods = ['GET']
        viewset.list_route.kwargs = {}
        viewset.list_route.detail = False

        routes = self.router.get_routes(viewset)

        expected = [
            Route(url='/{prefix}{trailing_slash}', mapping={'get': 'list', 'post': 'create'}, name='{basename}-list',
                  initkwargs={}),
            Route(url='/{prefix}/list_route{trailing_slash}', mapping={'get': 'list_route'},
                  name='{basename}-list-route', initkwargs={}),
            Route(url='/{prefix}/{lookup}{trailing_slash}',
                  mapping={'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'},
                  name='{basename}-detail', initkwargs={}),
            Route(url='/{prefix}/{lookup}/detail_route{trailing_slash}', mapping={'get': 'detail_route'},
                  name='{basename}-detail-route', initkwargs={})]

        assert routes == expected

    def test_improperly_configured_dynamic_route(self):
        viewset = MyCrudViewSet()

        # add mock detail_route and list_route methods
        def retrieve():
            pass

        viewset.retrieve = retrieve
        viewset.retrieve.bind_to_methods = ['GET']
        viewset.retrieve.kwargs = {}
        viewset.retrieve.detail = True

        self.assertRaises(ImproperlyConfigured, self.router.get_routes, viewset)

    def test_get_lookup(self):
        viewset = MyCrudViewSet()
        lookup = self.router.get_lookup(viewset)
        assert lookup == '{pk}'

        viewset = MyCrudViewSet()
        viewset.lookup_field = 'id'
        lookup = self.router.get_lookup(viewset)
        assert lookup == '{id}'

        viewset = MyCrudViewSet()
        viewset.lookup_url_kwargs = {'uuid': 1}
        lookup = self.router.get_lookup(viewset)
        assert lookup == '{uuid}'

    def test_nested_route(self):
        viewset = MyCrudViewSet()
        viewset.lookup_url_kwargs = {'uuid': 1, 'parent_id': 2}
        self.assertRaises(ImproperlyConfigured, self.router.get_lookup, viewset)

    def test_get_method_map(self):
        viewset = ReadOnlyViewSet()
        mapping = self.router.get_method_map(viewset, {'get': 'list', 'post': 'create', 'put': 'update'})
        assert mapping == {'get': 'list'}

    def test_register(self):
        viewset = CrudViewSet()
        self.config.reset_mock()
        self.router.register('users', viewset, 'user')
        self.config.add_route.assert_any_call('user-list', '/users/')
        self.config.add_route.assert_any_call('user-detail', '/users/{pk}/')
        assert self.config.add_view.call_count == 2

    def test_empty_register(self):
        viewset = ApiViewSet()
        self.config.reset_mock()
        self.router.register('users', viewset, 'user')
        self.config.add_route.assert_not_called()
        self.config.add_route.assert_not_called()
