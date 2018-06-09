import logging

import irc3
import boto3

from catbot.user_prefs import UserPrefs


@irc3.plugin
class Greeter:

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__
        self.config = config = bot.config.get(module, {})
        self.botoconfig = botoconfig = bot.config.get('boto', {})

        self.log = logging.getLogger('irc3.{0}'.format(module))
        self.log.debug('Config: %r', config)

        self.greetings = boto3.resource(
            'dynamodb',
            aws_access_key_id=botoconfig.get('aws_access_key_id'),
            aws_secret_access_key=botoconfig.get('aws_secret_access_key'),
            region_name=botoconfig.get('region')
        ).Table(
            '{0}User_Join_Greetings'.format(botoconfig.get(
                'dynamo_table_prefix', ''))
        )

    def get_greeting(self, lang):
        return 'Hello, {name}!'

    @irc3.event(irc3.rfc.JOIN)
    def greet(self, mask, channel, **kwargs):
        if mask.nick != self.bot.nick:
            userprefs = UserPrefs(self.bot, mask.nick)
            greeting = self.get_greeting(userprefs.get_pref('lang'))

            self.bot.privmsg(channel, greeting.format(name=mask.nick))
        else:
            self.bot.privmsg(channel, 'Mew! I\'m online and ready to help! '
                             '=^_^=')
