import logging

import irc3
from irc3.plugins.command import command

from catbot.data import Data


@irc3.plugin
class AdminPrefs:
    log = None
    namespace = 'catbot.admindata'

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        self.data = Data(bot)

        if AdminPrefs.log is None:
            AdminPrefs.log = logging.getLogger('irc3.{0}'.format(module))

        self.log.debug('Config: %r', self.config)
        self.log.debug('Defaults: %r', self.defaults)

    @property
    def config(self):
        return self.data.get(self.module, 'config', ttl=1800, default={})

    @property
    def defaults(self):
        return self.data.get(self.module, 'defaults', ttl=900, default={})

    def list_adminprefs(self):
        prefs = self.data.get_prefs(self.bot.nick.lower(),
                                    namespace=self.namespace)

        user_pref_keys = set(prefs.keys())
        default_pref_keys = set(self.defaults.keys())

        default_only = default_pref_keys - user_pref_keys

        return ['{0} = {1}'.format(x, prefs[x] if x in prefs else
                                   self.defaults[x]) for x in
                list(default_only) + list(prefs.keys())]

    def unset_adminpref(self, pref):
        return self.data.set_pref(self.bot.nick.lower(), pref, None,
                                  namespace=self.namespace)

    def set_adminpref(self, pref, value):
        return self.data.set_pref(self.bot.nick.lower(), pref, value,
                                  namespace=self.namespace)

    def get_adminpref(self, pref):
        pref = pref.lower()
        resp = self.data.get_pref(self.bot.nick.lower(), pref,
                                  namespace=self.namespace)

        return resp if resp is not None else self.defaults.get(pref, 'unset')

    @command(permission='admin', public=False, show_in_help_list=False)
    def adminpref(self, mask, target, args):
        """Set/get bot/admin preferences

           %%adminpref get <key>
           %%adminpref set <key> <value>...
           %%adminpref unset <key>
           %%adminpref list
        """
        if args['list']:
            return self.list_adminprefs()
        elif args['set']:
            self.set_adminpref(args['<key>'], ' '.join(args['<value>']))
        elif args['unset']:
            self.unset_adminpref(args['<key>'])

        return self.get_adminpref(args['<key>'])
