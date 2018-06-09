import logging

import irc3


@irc3.plugin
class Core:
    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        self.log = logging.getLogger('irc3.{0}'.format(module))
        self.log.debug('Loading Core plugins')

        bot.include('irc3.plugins.command')  # Configuration for !commands
        bot.include('irc3.plugins.ctcp')  # Various handling for CTCP
        bot.include('irc3.plugins.uptime')  # !uptime
        bot.include('catbot.plugins.nickserv')  # NickServ identify

        self.log.debug('Core plugins loaded!')
