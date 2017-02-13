from pyramid.response import Response


__all__ = ['ListModelMixin',
           'RetrieveModelMixin',
           'CreateModelMixin',
           'UpdateModelMixin',
           'DestroyModelMixin']


class ListModelMixin:
    """
    List objects.
    """

    def list(self, request, *args, **kwargs):
        query = self.filter_query(self.get_query())
        schema = self.get_schema()
        page = self.paginate_query(query)

        if page is not None:
            content = schema.dump(page, many=True)[0]
            return self.get_paginated_response(content)

        content = schema.dump(query, many=True)[0]
        return Response(json=content)  # todo, hardcoded json here, need to implement parsers


class RetrieveModelMixin:
    """
    Retrieve a single object.
    """

    def retrieve(self, request, *args, **kwargs):
        schema = self.get_schema()
        instance = self.get_object()
        content = schema.dump(instance)[0]

        return Response(json=content)


class CreateModelMixin:
    """
    Create object from serialized data
    """

    def create(self, request, *args, **kwargs):
        schema = self.get_schema()
        data, errors = schema.load(request.json_body)  # todo, hardcoded json here, need to implement parsers

        if errors:
            return Response(json=errors, status=400)  # todo, hardcoded json here, need to implement parsers

        instance = self.perform_create(data)
        content = schema.dump(instance)[0]

        return Response(json=content, status=201)

    def perform_create(self, data):
        """
        Hook for controlling the creation of an model instance
        """

        instance = self.model(**data)
        self.request.dbsession.add(instance)
        self.request.dbsession.flush()
        return instance


class UpdateModelMixin:
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        schema = self.get_schema()

        data, errors = schema.load(request.json_body, partial=partial)  # todo, hardcoded json here, need to implement parsers

        if errors:
            return Response(json_body=errors, status=400)  # todo, hardcoded json here, need to implement parsers

        self.perform_update(data, instance)
        content = schema.dump(instance)[0]
        return Response(json=content)  # todo, hardcoded json here, need to implement parsers

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, data, instance):
        # todo circle back on this and possibly use straight update statement
        for key, val in data.items():
            setattr(instance, key, val)


class DestroyModelMixin:
    """
    Destroy a model instance.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(status=204)

    def perform_destroy(self, instance):
        self.request.dbsession.delete(instance)
