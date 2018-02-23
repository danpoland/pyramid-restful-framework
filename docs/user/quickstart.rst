Quick Start
===========

The quickest way to get started with pyramid-restful-framework is to use
`pyramid-cookiecutter-restful <https://github.com/danpoland/pyramid-cookiecutter-restful>`_. The cookiecutter
will scaffold a project that includes Pyramid, SQLAlchemy and pyramid-restful-framework. The project uses Django like settings
instead of .ini files for configuration. It includes a wsgi.py file for running the app.

If you like ini files or want to include pyramid-restful-framework in an existing project you can install the library
via pip.

``$ pip install pyramid-restful-framework``

Be sure to add **pyramid_restful** to the **pyramid.includes** directive in your configuration file(s).

``pyramid.includes = pyramid_restful``

Alternatively you can use `pyramid.config.Configurator.include` in your app setup:

``config.include('pyramid_restful')``
