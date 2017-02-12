from unittest import TestCase
from unittest.mock import MagicMock, patch

from pyramid.config import Configurator

from pyramid_restful.routers import ViewSetRouter
from pyramid_restful.viewsets import CrudViewSet


class ViewSetRouterUnitTests(TestCase):

    def setUp(self):
        self.config = MagicMock(spec=Configurator)
        self.mock_viewset = MagicMock(spec=CrudViewSet)
        self.router = ViewSetRouter(self.config)

    # def viewsetrouter_test(self):
    #     router = ViewSetRouter(self.config)
    #
    #     with patch.object(CrudViewSet) as viewset:
    #         router.register('myobjects', viewset, 'myobject')
    #
    #     router

    def get_routes_test(self):
        routes = self.router.get_routes(self.mock_viewset)
        expected = {}
        assert routes == expected
