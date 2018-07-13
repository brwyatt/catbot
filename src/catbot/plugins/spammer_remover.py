import logging

import boto3
from boto3.dynamodb.conditions import Key
import irc3
from irc3.plugins.command import command


@irc3.plugin
class SpammerRemover:
    botoconfig = None
    config = None
    defaults = None
    log = None
    table = None

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        if SpammerRemover.config is None:
            SpammerRemover.config = bot.config.get(module, {})

        if SpammerRemover.defaults is None:
            SpammerRemover.defaults = bot.config.get('{0}.defaults'.format(
                module), {})
            if '#' in SpammerRemover.defaults:
                del SpammerRemover.defaults['#']
            if 'hash' in SpammerRemover.defaults:
                del SpammerRemover.defaults['hash']

        if SpammerRemover.botoconfig is None:
            SpammerRemover.botoconfig = bot.config.get('boto', {})

        if SpammerRemover.log is None:
            SpammerRemover.log = logging.getLogger('irc3.{0}'.format(module))

        self.log.debug('Config: %r', self.config)
        self.log.debug('Defaults: %r', self.defaults)

        if SpammerRemover.table is None:
            SpammerRemover.table = boto3.resource(
                'dynamodb',
                aws_access_key_id=self.botoconfig.get('aws_access_key_id'),
                aws_secret_access_key=self.botoconfig.get(
                    'aws_secret_access_key'),
                region_name=self.botoconfig.get('region')
            ).Table(
                '{0}User_Chat_Stats'.format(SpammerRemover.botoconfig.get(
                    'dynamo_table_prefix', ''))
            )

    @irc3.event(irc3.rfc.JOIN)
    def user_join(self, mask, channel, **kwargs):
        # Start Timer
        pass

    @irc3.event(irc3.rfc.KICK)
    def user_kick(self, mask, channel, **kwargs):
        # Stop Timer
        pass

    @irc3.event(irc3.rfc.NEW_NICK)
    def user_new_nick(self, nick, new_nick, **kwargs):
        # Stop Timer - All channels
        # Start Timer - All channels
        pass

    @irc3.event(irc3.rfc.PART)
    def user_part(self, mask, channel, **kwargs):
        # Stop Timer
        pass

    @irc3.event(irc3.rfc.PRIVMSG)
    def user_privmsg(self, mask, event, target, **kwargs):
        # Increment counter
        pass

    @irc3.event(irc3.rfc.QUIT)
    def user_quit(self, mask, **kwargs):
        # Stop Timer - All channels
        pass
