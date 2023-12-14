import shutil
import tempfile

import pytest
from flask import Flask

from flask_assets import Environment
from tests.helpers import new_blueprint


@pytest.fixture
def app():
    app = Flask(__name__, static_url_path="/app_static")
    bp = new_blueprint("bp", static_url_path="/bp_static", static_folder="static")
    app.register_blueprint(bp)
    return app


@pytest.fixture
def env(app):
    env = Environment(app)
    return env


@pytest.fixture
def no_app_env():
    return Environment()


@pytest.fixture
def temp_dir():
    temp = tempfile.mkdtemp()
    yield temp
    shutil.rmtree(temp, ignore_errors=True)
