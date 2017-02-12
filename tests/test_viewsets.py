from pyramid import testing
from pyramid.response import Response

from unittest import TestCase

from pyramid_restful.viewsets import ApiViewSet, CrudViewSet


class MyViewSet(ApiViewSet):

    def list(self, request, *args, **kwargs):
        return Response({'method': 'GET', 'action': 'list'})


class MyCrudViewSet(CrudViewSet):
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


class CrudViewSetTests(TestCase):

    def setUp(self):
        self.viewset = MyCrudViewSet.as_view(action_map={
            'get': 'list',
            'post': 'create'
        })
        self.detail_viewset = MyCrudViewSet.as_view(action_map={
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

    def test_list(self):
        request = testing.DummyRequest()
        self.assertRaises(NotImplementedError, self.viewset, request)

    def test_create(self):
        request = testing.DummyRequest()
        request.method = 'POST'
        self.assertRaises(NotImplementedError, self.viewset, request)

    def test_retrieve(self):
        request = testing.DummyRequest()
        self.assertRaises(NotImplementedError, self.detail_viewset, request)

    def test_update(self):
        request = testing.DummyRequest()
        request.method = 'PUT'
        self.assertRaises(NotImplementedError, self.detail_viewset, request)

    def test_partial_update(self):
        request = testing.DummyRequest()
        request.method = 'PATCH'
        self.assertRaises(NotImplementedError, self.detail_viewset, request)

    def test_destroy(self):
        request = testing.DummyRequest()
        request.method = 'DELETE'
        self.assertRaises(NotImplementedError, self.detail_viewset, request)
