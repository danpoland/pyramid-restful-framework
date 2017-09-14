from sqlalchemy import or_, ARRAY, func


class BaseFilter:
    """
    Base filter that all filter classes must implement.
    """

    def filter_query(self, request, query, view):
        """
        Return the filter query.
        """
        raise NotImplementedError('.filter_query() must be implemented.')  # pragma: no cover


class AttributeBaseFilter(BaseFilter):
    """
    A base class for implementing filters on SQLAlchemy model attributes.
    Supports filtering a comma separated list using OR statements and relationship filter using
    the . path to attribute. WARNING: Every relationship in a . path is joined.

    query_string_lookup: The key to use when parsing the requests query string. The <key> in <key>[<field_name>]=<val>.
    view_attribute_name: The attribute name used in the view that uses the filter that specifies which attributes
                         can be filtered on.
    """

    query_string_lookup = None
    view_attribute_name = None

    def parse_query_string(self, params):
        """
        Override this method if you need to support query string filter keys other than those in the
        format of filter[<field_name>].

        :return: dict
        """
        results = {}

        for key, val in params.items():
            lookup_len = len(self.query_string_lookup) + 1

            if key[0:lookup_len] == '{}['.format(self.query_string_lookup) and key[-1] == ']':
                results[key[lookup_len:-1]] = val

        return results

    def filter_query(self, request, query, view):
        if not request.params:
            return query

        querystring_params = self.parse_query_string(request.params)
        query, filter_list = self.build_filter_list(querystring_params, query, view)

        return self.apply_filter(query, filter_list)

    def build_filter_list(self, querystring_params, query, view):
        filterable_fields = getattr(view, self.view_attribute_name, None)

        if not filterable_fields:
            return query, []

        filter_list = []
        available_fields = list(map(lambda x: '{}.{}'.format(x.parent.class_.__name__, x.name), filterable_fields))

        for key, val in querystring_params.items():
            attrs = key.split('.')  # Every item in the resulting array must be a relationship except for the last
            related_model = view.model
            join_models = []

            for attr in attrs[:-1]:
                # Loop through all the relationships and build the list of tables that need to be joined
                # to the query. The final value of related_model will be the model representing the table
                # with the attribute to be filtered on.

                relationship = getattr(related_model, attr, None)

                if relationship is None:
                    related_model = None
                    break

                related_model = relationship.mapper.class_
                join_models.append(related_model)

            attr = attrs[-1]

            if related_model and hasattr(related_model, attr):
                try:
                    i = available_fields.index('{}.{}'.format(related_model.__name__, attr))
                except ValueError:
                    continue

                joined_tables = [mapper.class_ for mapper in query._join_entities]  # accessing protected attribute?

                for join_model in join_models:
                    if join_model not in joined_tables:
                        query = query.join(join_model)

                filter_list.append(self.build_comparision(filterable_fields[i], val))

        return query, filter_list

    def apply_filter(self, query, filter_list):
        """
        Override this if you need to do something beside calling filter.
        :param query: the query that will be returned from the filter_query method.
        :param filter_list: An array of SQLAlchemy comparative statements.
        :return: The query
        """

        return query.filter(*filter_list)

    def build_comparision(self, field, value):
        """
        Given the model field and the value to be filtered, this should return the statement to be appended
        as a filter to the final query.
        """

        raise NotImplementedError


class FieldFilter(AttributeBaseFilter):
    """
    Filters a query based on the filter_fields set on the view.
    filter_fields should be a list of SQLAlchemy Model columns.

    Comma separated values are treated as ORs. Multiple filter[<field>] query params are AND'd together.
    """

    query_string_lookup = 'filter'
    view_attribute_name = 'filter_fields'

    def build_comparision(self, field, value):
        # Support "IN" filtering
        return or_(*[field == v for v in value.split(',')])


class SearchFilter(AttributeBaseFilter):
    """
    Implements LIKE filtering based on the search[<field_name>]=<val> querystring.
    Comma separated values are treated as ORs.
    Multiple search[<fields>] are or'd together.
    """

    query_string_lookup = 'search'
    view_attribute_name = 'search_fields'

    def build_comparision(self, field, value):
        if issubclass(field.type.__class__, ARRAY):
            return or_(*[field.any(v.lower()) for v in value.split(',')])

        return or_(*[func.lower(field).like('%{}%'.format(v.lower())) for v in value.split(',')])

    def apply_filter(self, query, filter_list):
        return query.filter(or_(*filter_list))


class OrderFilter(AttributeBaseFilter):
    """"
    Allow ordering of the query based on an order[<field>]=<asc | desc> query string.
    """

    query_string_lookup = 'order'
    view_attribute_name = 'order_fields'

    def build_comparision(self, field, value):
        return field if value != 'desc' else field.desc()

    def apply_filter(self, query, filter_list):
        return query.order_by(*filter_list)
