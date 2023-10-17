from __future__ import absolute_import

import pytest
from flask import Flask
from flask_assets import Environment, Bundle
from webassets.bundle import get_all_bundle_files

from tests.helpers import TempEnvironmentHelper, Module, Blueprint


def test_import():
    # We want to expose these via the assets extension module.
    from flask_assets import Bundle
    from flask_assets import Environment


class TestUrlAndDirectory(TempEnvironmentHelper):
    """By default, the 'url' and 'directory' settings of webassets are
    not used in Flask-Assets; that is, the values are automatically
    handled based on the configuration of the Flask app and the modules
    used.

    The user can disable the automatic handling by setting these values
    if he needs to for some reason.

    Let's test the different scenarios to ensure everything works.
    """

    def setup(self):
        TempEnvironmentHelper.setup(self)

        self.app = Flask(__name__, static_url_path='/app_static')
        from tests import test_module
        if not Blueprint:
            self.module = Module(test_module.__name__, name='module',
                                 static_url_path='/mod_static')
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
        with pytest.raises(KeyError):
            self.env.config['directory']
        with pytest.raises(KeyError):
            self.env.config['url']

    def test_directory_auto(self):
        """Test how we resolve file references through the Flask static
        system by default (if no custom 'env.directory' etc. values
        have been configured manually).
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
        self.app.static_folder = '/test'
        assert get_all_bundle_files(Bundle('foo'), self.env) == ['/test/foo']

    def test_url_auto(self):
        """Test how urls are generated via the Flask static system
        by default (if no custom 'env.url' etc. values have been
        configured manually).
        """
        assert not 'url' in self.env.config

        assert Bundle('foo', env=self.env).urls() == ['/app_static/foo']
        # Urls for files that point to a module use that module's url prefix.
        assert Bundle('module/bar', env=self.env).urls() == ['/mod_static/bar']
        # Try with a prefix that's not actually a valid module
        assert Bundle('nomodule/bar', env=self.env).urls() == ['/app_static/nomodule/bar']

        # [Regression] Ensure that any request context we may have added
        # to the stack has been removed.
        from flask import has_request_context
        assert not has_request_context()

    def test_custom_load_path(self):
        """A custom load_path is configured - this will affect how
        we deal with source files.
        """
        self.env.append_path(self.tempdir, '/custom/')
        self.create_files(['foo', 'module/bar'])
        assert get_all_bundle_files(Bundle('foo'), self.env) == [self.path('foo')]
        # We do not recognize references to modules.
        assert get_all_bundle_files(Bundle('module/bar'), self.env) == [self.path('module/bar')]


        assert Bundle('foo', env=self.env).urls() == ['/custom/foo']
        assert Bundle('module/bar', env=self.env).urls() == ['/custom/module/bar']

        # [Regression] With a load path configured, generating output
        # urls still works, and it still uses the flask system.
        self.env.debug = False
        self.env.url_expire = False
        assert Bundle('foo', output='out', env=self.env).urls() == ['/app_static/out']

    def test_custom_directory_and_url(self):
        """Custom directory/url are configured - this will affect how
        we deal with output files."""
        # Create source source file, make it findable (by default,
        # static_folder) is set to a fixed subfolder of the test dir (why?)
        self.create_files({'a': ''})
        self.app.static_folder = self.tempdir
        # Setup custom directory/url pair for output
        self.env.directory = self.tempdir
        self.env.url = '/custom'
        self.env.debug = False   # Return build urls
        self.env.url_expire = False  # No query strings

        assert Bundle('a', output='foo', env=self.env).urls() == ['/custom/foo']
        # We do not recognize references to modules.
        assert Bundle('a', output='module/bar', env=self.env).urls() == ['/custom/module/bar']

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
            assert Bundle('foo', env=self.env).urls() == ['/yourapp/app_static/foo']

    def test_glob(self):
        """Make sure url generation works with globs."""
        self.app.static_folder = self.tempdir
        self.create_files({'a.js': 'foo', 'b.js': 'bar'})
        assert list(sorted(self.mkbundle('*.js', env=self.env).urls())) == [
            '/app_static/a.js', '/app_static/b.js']


class TestUrlAndDirectoryWithInitApp(object):
    """[Regression] Make sure the automatic "directory" and "url"
    values also work if the application is initialized via "init_app()".
    """

    def setup(self):
        self.app = Flask(__name__, static_url_path='/initapp_static')
        self.env = Environment()
        self.env.init_app(self.app)

    def test(self):
        """Make sure the "url" and "directory" config values are
        read from the Flask app.
        """
        with self.app.test_request_context():
            assert not 'url' in self.env.config
            assert Bundle('foo', env=self.env).urls() == ['/initapp_static/foo']

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


class TestBlueprints(TempEnvironmentHelper):

    default_files = {
        'foo': 'function bla  () { /* comment */ var a; }    ',
    }

    def make_blueprint(self, name='module', import_name=None, **kw):
        if not import_name:
            from tests import test_module
            import_name = test_module.__name__

        if not Blueprint:
            self.module = Module(import_name, name=name)
            self.app.register_module(self.module)
        else:
            self.blueprint = Blueprint(name, import_name, **kw)
            self.app.register_blueprint(self.blueprint)

    def test_blueprint_output(self):
        """[Regression] Output can point to a blueprint's static
        directory.
        """
        module_static_dir = self.create_directories('module-static')[0]
        self.make_blueprint('module', static_folder=module_static_dir)
        self.mkbundle('foo', filters='rjsmin', output='module/out').build()
        assert self.get('module-static/out') == 'function bla(){var a;}'

    def test_blueprint_urls(self):
        """Urls to blueprint files are generated correctly."""
        self.make_blueprint('module', static_folder='static',
                            static_url_path='/rasputin')

        # source urls
        assert self.mkbundle('module/foo').urls() == ['/rasputin/foo']

        # output urls - env settings are to not touch filesystem
        self.env.auto_build = False
        self.env.url_expire = False
        assert self.mkbundle(output='module/out', debug=False).urls() == ['/rasputin/out']

    def test_blueprint_no_static_folder(self):
        """Test dealing with a blueprint without a static folder."""
        self.make_blueprint('module')
        with pytest.raises(TypeError):
            self.mkbundle('module/foo').urls()

    def test_cssrewrite(self):
        """Make sure cssrewrite works with Blueprints.
        """

        module_static_dir = self.create_directories('modfolder')[0]
        self.make_blueprint('modname', static_folder=module_static_dir,
                            static_url_path='/w/u/f/f')
        self.create_files(
                {'modfolder/css': 'h1{background: url("local")}'})

        # Source file is in a Blueprint, output file is app-level.
        self.mkbundle('modname/css', filters='cssrewrite', output='out').build()

        # The urls are NOT rewritten using the filesystem (/modfolder), but
        # within the url space.
        assert self.get('out') == 'h1{background: url("../w/u/f/f/local")}'
