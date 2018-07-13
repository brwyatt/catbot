import logging

import boto3
from boto3.dynamodb.conditions import Key
import irc3
from irc3.plugins.command import command


@irc3.plugin
class AdminPrefs:
    botoconfig = None
    config = None
    defaults = None
    log = None
    table = None
    admin_key = None

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__

        if AdminPrefs.config is None:
            AdminPrefs.config = bot.config.get(module, {})

        if AdminPrefs.defaults is None:
            AdminPrefs.defaults = bot.config.get('{0}.defaults'.format(module),
                                                 {})
            if '#' in AdminPrefs.defaults:
                del AdminPrefs.defaults['#']
            if 'hash' in AdminPrefs.defaults:
                del AdminPrefs.defaults['hash']

        if AdminPrefs.botoconfig is None:
            AdminPrefs.botoconfig = bot.config.get('boto', {})

        if AdminPrefs.log is None:
            AdminPrefs.log = logging.getLogger('irc3.{0}'.format(module))

        if AdminPrefs.admin_key is None:
            AdminPrefs.admin_key = '*{0}'.format(bot.nick.lower())

        self.log.debug('Config: %r', self.config)
        self.log.debug('Defaults: %r', self.defaults)

        if AdminPrefs.table is None:
            AdminPrefs.table = boto3.resource(
                'dynamodb',
                aws_access_key_id=self.botoconfig.get('aws_access_key_id'),
                aws_secret_access_key=self.botoconfig.get(
                    'aws_secret_access_key'),
                region_name=self.botoconfig.get('region')
            ).Table(
                '{0}User_Prefs'.format(AdminPrefs.botoconfig.get(
                    'dynamo_table_prefix', ''))
            )

    def list_adminprefs(self):
        prefs = {x['pref']: x['value'] for x in
                 self.table.query(
                    KeyConditionExpression=Key('user').eq(self.admin_key)
                 )['Items']}

        user_pref_keys = set(prefs.keys())
        default_pref_keys = set(self.defaults.keys())

        default_only = default_pref_keys - user_pref_keys

        return ['{0} = {1}'.format(x, prefs[x] if x in prefs else
                                   self.defaults[x]) for x in
                list(default_only) + list(prefs.keys())]

    def unset_adminpref(self, pref):
        return self.table.delete_item(
            Key={
                'user': self.admin_key,
                'pref': pref
            }
        )

    def set_adminpref(self, pref, value):
        return self.table.put_item(
            Item={
                'user': self.admin_key,
                'pref': pref,
                'value': value
            }
        )

    def get_adminpref(self, pref):
        resp = self.table.get_item(
            Key={
                'user': self.admin_key,
                'pref': pref
            }
        )

        return resp.get('Item', {}).get('value',
                                        self.defaults.get(pref, 'unset'))

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
