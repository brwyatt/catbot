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
        # Set/get bot/admin preferences
        bot.include('catbot.plugins.admin_prefs')
        bot.include('catbot.plugins.dice')  # Roll dice
        bot.include('catbot.plugins.nickserv')  # NickServ identify
        bot.include('catbot.plugins.greeter')  # Greet on join
        bot.include('catbot.plugins.user_prefs')  # Set/get user preferences

        self.log.debug('Core plugins loaded!')
