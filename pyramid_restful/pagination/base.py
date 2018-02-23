class BasePagination:
    """
    The base class each Pagination class should implement.
    """

    def paginate_query(self, query, request):
        """
        :param query: SQLAlchemy ``query``.
        :param request: The request from the view
        :return: The paginated date based on the provided query and request.
        """

        raise NotImplementedError('paginate_query() must be implemented.')  # pragma: no cover

    def get_paginated_response(self, data):
        """
        :param data: The paginated data.
        :return: A response containing the paginated data.
        """

        raise NotImplementedError('get_paginated_response() must be implemented.')  # pragma: no cover
