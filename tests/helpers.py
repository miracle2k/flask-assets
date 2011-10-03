from flask.app import Flask, Blueprint, Module
from webassets.test import TempEnvironmentHelper as BaseTempEnvironmentHelper
from flaskext.assets import Environment


__all__ = ('TempEnvironmentHelper',)


class TempEnvironmentHelper(BaseTempEnvironmentHelper):

    def setdp(self):
        # webassets now requires the files we pass in to exist,
        # so we can' just do tests with arbitrary filenames.
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


    def _create_environment(self):
        if not hasattr(self, 'app'):
            self.app = Flask(__name__)
        self.env = Environment(self.app)
        return self.env
