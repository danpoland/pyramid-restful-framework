from pyramid import testing
from pyramid.response import Response

from unittest import TestCase

from pyramid_restful.viewsets import APIViewSet, CRUDViewSet


class MyViewSet(APIViewSet):

    def list(self, request, *args, **kwargs):
        return Response({'method': 'GET', 'action': 'list'})


class MyCRUDViewSet(CRUDViewSet):
    """
    All methods will throw not implemented exceptions.
    """
    pass


class ViewSetTests(TestCase):

    def setUp(self):
        self.viewset = MyViewSet.as_view(action_map={'get': 'list'})

    def test_action_map(self):
        request = testing.DummyRequest()
        response = self.viewset(request)
        expected = {'method': 'GET', 'action': 'list'}
        assert response.status_code == 200
        assert response.body == expected

    def test_missing_action_map(self):
        self.assertRaises(TypeError, MyViewSet.as_view)


class CRUDViewSetTests(TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.viewset = MyCRUDViewSet.as_view(action_map={
            'get': 'list',
            'post': 'create'
        })
        self.detail_viewset = MyCRUDViewSet.as_view(action_map={
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

    def test_list(self):
        self.assertRaises(NotImplementedError, self.viewset, self.request)

    def test_create(self):
        self.request.method = 'POST'
        self.assertRaises(NotImplementedError, self.viewset, self.request)

    def test_retrieve(self):
        self.assertRaises(NotImplementedError, self.detail_viewset, self.request)

    def test_update(self):
        self.request.method = 'PUT'
        self.assertRaises(NotImplementedError, self.detail_viewset, self.request)

    def test_partial_update(self):
        self.request.method = 'PATCH'
        self.assertRaises(NotImplementedError, self.detail_viewset, self.request)

    def test_destroy(self):
        self.request.method = 'DELETE'
        self.assertRaises(NotImplementedError, self.detail_viewset, self.request)
