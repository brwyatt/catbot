import logging

import irc3

from catbot.data import Data
from catbot.plugins.user_prefs import UserPrefs


@irc3.plugin
class Greeter:

    data = None

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__
        self.config = config = bot.config.get(module, {})

        self.log = logging.getLogger('irc3.{0}'.format(module))
        self.log.debug('Config: %r', config)

        self.data = Data(bot)

    def get_greeting(self, lang):
        return 'Hello, {name}!'

    @irc3.event(irc3.rfc.JOIN)
    def greet(self, mask, channel, **kwargs):
        if mask.nick != self.bot.nick:
            userprefs = UserPrefs(self.bot)
            greeting = self.get_greeting(userprefs.get_pref(mask.nick, 'lang'))

            self.bot.privmsg(channel, greeting.format(name=mask.nick))
        else:
            self.bot.privmsg(channel, 'Mew! I\'m online and ready to help! '
                             '=^_^=')
