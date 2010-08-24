#!/usr/bin/env python
# coding: utf8
"""
Flask-Assets
-------------

Integrates the ``webassets`` library with Flask, adding support for
merging, minifying and compiling CSS and Javascript files.
"""

from setuptools import setup, find_packages

# Figure out the version; this could be done by importing the
# module, though that requires dependencies to be already installed,
# which may not be the case when processing a pip requirements
# file, for example.a
import os, re
here = os.path.dirname(os.path.abspath(__file__))
version_re = re.compile(
    r'__version__ = (\(.*?\))')
fp = open(os.path.join(here, 'src/flaskext', 'assets.py'))
version = None
for line in fp:
    match = version_re.search(line)
    if match:
        version = eval(match.group(1))
        break
else:
    raise Exception("cannot find version")
fp.close()


setup(
    name='Flask-Assets',
    version=".".join(map(str, version)),
    url='http://github.com/miracle2k/flask-assets',
    license='BSD',
    author='Michael Elsdoerfer',
    author_email='michael@elsdoerfer.com',
    description='Asset management for Flask, to compress and merge ' \
        'CSS and Javascript files.',
    long_description=__doc__,
    packages=find_packages('src'),
    package_dir={'': 'src'},
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