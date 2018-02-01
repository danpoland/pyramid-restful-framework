import json

from collections import namedtuple

from unittest import TestCase, mock

from marshmallow import Schema, fields

from pyramid_restful.expandables import ExpandableSchemaMixin, ExpandableViewMixin

Account = namedtuple('Account', ['id', 'owner_id', 'profile_id', 'owner', 'profile'])
User = namedtuple('User', ['id', 'name'])
Profile = namedtuple('Profile', ['id', 'created_date'])


class UserSchema(Schema):
    id = fields.Integer()
    name = fields.String()


class AccountSchema(ExpandableSchemaMixin, Schema):
    id = fields.Integer()
    owner_id = fields.Integer()
    profile_id = fields.Integer()

    class Meta:
        expandable_fields = {'owner': fields.Nested(UserSchema, required=False)}


class AccountView:
    def get_query(self):
        return mock.Mock()


class ExpandableAccountView(ExpandableViewMixin, AccountView):
    schema_class = AccountSchema
    expandable_fields = {'owner': {
        'join': 'owner_id'
    }}


class ExpandablesSchemaTests(TestCase):
    """
    ExpandableSchemaMixin integration tests.
    """

    def setUp(self):
        self.user = User(id=99, name='test user')
        self.profile = Profile(id=50, created_date='20170214')
        self.account = Account(id=1, owner_id=99, profile_id=50, owner=self.user, profile=self.profile)

    def test_expandable_schema_mixin(self):
        request = mock.Mock()
        request.params = {'expand': 'owner'}
        schema = AccountSchema(context={'request': request})
        content = schema.dump(self.account)[0]
        assert content == {'id': 1, 'owner_id': 99, 'profile_id': 50, 'owner': {'id': 99, 'name': 'test user'}}

    def test_expandable_schema_mixin_not_available(self):
        request = mock.Mock()
        request.params = {'expand': 'profile'}
        schema = AccountSchema(context={'request': request})
        content = schema.dump(self.account)[0]
        assert content == {'id': 1, 'owner_id': 99, 'profile_id': 50}


class ExpandableViewTests(TestCase):
    """
    ExpandableViewMixin unit tests.
    """

    def test_expandable_view_mixin(self):
        request = mock.Mock()
        request.params = {'expand': 'owner'}
        view = ExpandableAccountView()
        view.request = request
        query = view.get_query()
        assert query.join.called_once_with('owner_id')

    def test_expandable_view_mixin_outer_join(self):
        request = mock.Mock()
        request.params = {'expand': 'owner'}
        view = ExpandableAccountView()
        view.expandable_fields = {'owner': {
            'outerjoin': 'owner_id',
        }}
        view.request = request
        query = view.get_query()
        assert query.outerjoin.called_once_with('owner_id')

    def test_expandable_view_mixin_options(self):
        request = mock.Mock()
        request.params = {'expand': 'owner'}
        view = ExpandableAccountView()
        view.expandable_fields = {'owner': {
            'join': 'owner_id',
            'options': {'preselect': True}
        }}
        view.request = request
        query = view.get_query()
        assert query.options.called_once_with({'preselect': True})
