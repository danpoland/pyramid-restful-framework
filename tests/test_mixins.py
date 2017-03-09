from unittest import TestCase, mock

import marshmallow as ma

from pyramid import testing
from pyramid.response import Response

from pyramid_restful import mixins


class MockAPIView:
    def model_side_effect(**data):
        instance = mock.Mock()

        for key, val in data.items():
            setattr(instance, key, val)

        return instance

    model = mock.Mock(side_effect=model_side_effect)
    dataset = [
        {'name': 'testing', 'id': 1},
        {'name': 'testing 2', 'id': 2}
    ]

    def get_query(self):
        ret = []

        for data in self.dataset:
            instance = mock.Mock()
            for key, val in data.items():
                setattr(instance, key, val)
            ret.append(instance)

        return ret

    def filter_query(self, query):
        return query

    def get_schema(self):
        def dump(data, many=False, **kwargs):
            if many:
                return [{'id': i.id, 'name': i.name} for i in data], ''

            return {'id': data.id, 'name': data.name}, ''

        def load(data, partial=False):
            if not partial and data['id'] == 4:
                raise ma.ValidationError(message={'id': ['invalid value.']})
            return data, ''

        schema = mock.Mock()
        schema.dump = mock.Mock(side_effect=dump)
        schema.load = mock.Mock(side_effect=load)

        return schema

    def paginate_query(self, data):
        return [data[0]]

    def get_paginated_response(self, data):
        return Response(json_body=data)

    def get_object(self):
        instance = mock.Mock()

        for key, val in self.dataset[0].items():
            setattr(instance, key, val)

        return instance


class MockAPIViewNoPage(MockAPIView):
    def paginate_query(self, data):
        return None


class ActionMixinView(mixins.ActionSchemaMixin):
    retrieve_schema = 'retrieve_schema'
    list_schema = 'list_schema'
    update_schema = 'update_schema'
    create_schema = 'create_schema'
    destroy_schema = 'destroy_schema'
    schema_class = 'schema_class'


# ------ Tests ------

class ModelMixinUnitTests(TestCase):
    def setUp(self):
        self.request = testing.DummyRequest()
        self.request.dbsession = mock.Mock()

    def test_list_mixin(self):
        class ListViewTest(mixins.ListModelMixin, MockAPIView):
            pass

        view = ListViewTest()
        response = view.list(self.request)
        assert response.status_code == 200
        assert response.body == b'[{"id":1,"name":"testing"}]'

    def test_list_mixin_no_page(self):
        class ListViewTest(mixins.ListModelMixin, MockAPIViewNoPage):
            pass

        view = ListViewTest()
        response = view.list(self.request)
        assert response.status_code == 200
        assert response.body == b'[{"id":1,"name":"testing"},{"id":2,"name":"testing 2"}]'

    def test_retrieve_mixin(self):
        class RetrieveViewTest(mixins.RetrieveModelMixin, MockAPIView):
            pass

        view = RetrieveViewTest()
        response = view.retrieve(self.request, id=1)
        assert response.status_code == 200
        assert response.body == b'{"id":1,"name":"testing"}'

    def test_create_mixin(self):
        class CreateViewTest(mixins.CreateModelMixin, MockAPIView):
            pass

        view = CreateViewTest()
        view.request = self.request
        self.request.json_body = {'id': 3, 'name': 'testing 3'}
        response = view.create(self.request)
        assert response.status_code == 201
        assert response.body == b'{"id":3,"name":"testing 3"}'
        self.request.dbsession.add.assert_called_once()

    def test_bad_create_mixin(self):
        class CreateViewTest(mixins.CreateModelMixin, MockAPIView):
            pass

        view = CreateViewTest()
        view.request = self.request
        self.request.json_body = {'id': 4, 'name': 'testing 4'}
        response = view.create(self.request)
        assert response.status_code == 400
        assert response.body == b'{"id":["invalid value."]}'

    def test_update(self):
        class UpdateViewTest(mixins.UpdateModelMixin, MockAPIView):
            pass

        view = UpdateViewTest()
        self.request.json_body = {'id': 1, 'name': 'testing1'}
        response = view.update(self.request)
        assert response.status_code == 200
        assert response.body == b'{"id":1,"name":"testing1"}'

    def test_bad_update(self):
        class UpdateViewTest(mixins.UpdateModelMixin, MockAPIView):
            pass

        view = UpdateViewTest()
        self.request.json_body = {'id': 4, 'name': '4testing'}
        response = view.update(self.request)
        assert response.status_code == 400

    def test_partial_update(self):
        class UpdateViewTest(mixins.PartialUpdateMixin, MockAPIView):
            pass

        view = UpdateViewTest()
        self.request.json_body = {'name': 'testing1'}
        response = view.partial_update(self.request)
        assert response.status_code == 200
        assert response.body == b'{"id":1,"name":"testing1"}'

    def test_destroy(self):
        class DestroyViewTest(mixins.DestroyModelMixin, MockAPIView):
            pass

        view = DestroyViewTest()
        view.request = self.request
        response = view.destroy(self.request)
        assert response.status_code == 204
        self.request.dbsession.delete.assert_called_once()


class TestActionSchemaMixin(TestCase):

    def setUp(self):
        self.view = ActionMixinView()

    def test_retrieve(self):
        self.view.action = 'retrieve'
        assert self.view.get_schema_class() == 'retrieve_schema'

    def test_list(self):
        self.view.action = 'list'
        assert self.view.get_schema_class() == 'list_schema'

    def test_update(self):
        self.view.action = 'update'
        assert self.view.get_schema_class() == 'update_schema'

    def test_partial_update(self):
        self.view.action = 'partial_update'
        assert self.view.get_schema_class() == 'update_schema'

    def test_create(self):
        self.view.action = 'create'
        assert self.view.get_schema_class() == 'create_schema'

    def test_destroy(self):
        self.view.action = 'destroy'
        assert self.view.get_schema_class() == 'destroy_schema'

    def test_default(self):
        self.view.action = 'default'
        assert self.view.get_schema_class() == 'schema_class'
