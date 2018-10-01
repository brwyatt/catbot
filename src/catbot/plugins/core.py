import irc3

from catbot.plugin import Plugin


@irc3.plugin
class Core(Plugin):
    def __init__(self, bot):
        super().__init__(bot)

        self.log.debug('Loading Core plugins')

        bot.include('irc3.plugins.command')  # Configuration for !commands
        bot.include('irc3.plugins.ctcp')  # Various handling for CTCP
        bot.include('irc3.plugins.uptime')  # !uptime
        # Set/get bot/admin preferences
        bot.include('catbot.plugins.admin_prefs')
        bot.include('catbot.plugins.cache_control')  # Control local data cache
        bot.include('catbot.plugins.chat_stats')  # User chat stats
        bot.include('catbot.plugins.dice')  # Roll dice
        bot.include('catbot.plugins.nickserv')  # NickServ identify
        bot.include('catbot.plugins.greeter')  # Greet on join
        bot.include('catbot.plugins.user_prefs')  # Set/get user preferences

        self.log.debug('Core plugins loaded!')
