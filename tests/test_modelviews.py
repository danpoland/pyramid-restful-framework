from unittest import TestCase

from pyramid import testing

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.query import Query

from pyramid_restful.modelviews import ModelAPIView

engine = create_engine('sqlite://')
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)


class UserAPIView(ModelAPIView):
    model = User


class UserOverrideView(ModelAPIView):
    model = User

    def get_query(self):
        return self.request.dbsession.query(self.model)


def get_dbsession():
    Session = sessionmaker()
    Session.configure(bind=engine)
    return Session()


class ModelAPIViewUnitTests(TestCase):
    def setUp(self):
        Base.metadata.create_all(engine)

        self.dbsession = get_dbsession()
        self.request = testing.DummyRequest()
        self.request.dbsession = self.dbsession

        user = User(name='testing')
        self.dbsession.add(user)
        self.dbsession.commit()

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

