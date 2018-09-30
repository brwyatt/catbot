import random

import irc3
from irc3.plugins.command import command

from catbot.plugin import Plugin
from catbot.plugins.user_prefs import UserPrefs


@irc3.plugin
class Dice(Plugin):
    userprefs = None

    def __init__(self, bot):
        super().__init__(bot)

        if Dice.userprefs is None:
            Dice.userprefs = UserPrefs(bot)

    def get_string(self, string_id, lang, default):
        string_id = string_id.lower()
        lang = lang.lower()
        default_lang = self.userprefs.defaults.get('lang', 'eng').lower()

        string = self.data.get_string(string_id, lang=lang,
                                      namespace=self.module)

        if string is None and lang != default_lang:
            string = self.data.get_string(string_id, lang=default_lang,
                                          namespace=self.module)

        if string is None:
            string = default

        return string

    @command()
    def roll(self, mask, target, args):
        """Roll dice

           %%roll
           %%roll <count>
           %%roll <count> <sides>
        """

        count = 1
        sides = 6

        lang = self.userprefs.get_pref(mask.nick, 'lang')

        if '<count>' in args and args['<count>'] is not None:
            try:
                count = int(args['<count>'])
            except:
                return self.get_string(
                    'error_non-numeric_count', lang,
                    'ERROR: non-numeric count').format(count=args['<count>'])

        if '<sides>' in args and args['<sides>'] is not None:
            try:
                sides = int(args['<sides>'])
            except:
                return self.get_string(
                    'error_non-numeric_sides', lang,
                    'ERROR: non-numeric sides').format(sides=args['<sides>'])

        if count < 1:
            return self.get_string(
                'error_too_few_dice', lang,
                'ERROR: too few dice').format(count=count)
        elif count > 1000000:
            return self.get_string(
                'error_too_many_dice', lang,
                'ERROR: too many dice').format(count=count)

        if sides < 2:
            return self.get_string(
                'error_too_few_sides', lang,
                'ERROR: too few sides').format(sides=sides)

        total = 0
        for i in range(count):
            total += random.randint(1, sides)

        return self.get_string(
            'success', lang, '{count}xD{sides} = {total}!'
        ).format(count=count, sides=sides, total=total)
