import irc3
from irc3.plugins.command import command

from catbot.plugin import Plugin


@irc3.plugin
class UserPrefs(Plugin):
    def list_prefs(self, user):
        prefs = self.data.get_prefs(user)

        user_pref_keys = set(prefs.keys())
        default_pref_keys = set(self.defaults.keys())

        default_only = default_pref_keys - user_pref_keys

        return ['{0} = {1}'.format(x, prefs[x] if x in prefs else
                                   self.defaults[x]) for x in
                list(default_only) + list(prefs.keys())]

    def unset_pref(self, user, pref):
        return self.data.set_pref(user, pref, None)

    def set_pref(self, user, pref, value):
        return self.data.set_pref(user, pref, value)

    def get_pref(self, user, pref):
        pref = pref.lower()
        resp = self.data.get_pref(user, pref)

        return resp if resp is not None else self.defaults.get(pref, 'unset')

    @command(public=False)
    def pref(self, mask, target, args):
        """Set/get user preferences

           %%pref get <key>
           %%pref set <key> <value>...
           %%pref unset <key>
           %%pref list
        """
        if args['list']:
            return self.list_prefs(mask.nick)
        elif args['set']:
            self.set_pref(mask.nick, args['<key>'], ' '.join(args['<value>']))
        elif args['unset']:
            self.unset_pref(mask.nick, args['<key>'])

        return self.get_pref(mask.nick, args['<key>'])
