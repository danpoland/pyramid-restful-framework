#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from io import open
from setuptools import setup

name = 'pyramid-restful-framework'
package = 'pyramid_restful'
description = 'RESTful API framework for Pyramid.'
url = 'https://github.com/danpoland/pyramid-restful-framework'
author = 'Daniel Poland'
author_email = 'danpoland84@gmail.com'
install_requires = [
    'six',
    'pyramid',
    'sqlalchemy',
    'marshmallow>=2.14,<3.0',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest'
]

here = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()
except IOError:
    README = ''


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """

    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a package themselves.
    """

    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []

    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])

    return {package: filepaths}


version = get_version(package)

if sys.argv[-1] == 'publish':
    if os.system("pip freeze | grep wheel"):
        print("wheel not installed.\nUse `pip install wheel`.\nExiting.")
        sys.exit()

    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a {0} -m 'version {0}'".format(version))
    print("  git push --tags")
    sys.exit()

setup(
    name=name,
    version=version,
    url=url,
    license='BSD',
    description=description,
    long_description=README,
    author=author,
    author_email=author_email,
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
