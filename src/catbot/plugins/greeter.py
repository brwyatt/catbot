import logging

import irc3

from catbot.user_prefs import UserPrefs


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
        userprefs = UserPrefs(self.bot, mask.nick)

        greeting = 'Hello, {name}! - lang={lang}'

        if mask.nick != self.bot.nick:
            self.bot.privmsg(channel, greeting.format(
                lang=userprefs.get_pref('lang'), name=mask.nick))
        else:
            self.bot.privmsg(channel, 'Mew! I\'m online and ready to help! '
                             '=^_^=')
