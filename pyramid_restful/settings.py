import six

from importlib import import_module

from pyramid.events import subscriber, ApplicationCreated

DEFAULTS = {
    # Generic view behavior
    'default_pagination_class': 'pyramid_restful.pagination.PageNumberPagination',
    # Pagination
    'page_size': None,
    # Permissions
    'default_permission_classes': []
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'default_pagination_class',
    'default_permission_classes'
)


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """

    if val is None:
        return None
    elif isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]

    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """

    try:
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        msg = "Could not import '%s' for API setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class APISettings:
    """
    A settings object, that allows API settings to accessed as properties
    """

    def __init__(self, app_settings=None, defaults=None, import_strings=None):
        if app_settings:
            self._app_settings = app_settings

        self.defaults = defaults or DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS

    @property
    def app_settings(self):
        if not hasattr(self, '_app_settings'):
            self._app_settings = {}
        return self._app_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError('Invalid API setting: `{}`'.format(attr))

        try:
            val = self.app_settings[attr]
        except KeyError:
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        setattr(self, attr, val)

        return val


api_settings = APISettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(settings, prefix='restful'):
    global api_settings
    app_settings = {}

    for key, val in settings.items():
        try:
            keyfix, setting_name = key.split('.')
        except ValueError:
            continue

        if keyfix == prefix:
            app_settings[setting_name] = val

    api_settings = APISettings(app_settings, DEFAULTS, IMPORT_STRINGS)


@subscriber(ApplicationCreated)
def application_created(app):
    """
    When a pyramid application is created re-create api_settings use the
    """
    reload_api_settings(app.settings)
