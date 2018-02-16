Filters
=======

PRF comes with very simple filter functionality. This functionality will likely be improved in the future. As outlined
in the :doc:`views` documentation you can attach several filter classes to a class that extends ``GenericAPIView``
using the ``filter_classes`` class attribute. All filter classes must extend the ``BaseFilter`` class. PRF comes with
a few predefined filter classes outlined below.


FieldFilter
-----------

The ``FieldFilter`` class allows your requests to filter the query used to return objects from your view using
query string parameters. The query string parameters on the request should be formatted as ``filter[field_name]=val``.
Comma separated values are treated as ORs. Multiple filter query params are AND'd together.

For example given the the ``ViewSet`` definition below and a request with the url of
``https://api.mycoolapp.com/users/?filter[account_id]=1``. The ViewSet would filter the query of users by
``User.account_id`` where the value was ``1``.

.. code-block:: python

    class UserViewSet(ModelCRUDViewSet):
            model = User
            schema = UserSchema
            filter_classes = (FieldFilter,)
            filter_fields = (User.account_id, User.email, User.name,)


SearchFilter
------------

The ``SearchFilter`` class allows requests to filter the query used to return objects from your view using ``LIKE``
statements. Comma separated values are treated as ORs. Multiple search query parameters are OR'd together. The values
are transformed into their all lower-case representation before the comparision is applied.

For example given the the ``ViewSet`` definition below and a request with the url of
``https://api.mycoolapp.com/users/?search[email]=gmail,hotmail``. The ViewSet would filter the query of users with
the a statement similar to: ``WHERE (user.email LIKE '%gmail%' OR  user.email LIKE '%hotmail%')``.

.. code-block:: python

    class UserViewSet(ModelCRUDViewSet):
            model = User
            schema = UserSchema
            filter_classes = (SearchFilter,)
            filter_fields = (User.email,)


OrderFilter
-----------

The ``OrderFilter`` class allows requests to order the results of a request by the fields specified in the
query string parameters. The value of the query string parameter indicates the direction of the ordering. Either ``asc``
or ``desc``.

For example given the the ``ViewSet`` definition below and a request with the url of
``https://api.mycoolapp.com/users/?order[created_at]=desc``. The ViewSet would order the results returned in the
response by the ``User.created_at`` field in descending order.

.. code-block:: python

    class UserViewSet(ModelCRUDViewSet):
            model = User
            schema = UserSchema
            filter_classes = (OrderFilter,)
            filter_fields = (User.created_at,)

