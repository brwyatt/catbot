import calendar
from decimal import Decimal
import json
import logging
from random import randint
import time

import boto3


def epoch_now():
    return calendar.timegm(time.gmtime())


def fix_dynamo_types(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


class Data:

    table = None
    cache = {}

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

    def bustcache(self):
        Data.cache = {}

    def get(self, entity, item, ttl=120, force_refresh=False, default=None):
        entity = entity.lower()
        item = item.lower()

        self.log.info('Retrieving {0} / {1}'.format(entity, item))
        self.log.debug('ttl = {0}'.format(ttl))
        self.log.debug('force_refresh = {0}'.format(force_refresh))

        if (entity in Data.cache and item in Data.cache[entity] and
                Data.cache[entity][item].get('retrieved', 0) +
                Data.cache[entity][item].get('ttl', 0) > epoch_now() and
                not force_refresh):
            self.log.debug('Cache for {0} / {1} is valid!'.format(entity, item))
        else:
            self.log.debug('Cache for {0} / {1} is invalid and will need to be '
                           'retrieved!'.format(entity, item))
            data = self.table.get_item(
                Key={
                    'entity': entity,
                    'item': item
                }
            ).get('Item', {}).get('value', default)

            if entity not in Data.cache:
                Data.cache[entity] = {}

            Data.cache[entity][item] = {
                'retrieved': epoch_now(),
                'ttl': ttl,
                'data': data
            }

        self.log.debug('{0} / {1} => {2}'.format(entity, item, json.dumps(
            Data.cache[entity][item], indent=2, sort_keys=True,
            default=fix_dynamo_types)))
        return Data.cache[entity][item]['data']

    def get_prefs(self, user, namespace=default_namespaces['prefs'],
                  force_refresh=False):
        entity = '{0}/{1}'.format(namespace, user)

        prefs = self.get(entity, 'prefs', ttl=120, force_refresh=force_refresh,
                         default={})

        return prefs

    def get_pref(self, user, pref, namespace=default_namespaces['prefs'],
                 force_refresh=False):
        data = self.get_prefs(user, namespace=namespace,
                              force_refresh=force_refresh)

        return data.get(pref, None)

    def get_strings(self, string, lang='eng',
                    namespace=default_namespaces['strings'],
                    force_refresh=False):
        entity = '{0}/string:{1}'.format(namespace, string)

        strings = self.get(entity, lang, ttl=900, force_refresh=force_refresh,
                           default=[])

        return strings

    def get_string(self, string, lang='eng', index=None,
                   namespace=default_namespaces['strings'],
                   force_refresh=False, default=None):
        data = self.get_strings(string, lang, namespace=namespace,
                                force_refresh=force_refresh)

        if len(data) > 0:
            if type(index) is not int:
                index = randint(0, len(data)-1)
            return data[index]
        else:
            return default

    def set(self, entity, item, value):
        entity = entity.lower()
        item = item.lower()

        self.log.info('Setting {0} / {1} => {2}'.format(
            entity, item, json.dumps(value, indent=2, sort_keys=True,
                                     default=fix_dynamo_types)))

        if entity not in Data.cache:
            Data.cache[entity] = {}

        if item in Data.cache[entity] and 'ttl' in Data.cache[entity][item]:
            ttl = Data.cache[entity][item]['ttl']
        else:
            ttl = 120

        Data.cache[entity][item] = {
            'retrived': epoch_now(),
            'ttl': ttl,
            'data': value
        }

        if value is None:
            self.log.debug('Value is "None", so deleting instead!')
            self.table.delete_item(
                Key={
                    'entity': entity,
                    'item': item
                }
            )
        else:
            self.table.put_item(
                Item={
                    'entity': entity,
                    'item': item,
                    'value': value,
                }
            )

        return True

    def set_pref(self, user, pref, value,
                 namespace=default_namespaces['prefs']):
        pref = pref.lower()
        entity = '{0}/{1}'.format(namespace, user)

        self.log.info('Setting user pref {0} for {1}'.format(pref, user))

        data = self.get_prefs(user, namespace=namespace, force_refresh=True)

        if value is not None:
            data[pref] = value
        else:
            if pref in data:
                del data[pref]

        return self.set(entity, 'prefs', data)
