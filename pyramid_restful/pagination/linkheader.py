import math

from pyramid.response import Response

from .pagenumber import PageNumberPagination
from .utilities import replace_query_param


__all__ = ['LinkHeaderPagination']


class LinkHeaderPagination(PageNumberPagination):
    """
    DOC GOES HERE
    """

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        first_url = self.get_first_link()
        last_url = self.get_last_link()

        link = ''

        if next_url is not None and previous_url is not None:
            link = '<{next_url}>; rel="next", <{previous_url}>; rel="prev"'
        elif next_url is not None:
            link = '<{next_url}>; rel="next"'
        elif previous_url is not None:
            link = '<{previous_url}>; rel="prev"'

        if link:
            link += ', <{first_url}>; rel="first", <{last_url}>; rel="last"'

        response = Response(json=data)  # todo, support renderer, should not hard code json
        link = link.format(next_url=next_url, previous_url=previous_url, first_url=first_url, last_url=last_url)

        if link:
            response.headers['Link'] = link
            response.headers['X-Total-Count'] = str(self.page.paginator.count)

        return response

    def get_first_link(self):
        url = self.get_url_root()
        return replace_query_param(url, self.page_query_param, 1)

    def get_last_link(self):
        url = self.get_url_root()
        count = self.page.paginator.count
        page_size = self.get_page_size(self.request)

        total_pages = int(math.ceil(count / float(page_size)))

        return replace_query_param(url, self.page_query_param, total_pages)
