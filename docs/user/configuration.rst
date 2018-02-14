Configuration
=============

Currently there are three settings you can use to configure default behavior in PRF.

- **default_pagination_class**: A string representing the path to the default pagination class to use.
- **page_size**: An integer used as the default page size for pagination.
- **default_permission_classes**: A list or tuple of strings. Each string represents the path to a permissions class to use by default with each view.

If you used .. _pyramid-cookiecutter-restful: https://github.com/danpoland/pyramid-cookiecutter-restful to create
your project you can simply update these values in the ``settings.__init__.py`` file in the ``PYRAMID_APP_SETTINGS``
variable::

    PYRAMID_APP_SETTINGS = {
        'pyramid.reload_templates': PYRAMID_RELOAD_TEMPLATES,
        'pyramid.debug_authorization': PYRAMID_DEBUG_AUTHORIZATION,
        'pyramid.debug_notfound': PYRAMID_DEBUG_NOTFOUND,
        'pyramid.debug_routematch': PYRAMID_DEBUG_ROUTEMATCH,
        'pyramid.default_locale_name': 'en',
        # pyramid_restful settings
        'restful.page_size': 50,
        'restful.default_pagination_class': 'pyramid_restful_jsonapi.pagination.JSONAPIPagination',
        'restful.default_permission_classes': ['exampleapp.permissions.AuthenticatedAndActivePermission'],
    }

If you are adding PRF to an existing project or your prefer using ini files for configuration you can set the values
for these configurations by adding a new ``restful`` section to you ini file::

    [restful]
    restful.page_size = 50
    restful.default_pagination_class = 'pyramid_restful_jsonapi.pagination.JSONAPIPagination'
    restful.default_permission_classes = 'exampleapp.permissions.AuthenticatedAndActivePermission'

