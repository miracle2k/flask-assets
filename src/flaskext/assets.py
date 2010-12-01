from flask import _request_ctx_stack
from webassets import Bundle
from webassets.env import BaseEnvironment, DictConfigStorage


__version__ = (0, 2, 'dev')

__all__ = ('Environment', 'Bundle',)


class FlaskConfigStorage(DictConfigStorage):
    """Uses the config object of a Flask app as the backend: either the app
    instance bound to the extension directly, or the current Flasp app on
    the stack.

    If no app is available, it writes to a defaults dictionary, which will
    be used as a fallback if no app-specific options are found.

    Also provides per-application defaults for some values.
    """

    _mapping = [
        'debug', 'cache', 'updater', 'auto_create', 'expire', 'directory', 'url',]

    def _transform_key(self, key):
        if key.lower() in self._mapping:
            return "ASSETS_%s" % key.upper()
        else:
            return key.upper()

    @property
    def _app(self):
        """The application object to work with; this is either the app
        that we have been bound to, or the current application.
        """
        if self.env.app is not None:
            return self.env.app
        else:
            ctx = _request_ctx_stack.top
            if ctx is not None:
                return ctx.app
        return None

    def _app_default_url(self):
        return '/static'

    def _app_default_directory(self):
        return self._app.root_path + self._app.static_path

    def __contains__(self, key):
        if self._app:
            return self._transform_key(key) in self._app.config
        else:
            return DictConfigStorage.__contains__(self, key)

    def __getitem__(self, key):
        # First try the current app's config
        public_key = self._transform_key(key)
        if self._app:
            if public_key in self._app.config:
                return self._app.config[public_key]

        # Try a non-app specific value
        if DictConfigStorage.__contains__(self, key):
            return DictConfigStorage.__getitem__(self, key)

        # Finally try to use a default based on the current app
        deffunc = getattr(self, "_app_default_%s" % key, False)
        if deffunc:
            if not self._app:
                raise RuntimeError('assets instance not bound to an application, '+
                                   'and no application in current context')
            return deffunc()

        # We've run out of options
        raise IndexError()

    def __setitem__(self, key, value):
        if self._app:
            self._app.config[self._transform_key(key)] = value
        else:
            DictConfigStorage.__setitem__(self, key, value)

    def __delitem__(self, key):
        if self._app:
            del self._app.config[self._transform_key(key)]
        else:
            DictConfigStorage.__delitem__(self, key)


class Environment(BaseEnvironment):

    config_storage_class = FlaskConfigStorage

    def __init__(self, app=None):
        self.app = app
        super(Environment, self).__init__()
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.jinja_env.add_extension('webassets.ext.jinja2.AssetsExtension')
        app.jinja_env.assets_environment = self