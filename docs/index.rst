Flask-Assets
============

.. currentmodule:: flask_assets

Flask-Assets helps you to integrate `webassets`_ into your `Flask`_
application.

.. _webassets: http://github.com/miracle2k/webassets
.. _Flask: http://flask.pocoo.org/


Installation
------------

Install the extension with one of the following commands::

    $ easy_install Flask-Assets

or alternatively if you have pip installed::

    $ pip install Flask-Assets


Usage
-----

You initialize the app by creating an :class:`Environment` instance, and
registering your assets with it in the form of so called *bundles*.

.. code-block:: python

    from flask import Flask
    from flask_assets import Environment, Bundle

    app = Flask(__name__)
    assets = Environment(app)

    js = Bundle('jquery.js', 'base.js', 'widgets.js',
                filters='jsmin', output='gen/packed.js')
    assets.register('js_all', js)


A bundle consists of any number of source files (it may also contain
other nested bundles), an output target, and a list of filters to apply.

All paths are relative to your app's **static** directory, or the static
directory of a :ref:`Flask blueprint <blueprints>`.

If you prefer you can of course just as well define your assets in an
external config file, and read them from there. ``webassets`` includes a
number of :ref:`helper classes <webassets:loaders>` for some popular formats
like YAML.

Like is common for a Flask extension, a Flask-Assets instance may be used
with multiple applications by initializing through ``init_app`` calls,
rather than passing a fixed application object:

.. code-block:: python

    app = Flask(__name__)
    assets = flask_assets.Environment()
    assets.init_app(app)


Using the bundles
~~~~~~~~~~~~~~~~~

Now with your assets properly defined, you want to merge and minify
them, and include a link to the compressed result in your web page:

.. code-block:: jinja

    {% assets "js_all" %}
        <script type="text/javascript" src="{{ ASSET_URL }}"></script>
    {% endassets %}


That's it, really. **Flask-Assets** will automatically merge and compress
your bundle's source files the first time the template is rendered, and will
automatically update the compressed file everytime a source file changes.
If you set ``ASSETS_DEBUG`` in your app configuration to ``True``, then
each source file will be outputted individually instead.


.. _blueprints:

Flask blueprints
~~~~~~~~~~~~~~~~

If you are using Flask blueprints, you can refer to a blueprint's static files
via a prefix, in the same way as Flask allows you to reference a blueprint's
templates:

.. code-block:: python

    js = Bundle('app_level.js', 'blueprint/blueprint_level.js')

In the example above, the bundle would reference two files,
``{APP_ROOT}/static/app_level.js``, and ``{BLUEPRINT_ROOT}/static/blueprint_level.js``.

If you have used the ``webassets`` library standalone before, you may be
familiar with the requirement to set the ``directory`` and ``url``
configuration values. You will note that this is not required here, as
Flask's static folder support is used instead. However, note that you *can*
set a custom root directory or url if you prefer, for some reason. However,
in this case the blueprint support of Flask-Assets is disabled, that is,
referencing static files in different blueprints using a prefix, as described
above, is no longer possible. All paths will be considered relative to the
directory and url you specified.

Pre 0.7 modules are also supported; they work exactly the same way.


Templates only
~~~~~~~~~~~~~~

If you prefer, you can also do without defining your bundles in code, and
simply define everything inside your template:

.. code-block:: jinja

    {% assets filters="jsmin", output="gen/packed.js",
              "common/jquery.js", "site/base.js", "site/widgets.js" %}
        <script type="text/javascript" src="{{ ASSET_URL }}"></script>
    {% endassets %}


.. _configuration:

Configuration
-------------

``webassets`` supports a couple of configuration options. Those can be
set both through the :class:`Environment` instance, as well as the Flask
configuration. The following two statements are equivalent:

.. code-block:: python

    assets_env.debug = True
    app.config['ASSETS_DEBUG'] = True


For a list of available settings, see the full
:ref:`webassets documentation <webassets:environment-configuration>`.

Babel Configuration
~~~~~~~~~~~~~~~~~~~

If you use `Babel`_ for internationalization, then you will need to
add the extension to your babel configuration file
as ``webassets.ext.jinja2.AssetsExtension``

Otherwise, babel will not extract strings from any templates that
include an ``assets`` tag.

Here is an example ``babel.cfg``:

.. code-block:: python

    [python: **.py]
    [jinja2: **.html]
    extensions=jinja2.ext.autoescape,jinja2.ext.with_,webassets.ext.jinja2.AssetsExtension


.. _Babel: http://babel.edgewall.org/

Flask-S3 Configuration
~~~~~~~~~~~~~~~~~~~~~~~

`Flask-S3`_ allows you to upload and serve your static files from
an Amazon S3 bucket. It accomplishes this by overwriting the Flask
``url_for`` function. In order for Flask-Assets to use this
overwritten ``url_for`` function, you need to let it know that
you are using Flask-S3. Just set

.. code-block:: python

    app.config['FLASK_ASSETS_USE_S3']=True

.. _Flask-S3: https://flask-s3.readthedocs.io/en/latest/

Flask-CDN Configuration
~~~~~~~~~~~~~~~~~~~~~~~

`Flask-CDN`_ allows you to upload and serve your static files from
a CDN (like `Amazon Cloudfront`_), without having to modify
your templates. It accomplishes this by overwriting the Flask
``url_for`` function. In order for Flask-Assets to use this
overwritten ``url_for`` function, you need to let it know that
you are using Flask-CDN. Just set

.. code-block:: python

    app.config['FLASK_ASSETS_USE_CDN']=True

.. _Flask-CDN: https://flask-cdn.readthedocs.io/en/latest/
.. _Amazon Cloudfront: https://aws.amazon.com/cloudfront/


Command Line Interface
----------------------

*New in version 0.12.*

Flask 0.11+ comes with build-in integration of `CLI`_ using `click`_
library. The ``assets`` command is automatically installed through
*setuptools* using ``flask.commands`` entry point group in **setup.py**.

.. code-block:: python

   entry_points={
       'flask.commands': [
           'assets = flask_assets:assets',
       ],
   },

After installing Flask 0.11+ you should see following line in the output
when executing ``flask`` command in your shell:

.. code-block:: console

   $ flask --help
   ...
   Commands:
     assets   Web assets commands.
   ...


.. _CLI: https://flask.pocoo.org/docs/0.11/cli/
.. _click: https://click.pocoo.org/docs/latest/


Legacy support
~~~~~~~~~~~~~~

If you have `Flask-Script`_ installed, then a command will be available
as ``flask_assets.ManageAssets``:

.. code-block:: python

    from flask_assets import ManageAssets
    manager = Manager(app)
    manager.add_command("assets", ManageAssets(assets_env))

You can explicitly pass the ``assets_env`` when adding the command as above.
Alternatively, ``ManageAssets`` will import the ``current_app`` from Flask and
use the ``jinja_env``.

The command allows you to do things like rebuilding bundles from the
command line. See the list of
:ref:`available subcommands <webassets:script-commands>`.


.. _Flask-Script: http://pypi.python.org/pypi/Flask-Script


Using in Google App Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use flask-assets in Google App Engine by manually building assets.
The GAE runtime cannot create files, which is necessary for normal flask-assets
functionality, but you can deploy pre-built assets. You can use a file change
listener to rebuild assets on the fly in development.

For a fairly minimal example which includes auto-reloading in development, see
`flask-assets-gae-example`_.

Also see the `relevant webassets documentation`_.

.. _flask-assets-gae-example: https://github.com/SocosLLC/flask-assets-gae-example
.. _relevant webassets documentation: http://webassets.readthedocs.io/en/latest/faq.html#is-google-app-engine-supported


API
---

.. automodule:: flask_assets
   :members:

Webassets documentation
-----------------------

For further information, have a look at the complete
:ref:`webassets documentation <index>`, and in particular, the
following topics:

- :ref:`Configuration <webassets:environment-configuration>`
- :ref:`All about bundles <webassets:bundles>`
- :ref:`Builtin filters <webassets:builtin-filters>`
- :ref:`Custom filters <webassets:custom-filters>`
- :ref:`CSS compilers <webassets:css-compilers>`
- :ref:`FAQ <webassets:faq>`
