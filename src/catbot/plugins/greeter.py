import irc3
from irc3.plugins.command import command

from catbot.plugin import Plugin
from catbot.plugins.user_prefs import UserPrefs


@irc3.plugin
class Greeter(Plugin):
    userprefs = None

    def __init__(self, bot):
        super().__init__(bot)

        if Greeter.userprefs is None:
            Greeter.userprefs = UserPrefs(bot)

    def get_greeting(self, lang):
        lang = lang.lower()
        default_lang = self.userprefs.defaults.get('lang', 'eng').lower()

        greeting = self.data.get_string('greeting', lang=lang,
                                        namespace=self.module)

        if greeting is None and lang != default_lang:
            greeting = self.data.get_string('greeting', lang=default_lang,
                                            namespace=self.module)

        if greeting is None:
            greeting = 'Hello, {nick}!'

        return greeting

    def get_botjoin(self):
        lang = self.userprefs.defaults.get('lang', 'eng').lower()

        greeting = self.data.get_string('botjoin', lang=lang,
                                        namespace=self.module)

        if greeting is None:
            greeting = 'Mew! I\'m online and ready to help! =^_^='

        return greeting

    @irc3.event(irc3.rfc.JOIN)
    def greet(self, mask, channel, **kwargs):
        if mask.nick != self.bot.nick:
            greeting = self.get_greeting(
                self.userprefs.get_pref(mask.nick, 'lang'))
        else:
            greeting = self.get_botjoin()

        self.bot.privmsg(channel, greeting.format(nick=mask.nick))

    @command(show_in_help_list=False)
    def greetme(self, mask, target, args):
        """Force bot greeting

           %%greetme
        """

        greeting = self.get_greeting(
            self.userprefs.get_pref(mask.nick, 'lang'))

        return greeting.format(nick=mask.nick)
