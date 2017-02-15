from unittest import TestCase, mock

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.query import Query

from marshmallow import Schema, fields

from pyramid_restful import modelviews

engine = create_engine('sqlite://')
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class UserSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class UserAPIView(modelviews.ModelAPIView):
    model = User
    schema_class = UserSchema
    filter_fields = [User.name]
    pagination_class = mock.Mock()


class UserOverrideView(modelviews.ModelAPIView):
    model = User
    lookup_column = (User, 'id')

    def get_query(self):
        return self.request.dbsession.query(self.model)

    def get_schema_class(self, *args, **kwargs):
        return UserSchema


def get_dbsession():
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()


class ModelAPIViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(engine)
        cls.dbsession = get_dbsession()

        user = User(id=1, name='testing')
        user2 = User(id=2, name='testing 2')

        cls.dbsession.add(user)
        cls.dbsession.add(user2)
        cls.dbsession.commit()

    @classmethod
    def tearDownClass(cls):
        cls.dbsession.close()

    def setUp(self):
        self.request = testing.DummyRequest()
        self.request.dbsession = self.dbsession

    def test_get_query_w_model(self):
        view = UserAPIView()
        view.request = self.request
        query = view.get_query()
        assert isinstance(query, Query)

    def test_get_query_w_override(self):
        view = UserOverrideView()
        view.request = self.request
        query = view.get_query()
        assert isinstance(query, Query)

    def test_missing_model(self):
        view = modelviews.ModelAPIView()
        view.request = self.request
        self.assertRaises(AssertionError, view.get_query)

    def test_get_object(self):
        view = UserAPIView()
        view.request = self.request
        view.lookup_url_kwargs = {'id': 1}
        instance = view.get_object()
        assert isinstance(instance, User)
        assert instance.id == 1
        assert instance.name == 'testing'

    def test_get_object_override(self):
        view = UserOverrideView()
        view.request = self.request
        view.lookup_url_kwargs = {'id': 1}
        instance = view.get_object()
        assert isinstance(instance, User)
        assert instance.id == 1
        assert instance.name == 'testing'

    def test_get_object_not_found(self):
        view = UserAPIView()
        view.request = self.request
        view.lookup_url_kwargs = {'id': 3}
        self.assertRaises(HTTPNotFound, view.get_object)

    def test_get_schema(self):
        view = UserAPIView()
        view.request = self.request
        schema = view.get_schema()
        assert isinstance(schema, UserSchema)
        assert schema.context['request'] == self.request

    def test_override_get_schema(self):
        view = UserOverrideView()
        view.request = self.request
        schema = view.get_schema()
        assert isinstance(schema, UserSchema)
        assert schema.context['request'] == self.request

    def test_filter_query(self):
        view = UserAPIView()
        self.request.params = {'name': 'testing', 'id': 3}
        view.request = self.request
        results = view.filter_query(view.get_query()).all()
        assert len(results) == 1
        assert results[0].id == 1

    def test_filter_query_empty(self):
        view = UserAPIView()
        self.request.params = {'name': 'testing3'}
        view.request = self.request
        results = view.filter_query(view.get_query()).all()
        assert len(results) == 0

    def test_paginate_query(self):
        view = UserAPIView()
        view.request = self.request
        query = view.get_query()
        view.paginate_query(query)
        view.paginator.paginate_query.assert_called_once()

    def test_no_paginator(self):
        view = UserOverrideView()
        view.request = self.request
        query = view.get_query()
        assert view.paginate_query(query) == None

    def test_get_paginated_response(self):
        view = UserAPIView()
        view.request = self.request
        view.get_paginated_response({})
        view.paginator.get_paginated_response.assert_called_once()


class ConcreteModelAPIViewsTest(TestCase):

    def test_create_api_view_post(self):
        class MockCreateApiView(modelviews.CreateAPIView):
            def create(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockCreateApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.post('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_list_api_view_get(self):
        class MockListApiView(modelviews.ListAPIView):
            def list(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockListApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.get('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_retrieve_api_view_get(self):
        class MockRetrieveApiView(modelviews.RetrieveAPIView):
            def retrieve(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockRetrieveApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.get('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_destroy_api_view_delete(self):
        class MockDestroyApiView(modelviews.DestroyAPIView):
            def destroy(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockDestroyApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.delete('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_update_api_view_partial_update(self):
        class MockUpdateApiView(modelviews.UpdateAPIView):
            def partial_update(self, request, *args, **kwargs):
                self.partial_called = True
                self.partial_call_args = (request, args, kwargs)

            def update(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockUpdateApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.patch('test request', 'test arg', test_kwarg='test')
        assert view.partial_called is True
        assert view.partial_call_args == data

        view.put('test request', 'test arg', test_kwarg='test')
        assert view.partial_called is True
        assert view.partial_call_args == data

    def test_list_create_api_view(self):
        class MockListCreateApiView(modelviews.ListCreateAPIView):
            def list(self, request, *args, **kwargs):
                self.list_called = True
                self.list_call_args = (request, args, kwargs)

            def create(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockListCreateApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.get('test request', 'test arg', test_kwarg='test')
        assert view.list_called is True
        assert view.list_call_args == data

        view.post('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_retrieve_update_api_view_get(self):
        class MockRetrieveUpdateApiView(modelviews.RetrieveUpdateAPIView):
            def retrieve(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockRetrieveUpdateApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.get('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_retrieve_update_api_view_put(self):
        class MockRetrieveUpdateApiView(modelviews.RetrieveUpdateAPIView):
            def update(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockRetrieveUpdateApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.put('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_retrieve_update_api_view_patch(self):
        class MockRetrieveUpdateApiView(modelviews.RetrieveUpdateAPIView):
            def partial_update(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockRetrieveUpdateApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.patch('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_retrieve_destroy_api_view_get(self):
        class MockRetrieveDestroyUApiView(modelviews.RetrieveDestroyAPIView):
            def retrieve(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockRetrieveDestroyUApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.get('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_retrieve_destroy_api_view_delete(self):
        class MockRetrieveDestroyUApiView(modelviews.RetrieveDestroyAPIView):
            def destroy(self, request, *args, **kwargs):
                self.called = True
                self.call_args = (request, args, kwargs)

        view = MockRetrieveDestroyUApiView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.delete('test request', 'test arg', test_kwarg='test')
        assert view.called is True
        assert view.call_args == data

    def test_retrieve_update_destroy_api_view(self):
        class MockRetrieveUpdateDestroyAPIView(modelviews.RetrieveUpdateDestroyAPIView):
            def retrieve(self, request, *args, **kwargs):
                self.r_called = True
                self.r_call_args = (request, args, kwargs)

            def destroy(self, request, *args, **kwargs):
                self.d_called = True
                self.d_call_args = (request, args, kwargs)

            def update(self, request, *args, **kwargs):
                self.u_called = True
                self.u_call_args = (request, args, kwargs)

            def partial_update(self, request, *args, **kwargs):
                self.p_called = True
                self.p_call_args = (request, args, kwargs)

        view = MockRetrieveUpdateDestroyAPIView()
        data = ('test request', ('test arg',), {'test_kwarg': 'test'})
        view.get('test request', 'test arg', test_kwarg='test')
        view.delete('test request', 'test arg', test_kwarg='test')
        view.put('test request', 'test arg', test_kwarg='test')
        view.patch('test request', 'test arg', test_kwarg='test')
        assert view.r_called is True
        assert view.r_call_args == data
        assert view.d_called is True
        assert view.d_call_args == data
        assert view.u_called is True
        assert view.u_call_args == data
        assert view.p_called is True
        assert view.p_call_args == data

