"""The Environment configuration is hooked up to the Flask config dict.
"""

from nose.tools import assert_raises
from flask import Flask, Module
from flaskext.assets import Environment, Bundle


class TestConfigAppBound:
    """The extension is bound to a specific app.
    """

    def setup(self):
        self.app = Flask(__name__)
        self.env = Environment(self.app)

    def test_set_environment(self):
        """Setting a config value on the environment works.
        """
        self.env.updater = 'foo'
        assert self.app.config['ASSETS_UPDATER'] == 'foo'

    def test_set_config(self):
        """Setting a value in the Flask config works.
        """
        self.app.config['ASSETS_UPDATER'] = 'foo'
        assert self.env.updater == 'foo'

    def test_custom_values(self):
        """Custom config values are relayed to the Flask config as.is.
        """
        self.app.config['LESS_PATH'] = '/usr/bin/less'
        assert self.env.config['LESS_PATH'] == '/usr/bin/less'

    def test_no_override(self):
        """Ensure that the webassets defaults do not override existing
        Flask config values.
        """
        app = Flask(__name__)
        app.config['ASSETS_UPDATER'] = 'MOO'
        env = Environment(app)
        assert env.updater == 'MOO'
        assert app.config['ASSETS_UPDATER'] == 'MOO'

         # Neither do the defaults that flask-assets set.
        app = Flask(__name__)
        app.config['ASSETS_URL'] = 'MOO'
        env = Environment(app)
        assert env.url == 'MOO'
        assert app.config['ASSETS_URL'] == 'MOO'


class TestConfigNoAppBound:
    """The application is not bound to a specific app.
    """

    def setup(self):
        self.env = Environment()

    def test_no_app_available(self):
        """Without an application bound, we can't do much."""
        assert_raises(RuntimeError, setattr, self.env, 'debug', True)
        assert_raises(RuntimeError, self.env.config.get, 'debug')

    def test_global_defaults(self):
        """We may set defaults even without an application, however."""
        self.env.config.setdefault('FOO', 'BAR')
        with Flask(__name__).test_request_context():
            assert self.env.config['FOO'] == 'BAR'

    def test_multiple_separate_apps(self):
        """Each app has it's own separate configuration.
        """
        app1 = Flask(__name__)
        self.env.init_app(app1)

        # With no app yet available...
        assert_raises(RuntimeError, getattr, self.env, 'url')
        # ...set a default
        self.env.config.setdefault('FOO', 'BAR')

        # When an app is available, the default is used
        with app1.test_request_context():
            assert self.env.config['FOO'] == 'BAR'

            # If the default is overridden for this application, it
            # is still valid for other apps.
            self.env.config['FOO'] = '42'
            assert self.env.config['FOO'] == '42'
            app2 = Flask(__name__)
            with app2.test_request_context():
                assert self.env.config['FOO'] == 'BAR'

    def test_key_error(self):
        """KeyError is raised if a config value doesn't exist.
        """
        with Flask(__name__).test_request_context():
            assert_raises(KeyError, self.env.config.__getitem__, 'YADDAYADDA')
            # The get() helper, on the other hand, simply returns None
            assert self.env.config.get('YADDAYADDA') == None


class TestUrlAndDirectory(object):
    """By default, the 'url' and 'directory' settings of webassets are
    not used in Flask-Assets; that is, the values are automatically
    handled based on the configuration of the Flask app and the modules
    used.

    The user can disable the automatic handling by setting these values
    if he needs to for some reason.

    Let's test the different scenarios to ensure everything works.
    """

#    root path without module usage
#       should already be tested?
#    root path with module usage
#       needs to test whether we find the files
#       test reference to non-existant module##
#
#    url without module usage
#       should already be tested
#    url with module usage
#       references the correct files
#       try with incorrect module reference

#    add documentation

    def setup(self):
        self.app = Flask(__name__, static_path='/app_static')
        import test_module
        self.module = Module(test_module.__name__, name='module',
                             static_path='/mod_static')
        self.app.register_module(self.module)
        self.env = Environment(self.app)

    def config_values_not_set_by_default(self):
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
        assert Bundle('foo').get_files(self.env) == [root + '/static/foo']
        # Modules prefixes in paths are handled specifically.
        assert Bundle('module/bar').get_files(self.env) == [root + '/test_module/static/bar']
        # Prefixes that aren't valid module names are just considered
        # subfolders of the main app.
        assert Bundle('nomodule/bar').get_files(self.env) == [root + '/static/nomodule/bar']
        # In case the name of a app-level subfolder conflicts with a
        # module name, you can always use this hack:
        assert Bundle('./module/bar').get_files(self.env) == [root + '/static/module/bar']

    def test_directory_custom(self):
        """A custom root directory is configured."""
        self.env.directory = '/tmp'
        assert Bundle('foo').get_files(self.env) == ['/tmp/foo']
        # We do not recognize references to modules.
        assert Bundle('module/bar').get_files(self.env) == ['/tmp/module/bar']

    def test_url_auto(self):
        """Test how urls are generated if no 'url' is configured manually.
        """
        assert not 'url' in self.env.config

        assert Bundle('foo').urls(self.env) == ['/app_static/foo']
        # Urls for files that point to a module use that module's url prefix.
        assert Bundle('module/bar').urls(self.env) == ['/mod_static/bar']
        # Try with a prefix that's not actually a valid module
        assert Bundle('nomodule/bar').urls(self.env) == ['/app_static/nomodule/bar']

    def test_url_custom(self):
        """A custom root url is configured."""
        self.env.url = '/media'
        assert Bundle('foo').urls(self.env) == ['/media/foo']
        # We do not recognize references to modules.
        assert Bundle('module/bar').urls(self.env) == ['/media/module/bar']
