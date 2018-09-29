import logging

import irc3
from irc3.plugins.command import command

from catbot.data import Data


@irc3.plugin
class CacheControl:
    log = None

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        if CacheControl.log is None:
            CacheControl.log = logging.getLogger('irc3.{0}'.format(module))

        self.data = Data(bot)

    @command(permission='admin', public=False, show_in_help_list=False)
    def bustcache(self, mask, target, args):
        """Bust cached data

           %%bustcache all
           %%bustcache <cache_set>
        """

        if args['all']:
            self.data.bustcache(prefs=True, strings=True, stats=True)
            return 'Cache cleared'
        else:
            return '¯\_(ツ)_/¯'
