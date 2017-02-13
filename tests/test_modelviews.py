from unittest import TestCase

from pyramid import testing
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.query import Query

from marshmallow import Schema, fields

from pyramid_restful.modelviews import ModelAPIView

engine = create_engine('sqlite://')
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class UserSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class UserAPIView(ModelAPIView):
    model = User
    schema_class = UserSchema
    filter_fields = [User.name]


class UserOverrideView(ModelAPIView):
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


class ModelAPIViewUnitTests(TestCase):
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
        view = ModelAPIView()
        view.request = self.request
        self.assertRaises(AssertionError, view.get_query)

    def test_get_object(self):
        view = UserAPIView()
        view.request = self.request
        view.url_lookup_kwargs = {'id': 1}
        instance = view.get_object()
        assert isinstance(instance, User)
        assert instance.id == 1
        assert instance.name == 'testing'

    def test_get_object_override(self):
        view = UserAPIView()
        view.request = self.request
        view.url_lookup_kwargs = {'id': 1}
        instance = view.get_object()
        assert isinstance(instance, User)
        assert instance.id == 1
        assert instance.name == 'testing'

    def test_get_object_not_found(self):
        view = UserAPIView()
        view.request = self.request
        view.url_lookup_kwargs = {'id': 3}
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
        self.request.params = {'name': 'testing'}
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
