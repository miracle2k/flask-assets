import pytest
from flask import Flask


def test_env_set(app, env):
    env.url = "https://github.com/miracle2k/flask-assets"
    assert app.config["ASSETS_URL"] == "https://github.com/miracle2k/flask-assets"


def test_env_get(app, env):
    app.config["ASSETS_URL"] = "https://github.com/miracle2k/flask-assets"
    assert env.url == "https://github.com/miracle2k/flask-assets"


def test_env_config(app, env):
    app.config["LESS_PATH"] = "/usr/bin/less"
    assert env.config["LESS_PATH"] == "/usr/bin/less"

    with pytest.raises(KeyError):
        _ = env.config["do_not_exist"]

    assert env.config.get("do_not_exist") is None


def test_no_app_env_set(no_app_env):
    with pytest.raises(RuntimeError):
        no_app_env.debug = True


def test_no_app_env_get(no_app_env):
    with pytest.raises(RuntimeError):
        no_app_env.config.get("debug")


def test_no_app_env_config(app, no_app_env):
    no_app_env.config.setdefault("foo", "bar")
    with app.test_request_context():
        assert no_app_env.config["foo"] == "bar"


def test_config_isolation_within_apps(no_app_env):
    no_app_env.config.setdefault("foo", "bar")

    app1 = Flask(__name__)
    with app1.test_request_context():
        assert no_app_env.config["foo"] == "bar"

        no_app_env.config["foo"] = "qux"
        assert no_app_env.config["foo"] == "qux"

    app2 = Flask(__name__)
    with app2.test_request_context():
        assert no_app_env.config["foo"] == "bar"
