from unittest import TestCase

from pyramid_restful.decorators import list_route, detail_route


class DecoratorTests(TestCase):

    def test_list_route(self):
        @list_route(methods=['GET'], url_path='my-list-route')
        def my_list_route():
            pass

        assert my_list_route.bind_to_methods == ['GET']
        assert my_list_route.detail == False
        assert my_list_route.kwargs == {'url_path': 'my-list-route'}

    def test_detail_route(self):
        @detail_route(methods=['PUT'], url_path='my-detail-route')
        def my_detail_route():
            pass

        assert my_detail_route.bind_to_methods == ['PUT']
        assert my_detail_route.detail == True
        assert my_detail_route.kwargs == {'url_path': 'my-detail-route'}
