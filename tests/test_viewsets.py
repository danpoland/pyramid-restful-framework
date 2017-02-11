from pyramid import testing
from pyramid.response import Response

from unittest import TestCase

from pyramid_restful.viewsets import ApiViewSet


class TestViewSet(ApiViewSet):

    def list(self, request, *args, **kwargs):
        return Response({'method': 'GET', 'action': 'list'})


class ViewSetTests(TestCase):

    def setUp(self):
        self.viewset = TestViewSet.as_view(action_map={'get': 'list'})

    def test_action_map(self):
        request = testing.DummyRequest()
        response = self.viewset(request)
        expected = {'method': 'GET', 'action': 'list'}
        assert response.status_code == 200
        assert response.body == expected

    def test_missing_action_map(self):
        self.assertRaises(TypeError, TestViewSet.as_view)
