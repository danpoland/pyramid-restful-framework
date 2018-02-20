Expandables
===========

The expandables mixins allow you to dynamically and efficiently control the expansion of relationships in the objects
returned from your views using query string parameters. Both the ``ExpandableViewMixin`` and ``ExpandableSchemaMixin``
can be used independently but are most effective when used together.

ExpandableViewMixin
-------------------

The ``ExpandableViewMixin`` allows you to dynamically control the joins executed by your view for each request. Using
the ``expandable_fields`` class attribute you can configure query joins and options based on the values passed into the
``expand`` query string parameter. This allows you to avoid inadvertently executing extra queries to expand
relationships for each object returned from your view. See the :doc:`../api` documentation for more information on
using the the ``expandable_fields`` attribute.

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
This effectively pre-queries all the books related to the authors returned by the view so that the individual quries
to retrieve the books are not executed for each author returned.


ExpandableSchemaMixin
---------------------

The ``ExpandableSchemaMixin`` is a mixin class for ``marshmallow.Schema`` classes. It supports optionally included
``Nested`` fields  based on the value of the query string parameters. The query string parameter's key is
determined by the value of the ``QUERY_KEY`` class attribute.

Fields that can be expanded are defined in the schema's Meta class using the ``expandable_fields`` attribute.
The value of ``expandable_fields`` should be a dictionary who's keys are used to match the value of the request's
query string parameter and the value should be a ``marshmallow.fields.Nested`` definition.

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

