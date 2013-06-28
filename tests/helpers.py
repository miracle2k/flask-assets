from flask.app import Flask
from webassets.test import TempEnvironmentHelper as BaseTempEnvironmentHelper
from flask.ext.assets import Environment

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

    def _create_environment(self, **kwargs):
        if not hasattr(self, 'app'):
            self.app = Flask(__name__, static_folder=self.tempdir, **kwargs)
        self.env = Environment(self.app)
        return self.env


try:
    from test.test_support import check_warnings
except ImportError:
    # Python < 2.6
    import contextlib

    @contextlib.contextmanager
    def check_warnings(*filters, **kwargs):
        # We cannot reasonably support this, we'd have to copy to much code.
        # (or write our own). Since this is only testing warnings output,
        # we might slide by ignoring it.
        yield
