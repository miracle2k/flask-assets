from __future__ import with_statement
from os import path
from flask import _request_ctx_stack, url_for
from webassets.env import BaseEnvironment, ConfigStorage, env_options
from webassets.loaders import PythonLoader, YAMLLoader


__version__ = (0, 8, 'dev')
__webassets_version__ = ('dev',) # webassets core compatibility. used in setup.py


__all__ = ('Environment', 'Bundle',)


# We want to expose this here.
from webassets import Bundle


class FlaskConfigStorage(ConfigStorage):
    """Uses the config object of a Flask app as the backend: either the app
    instance bound to the extension directly, or the current Flasp app on
    the stack.

    Also provides per-application defaults for some values.

    Note that if no app is available, this config object is basically
    unusable - this is by design; this could also let the user set defaults
    by writing to a container not related to any app, which would be used
    as a fallback if a current app does not include a key. However, at least
    for now, I specifically made the choice to keep things simple and not
    allow global across-app defaults.
    """

    def __init__(self, *a, **kw):
        self._defaults = {}
        ConfigStorage.__init__(self, *a, **kw)

    def _transform_key(self, key):
        if key.lower() in env_options:
            return "ASSETS_%s" % key.upper()
        else:
            return key.upper()

    def setdefault(self, key, value):
        """We may not always be connected to an app, but we still need
        to provide a way to the base environment to set it's defaults.
        """
        try:
            super(FlaskConfigStorage, self).setdefault(key, value)
        except RuntimeError:
            self._defaults.__setitem__(key, value)

    def __contains__(self, key):
        return self._transform_key(key) in self.env._app.config

    def __getitem__(self, key):
        value = self._get_deprecated(key)
        if value:
            return value

        # First try the current app's config
        public_key = self._transform_key(key)
        if self.env._app:
            if public_key in self.env._app.config:
                return self.env._app.config[public_key]

        # Try a non-app specific default value
        if key in self._defaults:
            return self._defaults.__getitem__(key)

        # Finally try to use a default based on the current app
        deffunc = getattr(self, "_app_default_%s" % key, False)
        if deffunc:
            return deffunc()

        # We've run out of options
        raise KeyError()

    def __setitem__(self, key, value):
        if not self._set_deprecated(key, value):
            self.env._app.config[self._transform_key(key)] = value

    def __delitem__(self, key):
        del self.env._app.config[self._transform_key(key)]


def get_static_folder(app_or_blueprint):
    """Return the static folder of the given Flask app
    instance, or module/blueprint.

    In newer Flask versions this can be customized, in older
    ones (<=0.6) the folder is fixed.
    """
    if hasattr(app_or_blueprint, 'static_folder'):
        return app_or_blueprint.static_folder
    return path.join(app_or_blueprint.root_path, 'static')


class Environment(BaseEnvironment):

    config_storage_class = FlaskConfigStorage

    def __init__(self, app=None):
        self.app = app
        super(Environment, self).__init__()
        if app:
            self.init_app(app)

    @property
    def _app(self):
        """The application object to work with; this is either the app
        that we have been bound to, or the current application.
        """
        if self.app is not None:
            return self.app
        else:
            ctx = _request_ctx_stack.top
            if ctx is not None:
                return ctx.app
        raise RuntimeError('assets instance not bound to an application, '+
                            'and no application in current context')

    def absurl(self, fragment):
        if self.config.get('url') is not None:
            # If a manual base url is configured, skip any
            # blueprint-based auto-generation.
            return super(Environment, self).absurl(fragment)
        else:
            try:
                filename, query = fragment.split('?', 1)
                query = '?' + query
            except (ValueError):
                filename = fragment
                query = ''

            if hasattr(self._app, 'blueprints'):
                try:
                    blueprint, name = filename.split('/', 1)
                    self._app.blueprints[blueprint] # generates keyerror if no module
                    endpoint = '%s.static' % blueprint
                    filename = name
                except (ValueError, KeyError):
                    endpoint = 'static'
            else:
                # Module support for Flask < 0.7
                try:
                    module, name = filename.split('/', 1)
                    self._app.modules[module] # generates keyerror if no module
                    endpoint = '%s.static' % module
                    filename = name
                except (ValueError, KeyError):
                    endpoint = '.static'

            ctx = None
            if not _request_ctx_stack.top:
                ctx = self._app.test_request_context()
                ctx.push()
            try:
                return url_for(endpoint, filename=filename) + query
            finally:
                if ctx:
                    ctx.pop()

    def abspath(self, path):
        """Still needed to resolve the output path.
        XXX: webassets needs to call _normalize_source_path
        for this!
        """
        return self._normalize_source_path(path)

    # XXX: This is required because in a couple of places, webassets 0.6
    # still access env.directory, at one point even directly. We need to
    # fix this for 0.6 compatibility, but it might be preferrable to
    # introduce another API similar to _normalize_source_path() for things
    # like the cache directory and output files.
    def set_directory(self, directory):
        self.config['directory'] = directory
    def get_directory(self):
        if self.config.get('directory') is not None:
            return self.config['directory']
        return get_static_folder(self._app)
    directory = property(get_directory, set_directory, doc=
    """The base directory to which all paths will be relative to.
    """)

    def _normalize_source_path(self, filename):
        if path.isabs(filename):
            return filename
        if self.config.get('directory') is not None:
            return super(Environment, self).abspath(filename)
        try:
            if hasattr(self._app, 'blueprints'):
                blueprint, name = filename.split('/', 1)
                directory = get_static_folder(self._app.blueprints[blueprint])
                filename = name
            else:
                # Module support for Flask < 0.7
                module, name = filename.split('/', 1)
                directory = get_static_folder(self._app.modules[module])
                filename = name
        except (ValueError, KeyError):
            directory = get_static_folder(self._app)
        return path.abspath(path.join(directory, filename))

    def init_app(self, app):
        app.jinja_env.add_extension('webassets.ext.jinja2.AssetsExtension')
        app.jinja_env.assets_environment = self

    def from_yaml(self, path):
        """Register bundles from a YAML configuration file"""
        bundles = YAMLLoader(path).load_bundles()
        [self.register(name, bundle) for name, bundle in bundles.iteritems()]

    def from_python(self, path):
        """Register bundles from a Python module"""
        bundles = PythonLoader(path).load_bundles()
        [self.register(name, bundle) for name, bundle in bundles.iteritems()]

try:
    from flaskext import script
except ImportError:
    pass
else:
    import argparse
    from webassets.script import GenericArgparseImplementation, CommandError

    class CatchAllParser(object):
        def parse_known_args(self, app_args):
            return argparse.Namespace(), app_args

    class FlaskArgparseInterface(GenericArgparseImplementation):
        """Subclass the CLI implementation to add a --parse-templates option."""

        def _construct_parser(self, *a, **kw):
            super(FlaskArgparseInterface, self).\
                _construct_parser(*a, **kw)
            self.parser.add_argument(
                '--parse-templates', action='store_true',
                help='search project templates to find bundles')

        def _setup_assets_env(self, ns, log):
            env = super(FlaskArgparseInterface, self)._setup_assets_env(ns, log)
            if env is not None:
                if ns.parse_templates:
                    log.info('Searching templates...')
                    # Note that we exclude container bundles. By their very nature,
                    # they are guaranteed to have been created by solely referencing
                    # other bundles which are already registered.
                    env.add(*[b for b in self.load_from_templates(env)
                                    if not b.is_container])

                if not len(env):
                    raise CommandError(
                        'No asset bundles were found. '
                        'If you are defining assets directly within '
                        'your templates, you want to use the '
                        '--parse-templates option.')
            return env

        def load_from_templates(self, env):
            from webassets.ext.jinja2 import Jinja2Loader, AssetsExtension
            from flask import current_app as app

            # Use the application's Jinja environment to parse
            jinja2_env = app.jinja_env

            # Get the template directories of app and blueprints
            template_dirs = [path.join(app.root_path, app.template_folder)]
            for blueprint in app.blueprints:
                template_dirs.append(
                    path.join(blueprint.root_path, blueprint.template_folder))

            return Jinja2Loader(env, template_dirs, [jinja2_env]).load_bundles()

    class ManageAssets(script.Command):
        """Manage assets."""
        capture_all_args = True

        def __init__(self, assets_env=None, impl=FlaskArgparseInterface,
                     log=None):
            self.env = assets_env
            self.implementation = impl
            self.log = log

        def create_parser(self, prog):
            return CatchAllParser()

        def run(self, args):
            """Runs the management script.
            If ``self.env`` is not defined, it will import it from
            ``current_app``.
            """

            if not self.env:
                from flask import current_app
                self.env = current_app.jinja_env.assets_environment

            # Determine 'prog' - something like for example
            # "./manage.py assets", to be shown in the help string.
            # While we don't know the command name we are registered with
            # in Flask-Assets, we are lucky to be able to rely on the
            # name being in argv[1].
            import sys, os.path
            prog = '%s %s' % (os.path.basename(sys.argv[0]), sys.argv[1])

            impl = self.implementation(self.env, prog=prog, log=self.log)
            impl.main(args)

    __all__ = __all__ + ('ManageAssets',)
