from .settings import reload_api_settings

__version__ = '0.7.2'

VERSION = __version__


def includeme(config):
    reload_api_settings(config.registry.settings)
