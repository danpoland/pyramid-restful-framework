views
-----

.. module:: pyramid_restful.views

.. autoclass:: APIView
    :members:

generics
--------

.. module:: pyramid_restful.generics

.. autoclass:: GenericAPIView
    :members:

.. autoclass:: CreateAPIView
    :members:

.. autoclass:: ListAPIView
    :members:

.. autoclass:: RetrieveAPIView
    :members:

.. autoclass:: DestroyAPIView
    :members:

.. autoclass:: UpdateAPIView
    :members:

.. autoclass:: ListCreateAPIView
    :members:

.. autoclass:: RetrieveUpdateAPIView
    :members:

.. autoclass:: RetrieveDestroyAPIView
    :members:

.. autoclass:: RetrieveUpdateDestroyAPIView
    :members:

viewsets
--------

.. module:: pyramid_restful.viewsets

.. autoclass:: ViewSetMixin
    :members:

.. autoclass:: APIViewSet
    :members:

.. autoclass:: GenericAPIViewSet
    :members:

.. autoclass:: ReadOnlyModelViewSet
    :members:

.. autoclass:: ModelCRUDViewSet
    :members:

.. autoclass:: ModelCRPDViewSet
    :members:

.. autoclass:: ModelCRUPDViewSet
    :members:


mixins
------

.. module:: pyramid_restful.mixins

.. autoclass:: ListModelMixin
    :members:

.. autoclass:: RetrieveModelMixin
    :members:

.. autoclass:: CreateModelMixin
    :members:

.. autoclass:: UpdateModelMixin
    :members:

.. autoclass:: PartialUpdateMixin
    :members:

.. autoclass:: DestroyModelMixin
    :members:

.. autoclass:: ActionSchemaMixin
    :members:


decorators
----------

.. module:: pyramid_restful.decorators

.. autofunction:: detail_route

.. autofunction:: list_route


routers
-------

.. module:: pyramid_restful.routers

.. autoclass:: ViewSetRouter
    :members: register

permissions
-----------

.. module:: pyramid_restful.permissions

.. autoclass:: BasePermission
    :members:

filters
-------

.. module:: pyramid_restful.filters

.. autoclass:: BaseFilter
    :members:

.. autoclass:: AttributeBaseFilter
    :members:

.. autoclass:: FieldFilter
    :members:

.. autoclass:: SearchFilter
    :members:

.. autoclass:: OrderFilter
    :members:


expandables
-----------

.. module:: pyramid_restful.expandables

.. autoclass:: ExpandableSchemaMixin
    :members:

.. autoclass:: ExpandableViewMixin
    :members:


pagination
----------

.. module:: pyramid_restful.pagination

.. autoclass:: PageNumberPagination
    :members:

.. autoclass:: LinkHeaderPagination
    :members: