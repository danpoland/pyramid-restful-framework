from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy.orm.exc import NoResultFound

from pyramid_restful.settings import api_settings

from .views import APIView
from . import mixins


class GenericAPIView(APIView):
    """
    Provide default functionality for working with RESTFul endpoints.
    pagination_class can be overridden as a class attribute:

    Usage::

        class MyView(GenericAPIView):
            pagination_class = MyPager

    """

    #: Controls which pagination class should be used for the class. Defaults to the ``default_pagination_class``
    #: configuration for pyramid
    pagination_class = api_settings.default_pagination_class
    #: The SQLAlchemy model class used by the view.
    model = None
    #: The marshmallow schema class used by the view.
    schema_class = None
    #: Iterable of Filter classes to be used with the view.
    filter_classes = ()
    #: The name of the primary key field in the model used by the view.
    lookup_field = 'id'

    def get_query(self):
        """
        Get the list of items for this view.
        You may want to override this if you need to provide different query  depending on the incoming request.
        (Eg. return a list of items that is specific to the user)

        :return: ``sqlalchemy.orm.query.Query``
        """

        assert self.model is not None, (
            "'{}' should include a `model` attribute, or override the `get_query()` method."
                .format(self.__class__.__name__)
        )

        return self.request.dbsession.query(self.model)

    def get_object(self):
        """
        Returns the object the view is displaying.
        You may want to override this if you need to provide non-standard queryset lookups.
        Eg if objects are referenced using multiple keyword arguments in the url conf.

        :return: An instance of the view's model.
        """

        query = self.filter_query(self.get_query())

        # If query joins more than one table and you need to base the lookup on something besides
        # an id field on the self.model, you can provide an alternative lookup as tuple of the model class
        # and a string of the column name.
        if isinstance(self.lookup_field, str):
            lookup_col = getattr(self.model, self.lookup_field)
            lookup_val = self.lookup_url_kwargs[self.lookup_field]
        else:
            assert isinstance(self.lookup_field, tuple), (
                "'{}' `lookup_field` attribute should be a string or a tuple of (<model class>, `column`) "
                    .format(self.__class__.__name__)
            )

            lookup_col = getattr(self.lookup_field[0], self.lookup_field[1])
            lookup_val = self.lookup_url_kwargs[self.lookup_field[1]]

        try:
            instance = query.filter(lookup_col == lookup_val).one()
        except NoResultFound:
            raise HTTPNotFound()

        # May raise HTTPForbidden
        self.check_object_permissions(self.request, instance)

        return instance

    def get_schema_class(self):
        """
        Return the class to use for the schema. Defaults to using `self.schema_class`.
        You may want to override this if you need to provide different serializations depending on the incoming request.
        """

        assert self.schema_class is not None, (
                "'%s' should either include a `schema_class` attribute, "
                "or override the `get_schema_class()` method."
                % self.__class__.__name__
        )

        return self.schema_class

    def get_schema_context(self):
        """
        Extra context provided to the schema class.
        """

        return {'request': self.request}

    def get_schema(self, *args, **kwargs):
        """
        Return the schema instance that should be used for validating and
        deserializing input, and for serializing output.
        """

        klass = self.get_schema_class()

        # kwargs context value take precedence.
        kwargs['context'] = dict(
            self.get_schema_context(),
            **kwargs.get('context', {})
        )

        return klass(*args, strict=True, **kwargs)

    def filter_query(self, query):
        """
        Filter the given query using the filter classes specified on the view if any are specified.
        """

        for filter_class in list(self.filter_classes):
            query = filter_class().filter_query(self.request, query, self)

        return query

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """

        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()

        return self._paginator

    def paginate_query(self, query):
        """
        Return single page of results or `None` if pagination is disabled.
        """

        if self.paginator is None:
            return None

        return self.paginator.paginate_query(query, self.request)

    def get_paginated_response(self, data):
        """
        Return a paginated style ``Response`` object for the given output data.
        """

        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


# Concrete view classes that provide method handlers by composing the mixin classes with the base view.

class CreateAPIView(mixins.CreateModelMixin,
                    GenericAPIView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(mixins.ListModelMixin,
                  GenericAPIView):
    """
    Concrete view for listing a queryset.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin,
                      GenericAPIView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyModelMixin,
                     GenericAPIView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateModelMixin,
                    mixins.PartialUpdateMixin,
                    GenericAPIView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.PartialUpdateMixin,
                            GenericAPIView):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(mixins.RetrieveModelMixin,
                             mixins.DestroyModelMixin,
                             GenericAPIView):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(mixins.RetrieveModelMixin,
                                   mixins.UpdateModelMixin,
                                   mixins.PartialUpdateMixin,
                                   mixins.DestroyModelMixin,
                                   GenericAPIView):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
