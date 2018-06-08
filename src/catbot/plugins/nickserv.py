# -*- coding: utf-8 -*-
import logging
import re

import irc3


@irc3.plugin
class NickServ:

    def __init__(self, bot):
        self.bot = bot
        self.module = module = self.__class__.__module__
        self.config = config = bot.config.get(module, {})

        self.log = logging.getLogger('irc3.{0}'.format(module))
        self.log.debug('Config: %r', config)

    def _check_mask(self, mask):
        if re.match('^{0}$'.format(self.config.get(
                'mask', 'NickServ!NickServ@service.*')), mask):
            return True
        else:
            return False

    @irc3.event(r'(@(?P<tags>\S+) )?:(?P<nsn>[^!]+)!(?P<nsu>[^@]+)@(?P<nsh>\S+)'
                r' NOTICE (?P<nick>[^#]\S+) :This nickname is registered.*')
    def identify(self, nsn=None, nsu=None, nsh=None, nick=None, **kw):
        mask = '{0}!{1}@{2}'.format(nsn, nsu, nsh)

        if self._check_mask(mask):
            self.log.info('NickServ requested our password!')
            try:
                password = self.config['password']
            except KeyError:
                self.log.critical('NickServ password not found in config file')
            else:
                self.bot.privmsg(nsn, 'identify %s %s' % (nick, password))
        else:
            self.log.critical('Attempt to steal bot password by {0}'
                              .format(mask))

    @irc3.event(r'(@(?P<tags>\S+) )?:(?P<nsn>[^!]+)!(?P<nsu>[^@]+)@(?P<nsh>\S+)'
                r' NOTICE (?P<nick>[^#]\S+) :Password accepted.*')
    def accepted(self, nsn=None, nsu=None, nsh=None, **kw):
        mask = '{0}!{1}@{2}'.format(nsn, nsu, nsh)

        if self._check_mask(mask):
            self.log.info('NickServ accepted our password')
        else:
            self.log.critical('Received password accepted from {0}! Something '
                              'bad might be happening...')

    @irc3.event(r'(@(?P<tags>\S+) )?:(?P<nsn>[^!]+)!(?P<nsu>[^@]+)@(?P<nsh>\S+)'
                r' NOTICE (?P<nick>[^#]\S+) :Password incorrect\.')
    def rejected(self, nsn=None, nsu=None, nsh=None, **kw):
        mask = '{0}!{1}@{2}'.format(nsn, nsu, nsh)

        if self._check_mask(mask):
            self.log.critical('NickServ rejected our password! Is our config '
                              'wrong?')
        else:
            self.log.critical('Received password rejected from {0}! Something '
                              'bad might be happening...')
