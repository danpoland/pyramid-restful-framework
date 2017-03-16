import pytest

from pyramid_restful.settings import APISettings, reload_api_settings, DEFAULTS
from pyramid_restful.pagination import PageNumberPagination


class TestPagination(PageNumberPagination):
    pass


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
    pager = TestPagination()

    reload_api_settings(
        {
            'testrestful.default_pagination_class': 'pyramid_restful.pagination.LinkHeaderPagination',
            'testrestful.page_size': 99,
            'testrestful': 'junk'
        },
        'testrestful'
    )

    assert pager.page_size == 99
    reload_api_settings(DEFAULTS)  # reset global settings
