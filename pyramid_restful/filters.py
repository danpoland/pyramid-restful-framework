from sqlalchemy import or_


class BaseFilter:
    """
    Base filter that all filter classes must implement.
    """

    def filter_query(self, request, query, view):
        """
        Return the filter query.
        """
        raise NotImplementedError('.filter_query() must be implemented.')  # pragma: no cover


class FieldFilter(BaseFilter):
    """
    Filters a query based on the filter_fields set on the view.
    filter_fields should be a list of SQLAlchemy Model columns.
    Supports filtering a comma separated list using OR statements.
    Supports relationship filter using the . path to attribute. WARNING: Every relationship in a . path is joined.
    """

    def filter_query(self, request, query, view):
        if not view.filter_fields or not request.params:
            return query

        filter_list = []
        querystring_params = self.parse_query_string(request.params)
        available_fields = list(map(lambda x: '{}.{}'.format(x.parent.class_.__name__, x.name), view.filter_fields))

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

                # If there is only one comparison in or_ it is just AND'd on the query
                filter_list.append(or_(*[view.filter_fields[i] == v for v in val.split(',')]))

            query = query.filter(*filter_list)

        return query

    def parse_query_string(self, params):
        """
        Override this method if you need to support query string filter keys other than
        the names of the fields being filtered.

        For example, if your filter querystring param looks like filter[<field_name>], you will
        just want to return a dictionary with just the field_name, value pair.

        :return: dict
        """

        return params
