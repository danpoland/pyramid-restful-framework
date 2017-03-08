from unittest.mock import MagicMock, Mock


from pyramid_restful.filters import FieldFilter


def test_field_filter():
    def return_args(*args, **kwargs):
        return args, kwargs

    view = MagicMock()
    name_field = MagicMock()
    name_field.name = 'name'
    view.filter_fields = [name_field]

    request = MagicMock()
    request.params = {'name': 'test'}

    query = MagicMock()
    query.filter = Mock(side_effect=return_args)

    fltr = FieldFilter()
    results = fltr.filter_query(request, query, view)
    expected = ((name_field == 'test', ), {})

    assert results == expected
