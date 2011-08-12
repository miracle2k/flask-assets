from flask import Flask
try:
    from flask import Blueprint
except ImportError:
    # Blueprints only available starting with 0.7,
    # fall back to old Modules otherwise.
    Blueprint = None
    from flask import Module
from flaskext.assets import Environment, Bundle
    

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
