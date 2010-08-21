from nose.tools import assert_raises
from flask import Flask
from flaskext.assets import Environment


class TestConfig:
    """The Environment configuration is hooked up to the Flask config
    dict.
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