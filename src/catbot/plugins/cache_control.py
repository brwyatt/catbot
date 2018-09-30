import irc3
from irc3.plugins.command import command

from catbot.plugin import Plugin


@irc3.plugin
class CacheControl(Plugin):
    @command(permission='admin', public=False, show_in_help_list=False)
    def bustcache(self, mask, target, args):
        """Bust cached data

           %%bustcache
        """

        self.data.bustcache()
        return 'Cache cleared'
