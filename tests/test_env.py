from nose.tools import assert_raises
from flask import Flask
from flask.ext.assets import Environment


class TestEnv:

    def setup(self):
        self.app = Flask(__name__)
        self.env = Environment(self.app)
        self.env.debug = True
        self.app.config.update({
            'ASSETS_DIRECTORY': '',
            'ASSETS_URL': '/foo',
        })
        self.env.register('test', 'file1', 'file2')

    def test_tag_available(self):
        """Jinja tag has been made available.
        """
        t = self.app.jinja_env.from_string('{% assets "test" %}{{ASSET_URL}};{% endassets %}');
        assert t.render() == '/foo/file1;/foo/file2;'
