import os

from flask import Blueprint

__all__ = ("create_files", "new_blueprint")


def create_files(parent, *files):
    result = []
    for file in files:
        path = os.path.join(parent, file)
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        f = open(path, "w", encoding="utf-8")
        f.close()
        result.append(path)

    return result


def new_blueprint(name, import_name=None, **kwargs):
    if import_name is None:
        from tests import bp_for_test
        import_name = bp_for_test.__name__
    bp = Blueprint(name, import_name, **kwargs)
    return bp
