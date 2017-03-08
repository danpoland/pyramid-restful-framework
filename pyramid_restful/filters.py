class BaseFilter:
    """
    Base filter that all filter classes must implement.
    """

    def filter_query(self, request, query, view):
        """
        Return the filter query.
        """
        raise NotImplementedError('.filter_query() must be implemented.')


class FieldFilter(BaseFilter):
    """
    Filters a query based on the filter_fields set on the view.
    filter_fields should be a list of SQLAlchemy Model columns.
    """

    def filter_query(self, request, query, view):
        filter_list = []

        if view.filter_fields and request.params:
            available_fields = list(map(lambda x: x.name, view.filter_fields))
            querystring_params = self.parse_query_string(request.params)

            for key, val in querystring_params.items():
                try:
                    i = available_fields.index(key)
                except ValueError:
                    continue

                filter_list.append(view.filter_fields[i] == val)

        return query.filter(*filter_list) if filter_list else query

    def parse_query_string(self, params):
        """
        Override this method if you need to support query string filter keys other than
        the names of the fields being filtered.

        For example, if your filter querystring param looks like filter[<field_name>], you will
        just want to return a dictionary with just the field_name, value pair.

        :return: dict
        """

        return params


class JSONAPIFilter(FieldFilter):
    """
    Implements filtering based on the JSON API recommended query string style.
    """

    def parse_query_string(self, params):
        """
        Expected filter query strings look like: filter[<field_name>].
        Pyramid takes care of decoding the percent encoded brackets.
        """
        results = {}

        for key, val in params:
            if key[0:7] == 'filter[' and key[-1] == ']':
                results[key[7:-1]] = val

        return results

