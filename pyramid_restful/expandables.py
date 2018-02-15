from marshmallow import SchemaOpts, pre_dump

__all__ = ['ExpandableSchemaMixin',
           'ExpandableViewMixin',
           'ExpandableOpts']


def parse_requested_expands(query_key, request):
    """
    Extracts the value of the expand query string parameter from a request.
    Supports comma separated lists.

    :param query_key: The name query string parameter.
    :param request: Request instance.
    :return: List of strings representing the values of the expand query string value.
    """

    requested_expands = []

    for key, val in request.params.items():
        if key == query_key:
            requested_expands += val.split(',')

    return requested_expands


class ExpandableOpts(SchemaOpts):
    """
    Adds support for expandable_fields to Class Meta. `expandable_fields` should be a
    dict of key = field name to be added to serialized results and val = a marshmallow Nested field.

    Example:
        expandable_fields = {'paymentmethod': fields.Nested(PaymentMethodSchema, required=False)}
    """

    def __init__(self, meta):
        super(ExpandableOpts, self).__init__(meta)
        self.expandable_fields = getattr(meta, 'expandable_fields', dict())


class ExpandableSchemaMixin:
    """
    A mixin class for ``marshmallow.Schema`` classes. Supports optionally expandable fields based on the value of
    the query string parameters. The query string parameter's key is determined by the value of the ``QUERY_KEY``
    class attribute.

    Fields that can be expanded are defined in the schema's Meta class using the ``expandable_fields`` attribute.
    The value of ``expandable_fields`` should be a dictionary who's keys are used to match the value of the requests's
    query string parameter and the value should be a ``marshmallow.fields.Nested`` definition.

    **Usage**::

        from marshmallow import Schema, fields

        from pyramid_restful.expandables import ExpandableSchemaMixin

        class UserSchema(ExpandableSchemaMixin, schema)
            id = fields.Integer()
            name = fields.String()
            email = fields.String()

            class Meta:
                expandable_fields = {
                'account': fields.Nested('AccountSchema')
            }

    """

    OPTIONS_CLASS = ExpandableOpts
    #: The query string parameter name used for expansion.
    QUERY_KEY = 'expand'

    @pre_dump
    def update_expandables(self, data):
        request = self.context.get('request')

        if request:
            requested_expands = parse_requested_expands(self.QUERY_KEY, request)
            available_expands = self.opts.expandable_fields.keys()

            for field in requested_expands:
                if field in available_expands:
                    self.declared_fields[field] = self.opts.expandable_fields[field]

        return data


class ExpandableViewMixin:
    """
    Optionally used to allow more fine grained control over the query used to pull data.
    ``expandable_fields`` should be a dictionary of key = the field name that is expandable
    and val = a dict with the following keys.

    - **join (optional)**: A table column to join() to the query.
    - **outerjoin (optional)**: A table column to outerjoin() to the query.
    - **options (optional)**: A list passed to the constructed queries' options method. \
    This is where you want to include the related objects to expand on. \
    Without a value you here you will likely end up running lots of extra queries.

    Example::

        expandable_fields = {
            'author': {'join': Book.author, 'options': [joinedload(Book.author)]
        }

    """

    #: A dictionary of the fields can be expanded. Its definition is described above.
    expandable_fields = None

    def get_query(self):
        """
        If you override this method do not forget to call ``super()``.
        """

        query = super(ExpandableViewMixin, self).get_query()
        expandable_fields = getattr(self, 'expandable_fields', [])

        if expandable_fields:
            requested_expands = parse_requested_expands(self.schema_class.QUERY_KEY, self.request)

            if requested_expands:
                available_expands = self.expandable_fields.keys()

                for name in requested_expands:
                    if name in available_expands:
                        field = self.expandable_fields[name]

                        innerjoin = field.get('join')
                        outerjoin = field.get('outerjoin')

                        if innerjoin:
                            query = query.join(innerjoin)
                        elif outerjoin:
                            query = query.outerjoin(outerjoin)

                        # Apply optional options
                        options = field.get('options')

                        if options:
                            query = query.options(*options)

        return query
