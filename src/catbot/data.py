import calendar
import copy
import json
import logging
from random import randint
import time

import boto3
from boto3.dynamodb.conditions import Key


def epoch_now():
    return calendar.timegm(time.gmtime())


class Data:

    table = None
    prefs = {}
    strings = {}
    stats = {}

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__
        self.config = config = bot.config.get(module, {})
        self.botoconfig = botoconfig = bot.config.get('boto', {})

        self.log = logging.getLogger('irc3.{0}'.format(module))
        self.log.debug('Config: %r', config)

        if Data.table is None:
            Data.table = boto3.resource(
                'dynamodb',
                aws_access_key_id=botoconfig.get('aws_access_key_id'),
                aws_secret_access_key=botoconfig.get('aws_secret_access_key'),
                region_name=botoconfig.get('region')
            ).Table(botoconfig['dynamo_table'])

    def get_prefs(self, user, force_refresh=False):
        user = user.lower()

        self.log.info('Getting user prefs for {0}'.format(user))
        self.log.debug('force_refresh = {0}'.format(force_refresh))

        if (user in Data.prefs and
                Data.prefs[user]['retrieved'] + Data.prefs[user]['ttl'] >
                epoch_now() and not force_refresh):
            self.log.debug('Preference cache for {0} is valid!'.format(user))
        else:
            self.log.debug('Preference cache for {0} is invalid and will '
                           'need to be retrieved!'.format(user))
            data = self.table.get_item(
                Key={
                    'user': user,
                    'key': 'prefs'
                }
            ).get('Item', {})

            if 'user' in data:
                del data['user']
            if 'key' in data:
                del data['key']

            Data.prefs[user] = {
                'retrieved': epoch_now(),
                'ttl': 120,
                'data': data
            }

        self.log.debug('{0} => {1}'.format(user, json.dumps(
            Data.prefs[user], indent=2, sort_keys=True)))
        return Data.prefs[user]['data']

    def get_pref(self, user, pref, force_refresh=False):
        user = user.lower()
        pref = pref.lower()
        data = self.get_prefs(user, force_refresh=force_refresh)

        return data.get(pref, None)

    def get_strings(self, string, lang='eng', force_refresh=False):
        string = string.lower()
        lang = lang.lower()
        string_key = '*str.{0}.{1}'.format(string, lang)

        self.log.info('Fetching string matching {0}'.format(string_key))
        self.log.debug('force_refresh = {0}'.format(force_refresh))

        if (string_key in Data.strings and
                Data.strings[string_key]['retrieved'] +
                Data.strings[string_key]['ttl'] > epoch_now() and
                not force_refresh):
            self.log.debug('String cache for {0} is valid!'.format(string_key))
        else:
            self.log.debug('String cache for {0} is invalid and will need to '
                           'be retrieved!'.format(string_key))
            data = [x['string'] for x in
                    self.table.query(
                        KeyConditionExpression=Key('user').eq(string_key)
                    ).get('Items', [])]

            Data.strings[string_key] = {
                'retrieved': epoch_now(),
                'ttl': 900,
                'data': data
            }

        self.log.debug('{0} => {1}'.format(string_key, json.dumps(
            Data.strings[string_key], indent=2, sort_keys=True)))
        return Data.strings[string_key]['data']

    def get_string(self, string, lang='eng', index=None, force_refresh=False):
        string = string.lower()
        lang = lang.lower()

        data = self.get_strings(string, lang, force_refresh=force_refresh)

        if len(data) > 0:
            if type(index) is not int:
                index = randint(0, len(data)-1)
            return data[index]
        else:
            return None

    def set_pref(self, user, pref, value):
        user = user.lower()
        pref = pref.lower()

        data = self.get_prefs(user, force_refresh=True)

        if value is not None:
            data[pref] = value
        else:
            if pref in data:
                del data[pref]

        Data.prefs[user]['data'] = copy.deepcopy(data)

        data['user'] = user
        data['key'] = 'prefs'

        self.table.put_item(
            Item=data
        )

        return True
