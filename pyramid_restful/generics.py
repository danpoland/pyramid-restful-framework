from .views import APIView

from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.orm.exc import NoResultFound

from . import mixins


class GenericAPIView(APIView):
    """
    Provide default functionality for working with RESTFul endpoints.
    pagination_class can be overridden as a class attribute:
    class MyView(GenericAPIView):
        pagination_class = MyPager
    """

    @property
    def pagination_class(self):
        if not hasattr(self, '_pagination_class'):
            # make sure we have the most up to date settings
            # Somebody please come up with something better
            from pyramid_restful.settings import api_settings
            self._pagination_class = api_settings.default_pagination_class

        return self._pagination_class

    model = None  # SQLAlchemy model class
    schema_class = None  # marshmallow schema class
    filter_classes = ()
    lookup_column = 'id'

    def get_query(self):
        assert self.model is not None, (
            "'%s' should include a `model` attribute, "
            "or override the `get_query()` method."
            % self.__class__.__name__
        )

        return self.request.dbsession.query(self.model)

    def get_object(self):
        query = self.filter_query(self.get_query())

        # If query joins more than one table and you need to base the lookup on something besides
        # an id field on the self.model, you can provide an alternative lookup as tuple of the model class
        # and a string of the column name.

        if isinstance(self.lookup_column, str):
            lookup_col = getattr(self.model, self.lookup_column)
            lookup_val = self.lookup_url_kwargs[self.lookup_column]
        else:
            assert isinstance(self.lookup_column, tuple), (
                "'%s' `lookup_column` attribute should be a string or a tuple of (<model class>, `column`) "
                % self.__class__.__name__
            )

            lookup_col = getattr(self.lookup_column[0], self.lookup_column[1])
            lookup_val = self.lookup_url_kwargs[self.lookup_column[1]]

        try:
            instance = query.filter(lookup_col == lookup_val).one()
        except NoResultFound:
            raise HTTPNotFound()

        return instance

    def get_schema_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
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
        klass = self.get_schema_class()
        kwargs['context'] = self.get_schema_context()
        return klass(*args, **kwargs, strict=True)

    def filter_query(self, query):
        """
        Filter the given query using the filter classes specified on the view
        if any are specified.
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
        Return a paginated style `Response` object for the given output data.
        """

        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


# Concrete view classes that provide method handlers
# by composing the mixin classes with the base view.

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
