import logging

import boto3
from boto3.dynamodb.conditions import Key
import irc3
from irc3.plugins.command import command


@irc3.plugin
class UserPrefs:
    botoconfig = None
    config = None
    defaults = None
    log = None
    table = None

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        if UserPrefs.config is None:
            UserPrefs.config = bot.config.get(module, {})

        if UserPrefs.defaults is None:
            UserPrefs.defaults = bot.config.get('{0}.defaults'.format(module),
                                                {})
            if '#' in UserPrefs.defaults:
                del UserPrefs.defaults['#']
            if 'hash' in UserPrefs.defaults:
                del UserPrefs.defaults['hash']

        if UserPrefs.botoconfig is None:
            UserPrefs.botoconfig = bot.config.get('boto', {})

        if UserPrefs.log is None:
            UserPrefs.log = logging.getLogger('irc3.{0}'.format(module))

        self.log.debug('Config: %r', self.config)
        self.log.debug('Defaults: %r', self.defaults)

        if UserPrefs.table is None:
            UserPrefs.table = boto3.resource(
                'dynamodb',
                aws_access_key_id=self.botoconfig.get('aws_access_key_id'),
                aws_secret_access_key=self.botoconfig.get(
                    'aws_secret_access_key'),
                region_name=self.botoconfig.get('region')
            ).Table(
                '{0}User_Prefs'.format(UserPrefs.botoconfig.get(
                    'dynamo_table_prefix', ''))
            )

    def list_prefs(self, user):
        prefs = {x['pref']: x['value'] for x in
                 self.table.query(
                    KeyConditionExpression=Key('user').eq(user.lower())
                 )['Items']}

        user_pref_keys = set(prefs.keys())
        default_pref_keys = set(self.defaults.keys())

        default_only = default_pref_keys - user_pref_keys

        return ['{0} = {1}'.format(x, prefs[x] if x in prefs else
                                   self.defaults[x]) for x in
                list(default_only) + list(prefs.keys())]

    def unset_pref(self, user, pref):
        return self.table.delete_item(
            Key={
                'user': user.lower(),
                'pref': pref
            }
        )

    def set_pref(self, user, pref, value):
        return self.table.put_item(
            Item={
                'user': user.lower(),
                'pref': pref,
                'value': value
            }
        )

    def get_pref(self, user, pref):
        resp = self.table.get_item(
            Key={
                'user': user.lower(),
                'pref': pref
            }
        )

        return resp.get('Item', {}).get('value',
                                        self.defaults.get(pref, 'unset'))

    @command(public=False)
    def pref(self, mask, target, args):
        """Set/get user preferences

           %%pref get <key>
           %%pref set <key> <value>
           %%pref unset <key>
           %%pref list
        """
        if args['list']:
            return self.list_prefs(mask.nick)
        elif args['set']:
            self.set_pref(mask.nick, args['<key>'], args['<value>'])
        elif args['unset']:
            self.unset_pref(mask.nick, args['<key>'])

        return self.get_pref(mask.nick, args['<key>'])
