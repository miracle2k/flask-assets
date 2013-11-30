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

# Figure out the version; this could be done by importing the
# module, though that requires dependencies to be already installed,
# which may not be the case when processing a pip requirements
# file, for example.
def parse_version(asignee):
    import os, re
    here = os.path.dirname(os.path.abspath(__file__))
    version_re = re.compile(
        r'%s = (\(.*?\))' % asignee)
    with open(os.path.join(here, 'src', 'flask_assets.py')) as fp:
        for line in fp:
            match = version_re.search(line)
            if match:
                version = eval(match.group(1))
                return ".".join(map(str, version))
        else:
            raise Exception("cannot find version")
version = parse_version('__version__')
webassets_version = parse_version('__webassets_version__')


setup(
    name='Flask-Assets',
    version=version,
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
        'webassets==%s' % webassets_version,
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
        'flask-script'
    ],
)
