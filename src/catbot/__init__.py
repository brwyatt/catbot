# from copy import deepcopy

from irc3 import IrcBot

from catbot.data import Data


def run(argv=None):
    data = Data.data()
    config = data.get_config(entity=__name__)

    config.update(config.pop('bot'))

    bots = {}
    bot = IrcBot.from_config(config, botnet=bots)
    bots['bot'] = bot

    # # This actually doesn't work... yet... XD
    # for section in list(bot.config):
    #     if section.startswith('bot_'):
    #         sub_config = deepcopy(bot.config).update(bot.config.pop(section))
    #         bots[section] = IrcBot.from_config(sub_config, botnet=bots)
    #         bots[section].run(forever=False)

    bot.run(forever=False)
    bot.loop.run_forever()
    return bots
