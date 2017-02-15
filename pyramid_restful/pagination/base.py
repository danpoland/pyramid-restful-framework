class BasePagination:

    def paginate_query(self, queryset, request):
        raise NotImplementedError('paginate_queryset() must be implemented.')  # pragma: no cover

    def get_paginated_response(self, data):
        raise NotImplementedError('get_paginated_response() must be implemented.')  # pragma: no cover
