#!/usr/bin/env python
# coding: utf8
"""
Flask-Assets
-------------

Integrates the ``webassets`` library with Flask, adding support for
merging, minifying and compiling CSS and Javascript files.
"""

from setuptools import setup, find_packages


setup(
    name='Flask-Assets',
    version='1.0',
    url='github.com/miracle2k/flask-assets',
    license='BSD',
    author='Michael Elsdörfer',
    author_email='michael@elsdoerfer.com',
    description='Asset management for Flask, to compress and merge ' \
        'CSS and Javascript files.',
    long_description=__doc__,
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'webassets',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
    ],
)