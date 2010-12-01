from flask import _request_ctx_stack
from webassets import Bundle
from webassets.env import BaseEnvironment, ConfigStorage


__version__ = (0, 2, 'dev')

__all__ = ('Environment', 'Bundle',)


class FlaskConfigStorage(ConfigStorage):
    """Uses the config object of a Flask app as the backend: either the app
    instance bound to the extension directly, or the current Flasp app on
    the stack.

    Also provides per-application defaults for some values.

    Note that if no app is available, this config object is basically
    unusable - this is by design; this could also let the user set defaults
    by writing to a container not related to any app, which would be used
    as a fallback if a current app does not include a key. However, at least
    for now, I specifically made the choice to keep things simple and not
    allow global across-app defaults.
    """

    _mapping = [
        'debug', 'cache', 'updater', 'auto_create', 'expire', 'directory', 'url',]

    def __init__(self, *a, **kw):
        self._defaults = {}
        ConfigStorage.__init__(self, *a, **kw)

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
        raise RuntimeError('assets instance not bound to an application, '+
                           'and no application in current context')

    def _app_default_url(self):
        return '/static'

    def _app_default_directory(self):
        return self._app.root_path + self._app.static_path

    def setdefault(self, key, value):
        """We may not always be connected to an app, but we still need
        to provide a way to the base environment to set it's defaults.
        """
        try:
            super(FlaskConfigStorage, self).setdefault(key, value)
        except RuntimeError:
            self._defaults.__setitem__(key, value)

    def __contains__(self, key):
        return self._transform_key(key) in self._app.config

    def __getitem__(self, key):
        # First try the current app's config
        public_key = self._transform_key(key)
        if self._app:
            if public_key in self._app.config:
                return self._app.config[public_key]

        # Try a non-app specific default value
        if key in self._defaults:
            return self._defaults.__getitem__(key)

        # Finally try to use a default based on the current app
        deffunc = getattr(self, "_app_default_%s" % key, False)
        if deffunc:
            return deffunc()

        # We've run out of options
        raise IndexError()

    def __setitem__(self, key, value):
        self._app.config[self._transform_key(key)] = value

    def __delitem__(self, key):
        del self._app.config[self._transform_key(key)]


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