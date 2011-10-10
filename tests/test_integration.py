from __future__ import with_statement
from nose.tools import assert_raises

from flask import Flask
from flaskext.assets import Environment, Bundle
from webassets.bundle import get_all_bundle_files
from helpers import TempEnvironmentHelper, Module, Blueprint


class TestUrlAndDirectory(object):
    """By default, the 'url' and 'directory' settings of webassets are
    not used in Flask-Assets; that is, the values are automatically
    handled based on the configuration of the Flask app and the modules
    used.

    The user can disable the automatic handling by setting these values
    if he needs to for some reason.

    Let's test the different scenarios to ensure everything works.
    """

    def setup(self):
        self.app = Flask(__name__, static_path='/app_static')
        import test_module
        if not Blueprint:
            self.module = Module(test_module.__name__, name='module',
                                 static_path='/mod_static')
            self.app.register_module(self.module)
        else:
            self.blueprint = Blueprint('module', test_module.__name__,
                                       static_url_path='/mod_static',
                                       static_folder='static')
            self.app.register_blueprint(self.blueprint)
        self.env = Environment(self.app)

    def test_config_values_not_set_by_default(self):
        assert not 'directory' in self.env.config
        assert not 'url' in self.env.config
        assert_raises(KeyError, self.env.config.__getitem__, 'directory')
        assert_raises(KeyError, self.env.config.__getitem__, 'url')

    def test_directory_auto(self):
        """Test how we handle file references if no root 'directory' is
        configured manually.
        """
        assert not 'directory' in self.env.config
        root = self.app.root_path
        assert get_all_bundle_files(Bundle('foo'), self.env) == [root + '/static/foo']
        # Modules prefixes in paths are handled specifically.
        assert get_all_bundle_files(Bundle('module/bar'), self.env) == [root + '/test_module/static/bar']
        # Prefixes that aren't valid module names are just considered
        # subfolders of the main app.
        assert get_all_bundle_files(Bundle('nomodule/bar'), self.env) == [root + '/static/nomodule/bar']
        # In case the name of a app-level subfolder conflicts with a
        # module name, you can always use this hack:
        assert get_all_bundle_files(Bundle('./module/bar'), self.env) == [root + '/static/module/bar']

        # Custom static folder
        self.app.static_folder = '/'
        assert get_all_bundle_files(Bundle('foo'), self.env) == ['/foo']

    def test_directory_custom(self):
        """A custom root directory is configured."""
        self.env.directory = '/tmp'
        assert get_all_bundle_files(Bundle('foo'), self.env) == ['/tmp/foo']
        # We do not recognize references to modules.
        assert get_all_bundle_files(Bundle('module/bar'), self.env) == ['/tmp/module/bar']

    def test_url_auto(self):
        """Test how urls are generated if no 'url' is configured manually.
        """
        assert not 'url' in self.env.config

        assert Bundle('foo').urls(self.env) == ['/app_static/foo']
        # Urls for files that point to a module use that module's url prefix.
        assert Bundle('module/bar').urls(self.env) == ['/mod_static/bar']
        # Try with a prefix that's not actually a valid module
        assert Bundle('nomodule/bar').urls(self.env) == ['/app_static/nomodule/bar']

        # [Regression] Ensure that any request context we may have added
        # to the stack has been removed.
        from flask import _request_ctx_stack
        assert _request_ctx_stack.top is None

    def test_url_custom(self):
        """A custom root url is configured."""
        self.env.url = '/media'
        assert Bundle('foo').urls(self.env) == ['/media/foo']
        # We do not recognize references to modules.
        assert Bundle('module/bar').urls(self.env) == ['/media/module/bar']

    def test_existing_request_object_used(self):
        """[Regression] Check for a bug where the url generation code of
        Flask-Assets always added a dummy test request to the context stack,
        instead of using the existing one if there is one.

        We test this by making the context define a custom SCRIPT_NAME
        prefix, and then we check if it affects the generated urls, as
        it should.
        """
        with self.app.test_request_context(
                  '/', environ_overrides={'SCRIPT_NAME': '/yourapp'}):
            assert Bundle('foo').urls(self.env) == ['/yourapp/app_static/foo']


class TestUrlAndDirectoryWithInitApp(object):
    """[Regression] Make sure the automatic "directory" and "url"
    values also work if the application is initialized via "init_app()".
    """

    def setup(self):
        self.app = Flask(__name__, static_path='/initapp_static')
        self.env = Environment()
        self.env.init_app(self.app)

    def test(self):
        """Make sure the "url" and "directory" config values are
        read from the Flask app.
        """
        with self.app.test_request_context():
            assert not 'url' in self.env.config
            assert Bundle('foo').urls(self.env) == ['/initapp_static/foo']

            assert not 'directory' in self.env.config
            root = self.app.root_path
            assert get_all_bundle_files(Bundle('foo'), self.env) == [root + '/static/foo']


class TestBuild(TempEnvironmentHelper):
    """[Regression]

    Make sure actually building a bundle works also.
    """

    default_files = {
        'foo': 'function bla  () { /* comment */ var a; }    ',
    }

    def test_build(self):
        self.mkbundle('foo', filters='rjsmin', output='out').build()
        assert self.get('out') == 'function bla(){var a;}'

    def test_with_cache_default_directory(self):
        """[Regression] The cache directory is created in the Flask
        main static folder.
        """
        self.env.cache = True
        self.mkbundle('foo', filters='rjsmin', output='out').build()
        assert self.get('out') == 'function bla(){var a;}'
