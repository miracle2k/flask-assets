from nose import SkipTest
from nose.tools import assert_raises
from flask.app import Flask
try:
    from flask import __version__ as FLASK_VERSION
except ImportError:
    FLASK_VERSION = '0.6'
from webassets.test import TempEnvironmentHelper as BaseTempEnvironmentHelper
from flaskext.assets import Environment

try:
    from flask import Blueprint
    Module = None
except ImportError:
    # Blueprints only available starting with 0.7,
    # fall back to old Modules otherwise.
    Blueprint = None
    from flask import Module


__all__ = ('TempEnvironmentHelper', 'Module', 'Blueprint')


class TempEnvironmentHelper(BaseTempEnvironmentHelper):

    def _create_environment(self):
        if FLASK_VERSION < '0.7':
            # Older Flask versions do not support the
            # static_folder argument, which we need to use
            # a temporary folder for static files, without
            # having to do sys.path hacking.
            raise SkipTest()

        if not hasattr(self, 'app'):
            self.app = Flask(__name__, static_folder=self.tempdir)
        self.env = Environment(self.app)
        return self.env
