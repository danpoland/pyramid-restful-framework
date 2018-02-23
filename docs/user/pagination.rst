Pagination
==========

PRF has built in support for pagination. You can set the default pagination class for you project using the
``restful.default_pagination_class`` setting. The pagination class can also be set on a per view settings using the
``pagination_class`` class attribute. PRF supports two styles of pagination out of the box, ``PageNumberPagination``
and ``LinkHeaderPagination`` pagination. You can find the details about these pagination classes in the
:ref:`pagination <api-pagination-label>` section of the API docs.


Custom Pagination Classes
-------------------------

To create you own pagination classes simply extend the ``BasePagination`` class and implement the ``paginate_query()``
and ``get_paginated_response()`` methods.