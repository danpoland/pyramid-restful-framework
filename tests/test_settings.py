import pytest

from pyramid_restful.settings import APISettings, reload_api_settings
from pyramid_restful.pagination import PageNumberPagination, LinkHeaderPagination


def test_default_settings():
    settings = APISettings()
    assert settings.default_pagination_class == PageNumberPagination


def test_import_error():
    settings = APISettings({
        'default_pagination_class': [
            'tests.invalid_module.InvalidClassName'
        ]
    })

    with pytest.raises(ImportError):
        settings.default_pagination_class


def test_reload_api_settings():
    reload_api_settings(
        {
            'testrestful.default_pagination_class': 'pyramid_restful.pagination.LinkHeaderPagination',
            'testrestful': 'junk'
        },
        'testrestful'
    )

    from pyramid_restful.settings import api_settings
    api_settings.default_pagination_class == LinkHeaderPagination
