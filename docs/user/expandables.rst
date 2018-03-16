Expandables
===========

Using query string parameters, the expandables mixins allow you to dynamically and efficiently control the expansion of 
relationships in the objects returned from your views. Both the ``ExpandableViewMixin`` and ``ExpandableSchemaMixin``
can be used independently but are most effective when used together.

ExpandableViewMixin
-------------------

The ``ExpandableViewMixin`` allows you to dynamically control the joins executed by your view for each request. Using
the ``expandable_fields`` class attribute you can configure query joins and options based on the values passed into the
``expand`` query string parameter. This allows you to avoid inadvertently executing extra queries that expand
relationships for each object returned from your view. See the :ref:`expandables API <api-expandables.ExpandableViewMixin-label>`
documentation for more information on using the ``expandable_fields`` attribute.

Example::

    from sqlalchemy.orm import subqueryload

    from pyramid_restful import viewsets
    from pyramid_restful.expandables import ExpandableViewMixin


    class AuthorViewSet(viewsets.CRUDModelViewSet,
                        ExpandableViewMixin):
        model = Author
        schema_class = AuthorSchema
        expandable_fields = {
            'books': {'options': [subqueryload(Author.books)]
        }


Using the example class above, a request with a query string of ``?expand=books`` would results in
``subqueryload(Author.books)`` being passed to the ``.options()`` method on the SQLAlchemy query executed by the view.
This effectively performs a single query for all of the books related to the authors returned by the view, which prevents
performing individual quries to retrieve the books for each author returned when the authors are serialized.


ExpandableSchemaMixin
---------------------

The ``ExpandableSchemaMixin`` is a mixin class for ``marshmallow.Schema`` classes. It supports optionally including
``Nested`` fields  based on the value of the query string parameters. The query string parameter's key is
determined by the value of the ``QUERY_KEY`` class attribute.

Fields that can be expanded are defined in the schema's Meta class using the ``expandable_fields`` attribute.
The value of ``expandable_fields`` should be a dictionary. That dictionary's keys should match both the name of the model's
relationship being expanded, and the query string parameter in from the request. The dictionary's values should be a
``marshmallow.fields.Nested`` definition.

Example::

    from marshmallow import Schema, fields

    from pyramid_restful.expandables import ExpandableSchemaMixin

    class AuthorSchema(ExpandableSchemaMixin, schema)
        id = fields.Integer()
        name = fields.String()

        class Meta:
            expandable_fields = {
                'books': fields.Nested('BookSchema')
            }

