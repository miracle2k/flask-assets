"""The Environment configuration is hooked up to the Flask config dict.
"""

from nose.tools import assert_raises
from flask import Flask
from flaskext.assets import Environment


class TestConfigAppBound:
    """The extension is bound to a specific app.
    """

    def setup(self):
        self.app = Flask(__name__)
        self.env = Environment(self.app)

    def test_no_defaults(self):
        """directory and url have default values.
        """
        assert self.env.directory.startswith(self.app.root_path)
        assert self.env.url

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
        assert_raises(RuntimeError, getattr, self.env, 'url')
        assert_raises(RuntimeError, setattr, self.env, 'debug', True)
        assert_raises(RuntimeError, self.env.config.get, 'debug')

    def test_global_defaults(self):
        """We may set defaults even without an application, however."""
        self.env.config.setdefault('FOO', 'BAR')
        with Flask(__name__).test_request_context():
            assert self.env.config['FOO'] == 'BAR'

    def test_app_specific_defaults(self):
        """The defaults for url and directory are read from the app object.
        """
        app = Flask(__name__, static_path='/foo')
        self.env.init_app(app)
        with app.test_request_context():
            assert self.env.url.endswith('static')
            assert self.env.directory.endswith('foo')

            # Can be overridden
            self.env.directory = 'new_media_dir'
            assert self.env.directory == 'new_media_dir'

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
            assert_raises(KeyError, self.env.config.get, 'YADDAYADDA')
