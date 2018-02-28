[![pypi-version]][pypi]
[![build-status-image]][travis]
[![Coverage Status](https://coveralls.io/repos/github/danpoland/pyramid-restful-framework/badge.svg?branch=master)](https://coveralls.io/github/danpoland/pyramid-restful-framework?branch=master)

# pyramid-restful-framework
A RESTful API framework for Pyramid heavily influenced by [django-rest-framework](https://github.com/encode/django-rest-framework).

The goal of this project is to provide DRF’s view patterns on a lighter weight web framework that grants you more fine 
grained and explicit control over database queries and object serialization/deserialization. This is accomplished using [SQLAlchemy](http://www.sqlalchemy.org/) as an ORM and [marshmallow](https://github.com/marshmallow-code/marshmallow/) Schemas for object serialization and deserialization.

[Read the docs]( http://pyramid-restful-framework.readthedocs.io/en/latest/) to learn more. 

[build-status-image]: https://travis-ci.org/danpoland/pyramid-restful-framework.svg?branch=master
[travis]: https://travis-ci.org/danpoland/pyramid-restful-framework
[pypi-version]: https://badge.fury.io/py/pyramid-restful-framework.svg
[pypi]: https://pypi.python.org/pypi/pyramid-restful-framework