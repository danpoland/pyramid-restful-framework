import warnings
import six

from math import ceil

from collections import OrderedDict, Sequence

from sqlalchemy.orm.query import Query

from pyramid.exceptions import HTTPNotFound
from pyramid.response import Response

from .utilities import remove_query_param, replace_query_param
from .base import BasePagination

__all__ = ['PageNumberPagination']


def _positive_int(integer_string, strict=False, cutoff=None):
    """
    Cast a string to a strictly positive integer.
    """
    ret = int(integer_string)

    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        ret = min(ret, cutoff)

    return ret


class InvalidPage(Exception):
    pass


class PageNotAnInteger(InvalidPage):
    pass


class EmptyPage(InvalidPage):
    pass


class UnorderedObjectListWarning(RuntimeWarning):
    pass


class Paginator:
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        self.object_list = object_list
        self._check_object_list_is_ordered()
        self.per_page = int(per_page)
        self.orphans = int(orphans)
        self.allow_empty_first_page = allow_empty_first_page

    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return number

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return self._get_page(self.object_list[bottom:top], number, self)

    def _get_page(self, *args, **kwargs):
        """
        Returns an instance of a single page.
        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return Page(*args, **kwargs)

    @property
    def count(self):
        """
        Returns the total number of objects, across all pages.
        """
        try:
            return self.object_list.count()
        except (AttributeError, TypeError):
            # AttributeError if object_list has no count() method.
            # TypeError if object_list.count() requires arguments
            # (i.e. is of type list).
            return len(self.object_list)

    @property
    def num_pages(self):
        """
        Returns the total number of pages.
        """
        if self.count == 0 and not self.allow_empty_first_page:
            return 0
        hits = max(1, self.count - self.orphans)
        return int(ceil(hits / float(self.per_page)))

    @property
    def page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a template for loop.
        """
        return range(1, self.num_pages + 1)

    def _check_object_list_is_ordered(self):
        """
        Warn if self.object_list is unordered (typically a QuerySet).
        """
        if hasattr(self.object_list, 'ordered') and not self.object_list.ordered:
            warnings.warn(
                'Pagination may yield inconsistent results with an unordered '
                'object_list: {!r}'.format(self.object_list),
                UnorderedObjectListWarning
            )


class Page(Sequence):

    def __init__(self, object_list, number, paginator):
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self):
        return '<Page %s of %s>' % (self.number, self.paginator.num_pages)

    def __len__(self):
        return len(self.object_list)

    def __getitem__(self, index):
        if not isinstance(index, (int, slice)):
            raise TypeError
        # The object_list is converted to a list so that if it was a QuerySet
        # it won't be a database hit per __getitem__.
        if not isinstance(self.object_list, list):
            self.object_list = list(self.object_list)
        return self.object_list[index]

    def has_next(self):
        return self.number < self.paginator.num_pages

    def has_previous(self):
        return self.number > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.paginator.validate_number(self.number + 1)

    def previous_page_number(self):
        return self.paginator.validate_number(self.number - 1)

    def start_index(self):
        """
        Returns the 1-based index of the first object on this page,
        relative to total objects in the paginator.
        """
        # Special case, return zero if no items.
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    def end_index(self):
        """
        Returns the 1-based index of the last object on this page,
        relative to total objects found (hits).
        """
        # Special case for the last page because there can be orphans.
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page


class PageNumberPagination(BasePagination):
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:

    http://api.example.org/accounts/?page=4
    http://api.example.org/accounts/?page=4&page_size=100
    """

    page_size = 100  # todo make configurable

    paginator_class = Paginator

    # Client can control the page using this query parameter.
    page_query_param = 'page'

    # Client can control the page size using this query parameter.
    # Default is 'None'. Set to eg 'page_size' to enable usage.
    page_size_query_param = None

    # Set to an integer to limit the maximum page size the client may request.
    # Only relevant if 'page_size_query_param' has also been set.
    max_page_size = None

    last_page_strings = ('last',)

    invalid_page_message = 'Invalid page "{page_number}": {message}.'

    def paginate_query(self, query, request):
        self.request = request

        # Force the execution of the query, so we don't make unnecessary db calls
        data = query.all() if isinstance(query, Query) else query
        page_size = self.get_page_size(request)

        if not page_size:
            return None

        page_number = request.params.get(self.page_query_param, 1)
        paginator = self.paginator_class(data, page_size)

        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise HTTPNotFound(msg)

        return list(self.page)

    def get_paginated_response(self, data):
        return Response(json=OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(
                    request.params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_next_link(self):
        if not self.page.has_next():
            return None

        url = self.request.current_route_url()
        page_number = self.page.next_page_number()

        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None

        url = self.request.current_route_url()
        page_number = self.page.previous_page_number()

        if page_number == 1:
            return remove_query_param(url, self.page_query_param)

        return replace_query_param(url, self.page_query_param, page_number)
