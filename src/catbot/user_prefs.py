import logging

import boto3


class UserPrefs:

    def __init__(self, bot, user):
        self.bot = bot
        self.user = user
        self.module = module = self.__class__.__module__
        self.config = config = bot.config.get(module, {})
        self.botoconfig = botoconfig = bot.config.get('boto', {})

        self.log = logging.getLogger('irc3.{0}'.format(module))
        self.log.debug('Config: %r', config)

        self.userpref_table = boto3.resource(
            'dynamodb',
            aws_access_key_id=botoconfig.get('aws_access_key_id'),
            aws_secret_access_key=botoconfig.get('aws_secret_access_key'),
            region_name=botoconfig.get('region')
        ).Table(
            '{0}User_Prefs'.format(botoconfig.get('dynamo_table_prefix', ''))
        )

    def set_pref(self, pref, value):
        pass

    def get_pref(self, pref):
        resp = self.userpref_table.get_item(
            Key={
                'user': self.user,
                'pref': pref
            }
        )

        return resp['Item'].get('value', 'unset')
