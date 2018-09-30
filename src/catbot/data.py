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

    default_namespaces = {
        'prefs': 'catbot.userdata',
        'strings': 'catbot.default'
    }

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

    def bustcache(self, prefs=False, strings=False, stats=False):
        if prefs:
            Data.prefs = {}

        if strings:
            Data.strings = {}

        if stats:
            Data.stats = {}

    def get_prefs(self, user, namespace=default_namespaces['prefs'],
                  force_refresh=False):
        user = user.lower()
        namespace = namespace.lower()
        entity = '{0}/{1}'.format(namespace, user)

        self.log.info('Getting user prefs for {0}'.format(user))
        self.log.debug('force_refresh = {0}'.format(force_refresh))
        self.log.debug('namespace = {0}'.format(namespace))
        self.log.debug('entity = {0}'.format(entity))

        if (user in Data.prefs and
                Data.prefs[user]['retrieved'] + Data.prefs[user]['ttl'] >
                epoch_now() and not force_refresh):
            self.log.debug('Preference cache for {0} is valid!'.format(user))
        else:
            self.log.debug('Preference cache for {0} is invalid and will '
                           'need to be retrieved!'.format(user))
            data = self.table.get_item(
                Key={
                    'entity': entity,
                    'item': 'prefs'
                }
            ).get('Item', {}).get('value', {})

            Data.prefs[user] = {
                'retrieved': epoch_now(),
                'ttl': 120,
                'data': data
            }

        self.log.debug('{0} => {1}'.format(user, json.dumps(
            Data.prefs[user], indent=2, sort_keys=True)))
        return Data.prefs[user]['data']

    def get_pref(self, user, pref, namespace=default_namespaces['prefs'],
                 force_refresh=False):
        user = user.lower()
        pref = pref.lower()
        data = self.get_prefs(user, namespace=namespace,
                              force_refresh=force_refresh)

        return data.get(pref, None)

    def get_strings(self, string, lang='eng',
                    namespace=default_namespaces['strings'],
                    force_refresh=False):
        string = string.lower()
        lang = lang.lower()
        namespace = namespace.lower()
        entity = '{0}/string:{1}'.format(namespace, string)
        cache_key = '{0}/{1}'.format(entity, lang)

        self.log.info('Fetching string matching {0}'.format(string))
        self.log.debug('lang = {0}'.format(lang))
        self.log.debug('namespace = {0}'.format(namespace))
        self.log.debug('force_refresh = {0}'.format(force_refresh))
        self.log.debug('entity = {0}'.format(entity))
        self.log.debug('cache_key = {0}'.format(cache_key))

        if (cache_key in Data.strings and
                Data.strings[cache_key]['retrieved'] +
                Data.strings[cache_key]['ttl'] > epoch_now() and
                not force_refresh):
            self.log.debug('String cache for {0} is valid!'.format(cache_key))
        else:
            self.log.debug('String cache for {0} is invalid and will need to '
                           'be retrieved!'.format(cache_key))
            data = self.table.get_item(
                Key={
                    'entity': entity,
                    'item': lang
                }
            ).get('Item', {}).get('value', [])

            Data.strings[cache_key] = {
                'retrieved': epoch_now(),
                'ttl': 900,
                'data': data
            }

        self.log.debug('{0} => {1}'.format(cache_key, json.dumps(
            Data.strings[cache_key], indent=2, sort_keys=True)))
        return Data.strings[cache_key]['data']

    def get_string(self, string, lang='eng', index=None,
                   namespace=default_namespaces['strings'],
                   force_refresh=False):
        string = string.lower()
        lang = lang.lower()
        namespace = namespace.lower()

        data = self.get_strings(string, lang, namespace=namespace,
                                force_refresh=force_refresh)

        if len(data) > 0:
            if type(index) is not int:
                index = randint(0, len(data)-1)
            return data[index]
        else:
            return None

    def set_pref(self, user, pref, value,
                 namespace=default_namespaces['prefs']):
        user = user.lower()
        pref = pref.lower()
        namespace = namespace.lower()
        entity = '{0}/{1}'.format(namespace, user)

        self.log.info('Setting user pref {0} for {1}'.format(pref, user))
        self.log.debug('namespace = {0}'.format(namespace))
        self.log.debug('entity = {0}'.format(entity))

        data = self.get_prefs(user, namespace=namespace, force_refresh=True)

        if value is not None:
            data[pref] = value
        else:
            if pref in data:
                del data[pref]

        Data.prefs[user]['data'] = copy.deepcopy(data)

        data = {'value': data}

        data['entity'] = entity
        data['item'] = 'prefs'

        self.table.put_item(
            Item=data
        )

        return True
