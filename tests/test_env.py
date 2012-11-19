import os
from nose.tools import assert_raises
from flask import Flask
from flask.ext.assets import Environment, Bundle


class TestEnv:

    def setup(self):
        self.app = Flask(__name__)
        self.env = Environment(self.app)
        self.env.debug = True
        self.env.register('test', 'file1', 'file2')

    def test_tag_available(self):
        """Jinja tag has been made available.
        """
        t = self.app.jinja_env.from_string('{% assets "test" %}{{ASSET_URL}};{% endassets %}')
        assert t.render() == '/static/file1;/static/file2;'

    def test_from_yaml(self):
        """YAML configuration gets loaded
        """
        f = open('test.yaml', 'w')
        f.write("""
        yamltest:
            contents:
                - yamlfile1
                - yamlfile2
        """)
        f.close()

        self.env.from_yaml('test.yaml')

        t = self.app.jinja_env.from_string('{% assets "yamltest" %}{{ASSET_URL}};{% endassets %}')
        assert t.render() == '/static/yamlfile1;/static/yamlfile2;'

        os.remove('test.yaml')

    def test_from_python_module(self):
        """Python configuration module gets loaded
        """
        import types
        module = types.ModuleType('test')
        module.pytest = Bundle('pyfile1', 'pyfile2')

        self.env.from_module(module)

        t = self.app.jinja_env.from_string('{% assets "pytest" %}{{ASSET_URL}};{% endassets %}')
        assert t.render() == '/static/pyfile1;/static/pyfile2;'
