import logging
import random

import irc3
from irc3.plugins.command import command


@irc3.plugin
class Dice:
    config = None
    defaults = None
    log = None

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        if Dice.config is None:
            Dice.config = bot.config.get(module, {})

        if Dice.defaults is None:
            Dice.defaults = bot.config.get('{0}.defaults'.format(module), {})
            if '#' in Dice.defaults:
                del Dice.defaults['#']
            if 'hash' in Dice.defaults:
                del Dice.defaults['hash']

        if Dice.log is None:
            Dice.log = logging.getLogger('irc3.{0}'.format(module))

        self.log.debug('Config: %r', self.config)
        self.log.debug('Defaults: %r', self.defaults)

    @command()
    def roll(self, mask, target, args):
        """Roll dice

           %%roll
           %%roll <count>
           %%roll <count>d<sides>
        """

        count = 1
        sides = 6

        if '<count>' in args:
            count = args['<count>']

        if '<sides>' in args:
            sides = args['<sides>']

        if count < 1:
            return 'ERROR: I have to roll SOMETHING!'

        if sides < 2:
            return 'Error: Cannot roll something with less than 2 sides!'

        total = 0
        for i in range(count):
            total += random.randint(1, sides)

        return 'Rolled {count} D{sides} and got {total}!'.format(count=count,
                                                                 sides=sides,
                                                                 total=total)
