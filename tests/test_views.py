import pytest

from pyramid import testing
from pyramid.response import Response

from unittest import TestCase

from pyramid_restful.views import APIView


class GetView(APIView):

    def get(self, request, *args, **kwargs):
        return Response({'method': 'GET'})


class PostView(APIView):

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
        self.get_view = GetView.as_view()
        self.post_view = PostView.as_view()
        self.init_view = InitKwargsView.as_view(name='test')

    def test_implemented_method_dispatch(self):
        request = testing.DummyRequest()
        response = self.get_view(request)
        expected = {'method': 'GET'}
        assert response.status_code == 200
        assert response.body == expected

    def test_method_not_allowed(self):
        request = testing.DummyRequest(post={'data': 'testing'})
        response = self.get_view(request)
        assert response.status_code == 405

    def test_allowed_methods(self):
        view = GetView()
        expected = ['GET', 'OPTIONS']
        assert expected == view.allowed_methods

    def test_initkwargs(self):
        request = testing.DummyRequest()
        response = self.init_view(request)
        expected = {'name': 'test'}
        assert response.body == expected

    def test_raises_exception(self):
        view = ExceptionView().as_view()
        request = testing.DummyRequest()
        self.assertRaises(Exception, view, request)
