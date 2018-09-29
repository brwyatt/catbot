import logging

import irc3
from irc3.plugins.command import command

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
        lang = lang.lower()
        default_lang = UserPrefs.defaults.get('lang', 'eng').lower()

        greeting = self.data.get_string('greeting', lang=lang)

        if greeting is None and lang != default_lang:
            greeting = self.data.get_string('greeting', lang=default_lang)

        if greeting is None:
            greeting = 'Hello, {nick}!'

        return greeting

    def get_botjoin(self):
        lang = UserPrefs.defaults.get('lang', 'eng').lower()

        greeting = self.data.get_string('botjoin', lang=lang)

        if greeting is None:
            greeting = 'Mew! I\'m online and ready to help! =^_^='

        return greeting

    @irc3.event(irc3.rfc.JOIN)
    def greet(self, mask, channel, **kwargs):
        if mask.nick != self.bot.nick:
            userprefs = UserPrefs(self.bot)
            greeting = self.get_greeting(userprefs.get_pref(mask.nick, 'lang'))
        else:
            greeting = self.get_botjoin()

        self.bot.privmsg(channel, greeting.format(nick=mask.nick))

    @command(show_in_help_list=False)
    def greetme(self, mask, target, args):
        """Force bot greeting

           %%greetme
        """

        userprefs = UserPrefs(self.bot)
        greeting = self.get_greeting(userprefs.get_pref(mask.nick, 'lang'))

        self.bot.privmsg(target, greeting.format(nick=mask.nick))
