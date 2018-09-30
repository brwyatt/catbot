import random

import irc3
from irc3.plugins.command import command

from catbot.plugin import Plugin


@irc3.plugin
class Dice(Plugin):
    @command()
    def roll(self, mask, target, args):
        """Roll dice

           %%roll
           %%roll <count>
           %%roll <count> <sides>
        """

        count = 1
        sides = 6

        if '<count>' in args and args['<count>'] is not None:
            try:
                count = int(args['<count>'])
            except:
                return 'ERROR: I can\'t roll a non-numeric amount of things!'

        if '<sides>' in args and args['<sides>'] is not None:
            try:
                sides = int(args['<sides>'])
            except:
                return 'ERROR: I can\'t roll something with non-numeric sides!'

        if count < 1:
            return 'ERROR: I have to roll SOMETHING!'
        elif count > 1000000:
            return 'I don\'t have that many dice to roll!'

        if sides < 2:
            return 'Error: Cannot roll something with less than 2 sides!'

        total = 0
        for i in range(count):
            total += random.randint(1, sides)

        return 'Rolled {count} D{sides} and got {total}!'.format(count=count,
                                                                 sides=sides,
                                                                 total=total)
