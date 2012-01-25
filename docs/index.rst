Flask-Assets
============

.. module:: flask_assets

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
    from flask.ext.assets import Environment, Bundle

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

Like is common for a Flask extension, a Flask-Asssets instance may be used
with multiple applications by initializing through ``init_app`` calls,
rather than passing a fixed application object:

.. code-block:: python

    app = Flask(__name__)
    assets = flask.ext.assets.Environment()
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

    {% assets filter="jsmin", output="gen/packed.js",
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


Management Command
------------------

If you have `Flask-Script`_ installed, then a command will be available
as ``flaskext.assets.ManageAssets``:

.. code-block:: python

    from flaskext.assets import ManageAssets
    manager = Manager(app)
    manager.add_command("assets", ManageAssets(assets_env))

You can explicitly pass the ``assets_env`` when adding the comm`and as above.
Alternatively, ``ManageAssets`` will import the ``current_app` from Flask and
use the ``jinja_env``.

The command allows you to do things like rebuilding bundles from the
command line. See the list of
:ref:`available subcommands <webassets:script-commands>`.


.. _Flask-Script: http://pypi.python.org/pypi/Flask-Script


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
