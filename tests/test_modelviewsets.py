import json

from unittest import TestCase, mock

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from marshmallow import Schema, fields

from pyramid import testing

from pyramid_restful import modelviewsets

engine = create_engine('sqlite://')
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String)


class UserSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class UserViewSet(modelviewsets.ModelCRUDViewSet):
    model = User
    schema_class = UserSchema


def get_dbsession():
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()


class ModelViewSetTests(TestCase):

    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(engine)
        dbsession = get_dbsession()

        user = User(id=1, name='testing')
        user2 = User(id=2, name='testing 2')

        dbsession.add(user)
        dbsession.add(user2)
        dbsession.commit()

    def setUp(self):
        self.dbsession = get_dbsession()
        self.list_viewset = UserViewSet.as_view({'get': 'list', 'post': 'create'})
        self.detail_viewset = UserViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
        self.request = testing.DummyRequest()
        self.request.dbsession = self.dbsession

    def tearDown(self):
        self.dbsession.close()

    def test_list(self):
        response = self.list_viewset(self.request)
        assert response.status_code == 200
        assert json.loads(response.body) == [{"id": 1, "name": "testing"}, {"id": 2, "name": "testing 2"}]

    def test_create(self):
        expected = {'id': 3, 'name': 'testing 3'}
        self.request.json_body = expected
        self.request.method = 'POST'
        response = self.list_viewset(self.request)
        assert response.status_code == 201
        assert json.loads(response.body) == expected

    def test_retrieve(self):
        expected = {'id': 1, 'name': 'testing'}
        self.request.matchdict['id'] = 1
        response = self.detail_viewset(self.request)
        assert response.status_code == 200
        assert json.loads(response.body) == expected

    def test_object_does_not_exist(self):
            self.request.matchdict['id'] = 99
            response = self.detail_viewset(self.request)
            assert response.status_code == 404

    def test_update(self):
        expected = {'id': 1, 'name': 'testing 1'}
        self.request.matchdict['id'] = 1
        self.request.method = 'PUT'
        self.request.json_body = expected
        response = self.detail_viewset(self.request)
        assert response.status_code == 200
        assert json.loads(response.body) == expected

    def test_partial_update(self):
        expected = {'id': 1, 'name': '1'}
        self.request.matchdict['id'] = 1
        self.request.method = 'PATCH'
        self.request.json_body = {'name': '1'}
        response = self.detail_viewset(self.request)
        assert response.status_code == 200
        assert json.loads(response.body) == expected

    def test_destroy(self):
        self.request.matchdict['id'] = 1
        self.request.method = 'DELETE'
        response = self.detail_viewset(self.request)
        assert response.status_code == 204

        self.request.method = 'GET'
        response = self.detail_viewset(self.request)
        assert response.status_code == 404
