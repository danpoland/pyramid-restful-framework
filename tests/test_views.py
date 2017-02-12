from pyramid import testing
from pyramid.response import Response

from unittest import TestCase

from pyramid_restful.views import APIView


class MyView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({'method': 'GET'})

    def post(self, request, *args, **kwargs):
        return Response({'method': 'POST', 'data': request.body})


class InitKwargsView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({'name': self.name})


class ExceptionView(APIView):

    def get(self, request, *args, **kwargs):
        raise Exception('test exception')


class APIViewTests(TestCase):

    def setUp(self):
        self.test_view = MyView.as_view(name='MyView')

    def test_implemented_method_dispatch(self):
        request = testing.DummyRequest()
        response = self.test_view(request)
        expected = {'method': 'GET'}
        assert response.status_code == 200
        assert response.body == expected

    def test_method_not_allowed(self):
        request = testing.DummyRequest()
        request.method = 'PUT'
        response = self.test_view(request)
        assert response.status_code == 405

    def test_initkwargs(self):
        view = InitKwargsView.as_view(name='test')
        request = testing.DummyRequest()
        response = view(request)
        expected = {'name': 'test'}
        assert response.body == expected

    def test_raises_exception(self):
        view = ExceptionView.as_view()
        request = testing.DummyRequest()
        self.assertRaises(Exception, view, request)

    def test_invalid_method_exception(self):
        request = testing.DummyRequest()
        request.method = 'PUTZ'
        response = self.test_view(request)
        assert response.status_code == 405

    def test_options_request(self):
        request = testing.DummyRequest()
        request.method = 'OPTIONS'
        response = self.test_view(request)
        assert response.headers.get('Allow') == ['GET', 'POST', 'OPTIONS']
