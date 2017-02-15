from unittest import TestCase, mock

import pytest

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from pyramid_restful import pagination
from pyramid_restful.pagination.pagenumber import Paginator, InvalidPage, PageNotAnInteger, EmptyPage, Page


class ValidAdjacentNumsPage(Page):

    def next_page_number(self):
        if not self.has_next():
            return None
        return super(ValidAdjacentNumsPage, self).next_page_number()

    def previous_page_number(self):
        if not self.has_previous():
            return None
        return super(ValidAdjacentNumsPage, self).previous_page_number()


class ValidAdjacentNumsPaginator(Paginator):

    def _get_page(self, *args, **kwargs):
        return ValidAdjacentNumsPage(*args, **kwargs)


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


class PaginatorTests(TestCase):
    """
    Tests for the Paginator and Page classes.
    """

    def check_paginator(self, params, output):
        """
        Helper method that instantiates a Paginator object from the passed
        params and then checks that its attributes match the passed output.
        """
        count, num_pages, page_range = output
        paginator = Paginator(*params)
        self.check_attribute('count', paginator, count, params)
        self.check_attribute('num_pages', paginator, num_pages, params)
        self.check_attribute('page_range', paginator, page_range, params, coerce=list)

    def check_attribute(self, name, paginator, expected, params, coerce=None):
        """
        Helper method that checks a single attribute and gives a nice error
        message upon test failure.
        """
        got = getattr(paginator, name)
        if coerce is not None:
            got = coerce(got)
        self.assertEqual(
            expected, got,
            "For '%s', expected %s but got %s.  Paginator parameters were: %s"
            % (name, expected, got, params)
        )

    def test_paginator(self):
        """
        Tests the paginator attributes using varying inputs.
        """
        nine = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        ten = nine + [10]
        eleven = ten + [11]
        tests = (
            # Each item is two tuples:
            #     First tuple is Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is resulting Paginator attributes - count,
            #         num_pages, and page_range.
            # Ten items, varying orphans, no empty first page.
            ((ten, 4, 0, False), (10, 3, [1, 2, 3])),
            ((ten, 4, 1, False), (10, 3, [1, 2, 3])),
            ((ten, 4, 2, False), (10, 2, [1, 2])),
            ((ten, 4, 5, False), (10, 2, [1, 2])),
            ((ten, 4, 6, False), (10, 1, [1])),
            # Ten items, varying orphans, allow empty first page.
            ((ten, 4, 0, True), (10, 3, [1, 2, 3])),
            ((ten, 4, 1, True), (10, 3, [1, 2, 3])),
            ((ten, 4, 2, True), (10, 2, [1, 2])),
            ((ten, 4, 5, True), (10, 2, [1, 2])),
            ((ten, 4, 6, True), (10, 1, [1])),
            # One item, varying orphans, no empty first page.
            (([1], 4, 0, False), (1, 1, [1])),
            (([1], 4, 1, False), (1, 1, [1])),
            (([1], 4, 2, False), (1, 1, [1])),
            # One item, varying orphans, allow empty first page.
            (([1], 4, 0, True), (1, 1, [1])),
            (([1], 4, 1, True), (1, 1, [1])),
            (([1], 4, 2, True), (1, 1, [1])),
            # Zero items, varying orphans, no empty first page.
            (([], 4, 0, False), (0, 0, [])),
            (([], 4, 1, False), (0, 0, [])),
            (([], 4, 2, False), (0, 0, [])),
            # Zero items, varying orphans, allow empty first page.
            (([], 4, 0, True), (0, 1, [1])),
            (([], 4, 1, True), (0, 1, [1])),
            (([], 4, 2, True), (0, 1, [1])),
            # Number if items one less than per_page.
            (([], 1, 0, True), (0, 1, [1])),
            (([], 1, 0, False), (0, 0, [])),
            (([1], 2, 0, True), (1, 1, [1])),
            ((nine, 10, 0, True), (9, 1, [1])),
            # Number if items equal to per_page.
            (([1], 1, 0, True), (1, 1, [1])),
            (([1, 2], 2, 0, True), (2, 1, [1])),
            ((ten, 10, 0, True), (10, 1, [1])),
            # Number if items one more than per_page.
            (([1, 2], 1, 0, True), (2, 2, [1, 2])),
            (([1, 2, 3], 2, 0, True), (3, 2, [1, 2])),
            ((eleven, 10, 0, True), (11, 2, [1, 2])),
            # Number if items one more than per_page with one orphan.
            (([1, 2], 1, 1, True), (2, 1, [1])),
            (([1, 2, 3], 2, 1, True), (3, 1, [1])),
            ((eleven, 10, 1, True), (11, 1, [1])),
            # Non-integer inputs
            ((ten, '4', 1, False), (10, 3, [1, 2, 3])),
            ((ten, '4', 1, False), (10, 3, [1, 2, 3])),
            ((ten, 4, '1', False), (10, 3, [1, 2, 3])),
            ((ten, 4, '1', False), (10, 3, [1, 2, 3])),
        )
        for params, output in tests:
            self.check_paginator(params, output)

    def test_invalid_page_number(self):
        """
        Invalid page numbers result in the correct exception being raised.
        """
        paginator = Paginator([1, 2, 3], 2)
        with self.assertRaises(InvalidPage):
            paginator.page(3)
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number(None)
        with self.assertRaises(PageNotAnInteger):
            paginator.validate_number('x')
        with self.assertRaises(EmptyPage):
            paginator.validate_number(-1)
        with self.assertRaises(EmptyPage):
            paginator.validate_number(999)
        # With no content and allow_empty_first_page=True, 1 is a valid page number
        paginator = Paginator([], 2)
        self.assertEqual(paginator.validate_number(1), 1)

    def test_paginate_misc_classes(self):
        class CountContainer:
            def count(self):
                return 42

        # Paginator can be passed other objects with a count() method.
        paginator = Paginator(CountContainer(), 10)
        self.assertEqual(42, paginator.count)
        self.assertEqual(5, paginator.num_pages)
        self.assertEqual([1, 2, 3, 4, 5], list(paginator.page_range))

        # Paginator can be passed other objects that implement __len__.
        class LenContainer:
            def __len__(self):
                return 42

        paginator = Paginator(LenContainer(), 10)
        self.assertEqual(42, paginator.count)
        self.assertEqual(5, paginator.num_pages)
        self.assertEqual([1, 2, 3, 4, 5], list(paginator.page_range))

    def check_indexes(self, params, page_num, indexes):
        """
        Helper method that instantiates a Paginator object from the passed
        params and then checks that the start and end indexes of the passed
        page_num match those given as a 2-tuple in indexes.
        """
        paginator = Paginator(*params)
        if page_num == 'first':
            page_num = 1
        elif page_num == 'last':
            page_num = paginator.num_pages
        page = paginator.page(page_num)
        start, end = indexes
        msg = ("For %s of page %s, expected %s but got %s. Paginator parameters were: %s")
        self.assertEqual(start, page.start_index(),
                         msg % ('start index', page_num, start, page.start_index(), params))
        self.assertEqual(end, page.end_index(), msg % ('end index', page_num, end, page.end_index(), params))

    def test_page_indexes(self):
        """
        Paginator pages have the correct start and end indexes.
        """
        ten = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        tests = (
            # Each item is three tuples:
            #     First tuple is Paginator parameters - object_list, per_page,
            #         orphans, and allow_empty_first_page.
            #     Second tuple is the start and end indexes of the first page.
            #     Third tuple is the start and end indexes of the last page.
            # Ten items, varying per_page, no orphans.
            ((ten, 1, 0, True), (1, 1), (10, 10)),
            ((ten, 2, 0, True), (1, 2), (9, 10)),
            ((ten, 3, 0, True), (1, 3), (10, 10)),
            ((ten, 5, 0, True), (1, 5), (6, 10)),
            # Ten items, varying per_page, with orphans.
            ((ten, 1, 1, True), (1, 1), (9, 10)),
            ((ten, 1, 2, True), (1, 1), (8, 10)),
            ((ten, 3, 1, True), (1, 3), (7, 10)),
            ((ten, 3, 2, True), (1, 3), (7, 10)),
            ((ten, 3, 4, True), (1, 3), (4, 10)),
            ((ten, 5, 1, True), (1, 5), (6, 10)),
            ((ten, 5, 2, True), (1, 5), (6, 10)),
            ((ten, 5, 5, True), (1, 10), (1, 10)),
            # One item, varying orphans, no empty first page.
            (([1], 4, 0, False), (1, 1), (1, 1)),
            (([1], 4, 1, False), (1, 1), (1, 1)),
            (([1], 4, 2, False), (1, 1), (1, 1)),
            # One item, varying orphans, allow empty first page.
            (([1], 4, 0, True), (1, 1), (1, 1)),
            (([1], 4, 1, True), (1, 1), (1, 1)),
            (([1], 4, 2, True), (1, 1), (1, 1)),
            # Zero items, varying orphans, allow empty first page.
            (([], 4, 0, True), (0, 0), (0, 0)),
            (([], 4, 1, True), (0, 0), (0, 0)),
            (([], 4, 2, True), (0, 0), (0, 0)),
        )
        for params, first, last in tests:
            self.check_indexes(params, 'first', first)
            self.check_indexes(params, 'last', last)

        # When no items and no empty first page, we should get EmptyPage error.
        with self.assertRaises(EmptyPage):
            self.check_indexes(([], 4, 0, False), 1, None)
        with self.assertRaises(EmptyPage):
            self.check_indexes(([], 4, 1, False), 1, None)
        with self.assertRaises(EmptyPage):
            self.check_indexes(([], 4, 2, False), 1, None)

    def test_page_sequence(self):
        """
        A paginator page acts like a standard sequence.
        """
        eleven = 'abcdefghijk'
        page2 = Paginator(eleven, per_page=5, orphans=1).page(2)
        self.assertEqual(len(page2), 6)
        self.assertIn('k', page2)
        self.assertNotIn('a', page2)
        self.assertEqual(''.join(page2), 'fghijk')
        self.assertEqual(''.join(reversed(page2)), 'kjihgf')

    def test_get_page_hook(self):
        """
        A Paginator subclass can use the ``_get_page`` hook to
        return an alternative to the standard Page class.
        """
        eleven = 'abcdefghijk'
        paginator = ValidAdjacentNumsPaginator(eleven, per_page=6)
        page1 = paginator.page(1)
        page2 = paginator.page(2)
        self.assertIsNone(page1.previous_page_number())
        self.assertEqual(page1.next_page_number(), 2)
        self.assertEqual(page2.previous_page_number(), 1)
        self.assertIsNone(page2.next_page_number())

    def test_page_range_iterator(self):
        """
        Paginator.page_range should be an iterator.
        """
        self.assertIsInstance(Paginator([1, 2, 3], 2).page_range, type(range(0)))


class TestPageNumberPagination(TestCase):
    """
    Unit tests for `pagination.pagenumber.PageNumberPagination`.
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
        return response.json_body   # todo, if renders are ever implemented this needs updated

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
            page_size_query_param = 'unit'

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_query(self.queryset, request))

    def get_paginated_content(self, queryset):
        response = self.pagination.get_paginated_response(queryset)
        return response.json_body  # todo, if renders are ever implemented this needs updated

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

    def test_overridden_query_param(self):
        request = testing.DummyRequest()
        request.params['unit'] = 1
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


class TestLinkHeaderPagination(TestCase):
    """
    Unit tests for `pagination.LinkHeaderPagination`.
    """

    def setUp(self):
        class ExamplePagination(pagination.LinkHeaderPagination):
            page_size = 5

        self.pagination = ExamplePagination()
        self.queryset = range(1, 101)

    def paginate_queryset(self, request):
        return list(self.pagination.paginate_query(self.queryset, request))

    def get_paginated_response(self, queryset):
        return self.pagination.get_paginated_response(queryset)

    def get_current_url(self):
        return 'http://testserver/'

    def test_no_page_number(self):
        request = testing.DummyRequest()
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        assert queryset == [1, 2, 3, 4, 5]
        assert response.json_body == [1, 2, 3, 4, 5]  # todo, if renders are ever implemented this needs updated
        assert response.headers['Link'] == '<http://testserver/?page=2>; rel="next", <http://testserver/?page=1>; ' + \
                                           'rel="first", <http://testserver/?page=20>; rel="last"'

    def test_second_page(self):
        request = testing.DummyRequest()
        request.params['page'] = 2
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        assert queryset == [6, 7, 8, 9, 10]
        assert response.json_body == [6, 7, 8, 9, 10]  # todo, if renders are ever implemented this needs updated
        assert response.headers['Link'] == '<http://testserver/?page=3>; rel="next", ' +\
                                           '<http://testserver/>; rel="prev", <http://testserver/?page=1>; ' +\
                                           'rel="first", <http://testserver/?page=20>; rel="last"'

    def test_last_page(self):
        request = testing.DummyRequest()
        request.params['page'] = 'last'
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        queryset = self.paginate_queryset(request)
        response = self.get_paginated_response(queryset)
        assert queryset == [96, 97, 98, 99, 100]
        assert response.json_body == [96, 97, 98, 99, 100]  # todo, if renders are ever implemented this needs updated
        assert response.headers['Link'] == '<http://testserver/?page=19>; rel="prev", <http://testserver/?page=1>; ' +\
                                           'rel="first", <http://testserver/?page=20>; rel="last"'

    def test_invalid_page(self):
        request = testing.DummyRequest()
        request.params['page'] = 'invalid'
        request.current_route_url = mock.Mock(side_effect=self.get_current_url)
        with pytest.raises(HTTPNotFound):
            self.paginate_queryset(request)
