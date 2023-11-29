import os
import types

from flask_assets import Bundle


def test_assets_tag(app, env):
    env.register("test", "file1", "file2")
    template = app.jinja_env.from_string("{% assets 'test' %}{{ASSET_URL}};{% endassets %}")
    assert template.render() == "/app_static/file1;/app_static/file2;"


def test_from_module(app, env):
    module = types.ModuleType("test")
    module.pytest = Bundle("py_file1", "py_file2")
    env.from_module(module)
    template = app.jinja_env.from_string('{% assets "pytest" %}{{ASSET_URL}};{% endassets %}')
    assert template.render() == '/app_static/py_file1;/app_static/py_file2;'


def test_from_yaml(app, env):
    with open("test.yaml", "w", encoding="utf-8") as f:
        f.write("""
        yaml_test:
            contents:
                - yaml_file1
                - yaml_file2
        """)
    try:
        env.from_yaml("test.yaml")
        template = app.jinja_env.from_string('{% assets "yaml_test" %}{{ASSET_URL}};{% endassets %}')
        assert template.render() == "/app_static/yaml_file1;/app_static/yaml_file2;"
    finally:
        os.remove("test.yaml")
