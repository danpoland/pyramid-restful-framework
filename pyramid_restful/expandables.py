from marshmallow import SchemaOpts, pre_dump

__all__ = ['ExpandableSchemaMixin',
           'ExpandableViewMixin',
           'ExpandableOpts']


class ExpandableOpts(SchemaOpts):
    """
    Adds support for expandable_fields to Class Meta. `expandable_fields` should be a
    dict of key = field name to be added to serialized results and val = a marshmallow Nested field.

    Example:
        expandable_fields = dict(paymentmethod=fields.Nested(PaymentMethodSchema, required=False))
    """

    def __init__(self, meta):
        super(ExpandableOpts, self).__init__(meta)
        self.expandable_fields = getattr(meta, 'expandable_fields', dict())


class ExpandableSchemaMixin:
    """
    Supports optionally expandable fields based on QUERY_KEY query strings included in the request's url.
    """

    OPTIONS_CLASS = ExpandableOpts
    QUERY_KEY = 'expand'

    @pre_dump
    def update_expandables(self, data):
        request = self.context.get('request')

        if request:
            requested_expands = list(val for key, val in request.params.items() if key == self.QUERY_KEY)
            available_expands = self.opts.expandable_fields.keys()

            for field in requested_expands:
                if field in available_expands:
                    self.declared_fields[field] = self.opts.expandable_fields[field]

        return data


class ExpandableViewMixin:
    """
    Optionally used to allow more fine grained control over the query used to pull data.
    `expandable_fields` should be a dict of key = the field name that is expandable
    and val = is a dict with the following keys:

    column (required): The table column that represents the relationship to be expanded.
    outerjoin (optional): Whether or not to use an outer join when joining the relationship.
    options (optional): list passed to the constructed queries' options method.

    Example:
        expandable_fields = {
            'author': {'column': Book.author, 'options': [joinedload(Book.author)]
        }
    """

    expandable_fields = None

    def get_query(self):
        """
        If your query is more complicated than what is supported below, override this method.
        Don't forget to call super though.
        The value of schema_class.QUERY_KEY supports comma separated lists.
        """

        query = super(ExpandableViewMixin, self).get_query()
        expandable_fields = getattr(self, 'expandable_fields', [])
        query_key = self.schema_class.QUERY_KEY

        if expandable_fields:
            requested_expands = []

            for key, val in self.request.params.items():
                if key == query_key:
                    requested_expands += val.split(',')

            if requested_expands:
                available_expands = self.expandable_fields.keys()

                for name in requested_expands:
                    if name in available_expands:
                        field = self.expandable_fields[name]

                        if field.get('outerjoin', False):
                            query = query.outerjoin(field['column'])
                        else:
                            query = query.join(field['column'])

                        # Apply optional options
                        options = field.get('options')

                        if options:
                            query = query.options(*options)

        return query
