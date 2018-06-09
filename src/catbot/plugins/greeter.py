import logging

import irc3


@irc3.plugin
class Greeter:

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__
        self.config = config = bot.config.get(module, {})

        self.log = logging.getLogger('irc3.{0}'.format(module))
        self.log.debug('Config: %r', config)

    @irc3.event(irc3.rfc.JOIN)
    def greet(self, mask, channel, **kwargs):
        greeting = 'Hello, {0}!'

        if mask.nick != self.bot.nick:
            self.bot.privmsg(channel, greeting.format(mask.nick))
        else:
            self.bot.privmsg(channel, 'Mew! I\'m online and ready to help! '
                             '=^_^=')
