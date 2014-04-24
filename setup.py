#!/usr/bin/env python
# coding: utf8
"""
Flask-Assets
-------------

Integrates the ``webassets`` library with Flask, adding support for
merging, minifying and compiling CSS and Javascript files.
"""

from __future__ import with_statement
from setuptools import setup

setup(
    name='Flask-Assets',
    version='0.10.dev',
    url='http://github.com/miracle2k/flask-assets',
    license='BSD',
    author='Michael Elsdoerfer',
    author_email='michael@elsdoerfer.com',
    description='Asset management for Flask, to compress and merge ' \
        'CSS and Javascript files.',
    long_description=__doc__,
    py_modules=['flask_assets'],
    package_dir={'': 'src'},
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.8',
        'webassets>=0.10.dev'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'flask-script'
    ],
)
