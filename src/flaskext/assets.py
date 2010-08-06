from webassets import Bundle
from webassets.env import BaseEnvironment, ConfigStorage


__all__ = ('Environment', 'Bundle',)


class FlaskConfigStorage(ConfigStorage):

    _mapping = [
        'debug', 'cache', 'updater', 'auto_create', 'expire', 'directory', 'url',]

    def _transform_key(self, key):
        if key.lower() in self._mapping:
            return "ASSETS_%s" % key.upper()
        else:
            return key.upper()

    def __getitem__(self, key):
        return self.env.app.config[self._transform_key(key)]

    def __setitem__(self, key, value):
        self.env.app.config[self._transform_key(key)] = value

    def __delitem__(self, key):
        del self.env.app.config[self._transform_key(key)]


class Environment(BaseEnvironment):

    config_storage_class = FlaskConfigStorage

    def __init__(self, app):
        self.app = app
        super(Environment, self).__init__()

        self.app.jinja_env.add_extension('webassets.ext.jinja2.AssetsExtension')
        self.app.jinja_env.assets_environment = self
