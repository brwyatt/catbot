import logging

import irc3


@irc3.plugin
class Core:
    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        self.log = logging.getLogger('irc3.{0}'.format(module))
        self.log.debug('Loading Core plugins')

        bot.include('irc3.plugins.command')
        bot.include('irc3.plugins.ctcp')
        bot.include('irc3.plugins.uptime')
        bot.include('catbot.plugins.nickserv')

        self.log.debug('Core plugins loaded!')
