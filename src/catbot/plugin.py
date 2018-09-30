import logging

import irc3

from catbot.data import Data


@irc3.plugin
class Plugin:
    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        self.data = Data(bot)

        self.log = logging.getLogger('irc3.{0}'.format(module))

        self.log.debug('Config: %r', self.config)
        self.log.debug('Defaults: %r', self.defaults)

    @property
    def config(self):
        return self.data.get(self.module, 'config', ttl=1800, default={})

    @property
    def defaults(self):
        return self.data.get(self.module, 'defaults', ttl=900, default={})
