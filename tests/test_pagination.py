from unittest import TestCase, mock

import pytest

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from pyramid_restful import pagination


class PaginationUtilitiesTests(TestCase):

    def test_replace_query_param(self):
        from pyramid_restful.pagination.utilities import replace_query_param
        expected = 'http://test.com?name=testing'
        assert replace_query_param('http://test.com', 'name', 'testing') == expected
        assert replace_query_param('http://test.com?name=foo', 'name', 'testing') == expected

    def test_remove_query_param(self):
        from pyramid_restful.pagination.utilities import remove_query_param
        expected = 'http://test.com'
        assert remove_query_param('http://test.com?name=foo', 'name') == expected


class TestPageNumberPagination(TestCase):
    """
    Unit tests for `pagination.PageNumberPagination`.
    """

    def setUp(self):
        class ExamplePagination(pagination.PageNumberPagination):
            page_size = 5

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_query(self.queryset, request))

    def get_paginated_content(self, queryset):
        response = self.pagination.get_paginated_response(queryset)
        return response.json_body

    def get_current_url(self):
        return 'http://testserver/'

    def test_no_page_number(self):
        request = testing.DummyRequest()
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        assert queryset == [1, 2, 3, 4, 5]
        assert content == {
            'results': [1, 2, 3, 4, 5],
            'previous': None,
            'next': 'http://testserver/?page=2',
            'count': 100
        }

    def test_second_page(self):
        request = testing.DummyRequest()
        request.params['page'] = 2
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        assert queryset == [6, 7, 8, 9, 10]
        assert content == {
            'results': [6, 7, 8, 9, 10],
            'previous': 'http://testserver/',
            'next': 'http://testserver/?page=3',
            'count': 100
        }

    def test_last_page(self):
        request = testing.DummyRequest()
        request.params['page'] = 'last'
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        assert queryset == [96, 97, 98, 99, 100]
        assert content == {
            'results': [96, 97, 98, 99, 100],
            'previous': 'http://testserver/?page=19',
            'next': None,
            'count': 100
        }

    def test_invalid_page(self):
        request = testing.DummyRequest()
        request.params['page'] = 'invalid'
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        self.assertRaises(HTTPNotFound, self.paginate_queryset, request)


class TestPageNumberPaginationOverride:
    """
    Unit tests for `pagination.PageNumberPagination`.
    the Paginator Class is overridden.
    """

    def setup(self):
        class OverriddenPaginator(pagination.pagenumber.Paginator):
            # override the count in our overridden Paginator
            # we will only return one page, with one item
            count = 1

        class ExamplePagination(pagination.PageNumberPagination):
            page_size = 5
            paginator_class = OverriddenPaginator
            page_size_query_param = 'unit'  # TODO TEST THIS

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_query(self.queryset, request))

    def get_paginated_content(self, queryset):
        response = self.pagination.get_paginated_response(queryset)
        return response.json_body

    def get_current_url(self):
        return 'http://testserver/'

    def test_no_page_number(self):
        request = testing.DummyRequest()
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        queryset = self.paginate_queryset(request)
        content = self.get_paginated_content(queryset)
        assert queryset == [1]
        assert content == {
            'results': [1, ],
            'previous': None,
            'next': None,
            'count': 1
        }

    def test_invalid_page(self):
        request = testing.DummyRequest()
        request.params['page'] = 'invalid'
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        with pytest.raises(HTTPNotFound):
            self.paginate_queryset(request)
