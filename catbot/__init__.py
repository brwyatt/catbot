import logging
import logging.handlers
import os
import re
import ssl
import sys
import time

import irc.client

from catbot.settings import Config

VERSION = '0.0.1'
logger = logging.getLogger('CatBot')


class CatBot:

    def __init__(self, configFile='settings.json'):
        self.config = Config(configFile=configFile)
        self._initLogging()
        logger.info('CatBot %s loaded and ready!' % (VERSION,))

    def _initLogging(self):
        print('Setting up logger')

        print('Setting loglevel for logger')
        loglevel = self.config.settings['logging']['level']
        loglevel_numeric = getattr(logging, loglevel, None)
        if not isinstance(loglevel_numeric, int):
            raise ValueError('Invalid log level: %s' % (loglevel,))
        logger.setLevel(loglevel_numeric)

        print('Creating formatter for logger')
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | ' +
                                      '%(message)s')

        print('Setting stdouthandler for logger')
        stdoutHandler = logging.StreamHandler(sys.stdout)
        stdoutHandler.setFormatter(formatter)
        logger.addHandler(stdoutHandler)
        logger.debug('Stdouthandler added to logger')

        logger.debug('Setting filehandler for logger')
        logfile = self.config.settings['logging']['file']
        logdir = logfile[0:logfile.rfind('/')]
        if not os.path.isdir(logdir):
            logger.debug('Creating log directory %s' % (logdir,))
            os.makedirs(logdir)
        fileHandler = logging.handlers.WatchedFileHandler(logfile)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.debug('Filehandler added to logger')

    def start(self):

        pids = []

        for network in Config.settings['networks'].keys():
            worker = CatBotWorker(network,
                                  Config.settings['networks'][network])

            logger.debug('Forking for network {0}'.format(network))
            newpid = os.fork()
            if newpid != 0:
                pids.append(newpid)
                continue

            worker.start()

        while len(pids) > 0:
            logger.debug('Parent! Sleeping for 10 while children still exist!')
            time.sleep(10)


class CatBotWorker:
    config = None
    network = None
    reactor = None
    channels = []

    def __init__(self, network, config):
        self.network = network
        self.config = config
        self.reactor = irc.client.Reactor()

    def connect(self):
        connect_factory = None
        if self.config['servers'][0]['ssl']:
            logger.info('[{0}] Using SSL for connection'.format(self.network))
            connect_factory = irc.connection.Factory(
                wrapper=ssl.wrap_socket)

        while True:
            try:
                host = self.config['servers'][0]['host']
                port = self.config['servers'][0]['port']
                nick = self.config['nick']['nick']
                logger.info('[{0}] Connecting to {1}:{2} as {3}'.format(
                    self.network, host, port, nick))
                connection = self.reactor.server().connect(
                    host, port, nick,
                    connect_factory=connect_factory
                )
                break
            except irc.client.ServerConnectionError as sce:
                logger.critical('[{0}] {1}'.format(self.network, sce))
                time.sleep(10)

        return connection

    def on_connect(self, connection, event):
        for channel in self.config['channels']:
            logger.info('[{0}] Joining {1}'.format(
                self.network, channel['channel']))
            connection.join(channel['channel'])

    def on_disconnect(self, connection, event):
        logger.error('[{0}] Disconnected!'.format(self.network))

    def on_join(self, connection, event):
        if event.target in self.channels:
            logger.debug('[{0}] Join detected by {1} in {2}'.format(
                self.network, event.source, event.target))
            connection.privmsg(event.target, 'Hi, {0}! Welcome to {1}!'
                               .format(event.source.nick, event.target))
        else:
            logger.debug('[{0}] Joined {1}'.format(
                self.network, event.target))
            self.channels.append(event.target)
            connection.privmsg(event.target,
                               'Hi! I\'ve joined {0} on {1}'
                               .format(event.target, self.network))

    def on_privmsg(self, connection, event):
        logger.debug('[{0}] privmsg -- {1}'.format(
            self.network, event))
        self.process_command(event.arguments[0], event.source,
                             event.source.nick, connection, private=True)

    def on_pubmsg(self, connection, event):
        logger.debug('[{0}] pubmsg -- {1}'.format(
            self.network, event))
        m = re.search('{0}: (.+)'.format(connection.real_nickname),
                      event.arguments[0], re.I)
        if m:
            self.process_command(m.group(1), event.source, event.target,
                                 connection)

    def process_command(self, command, source, return_target, connection,
                        private=False):
        logger.debug('[{0}] Command: {1}'.format(self.network, command))

        prefix = ''
        if not private:
            prefix = '{0}: '.format(source.nick)

        if command.lower() == 'ping':
            connection.privmsg(return_target, '{0}PONG'.format(prefix))

    def start(self):
        c = self.connect()

        logger.info('[{0}] Adding protocol handlers'.format(self.network))
        c.add_global_handler('welcome', self.on_connect)
        c.add_global_handler('join', self.on_join)
        c.add_global_handler('disconnect', self.on_disconnect)
        c.add_global_handler('privmsg', self.on_privmsg)
        c.add_global_handler('pubmsg', self.on_pubmsg)

        logger.info('[{0}] Entering reactor loop'.format(self.network))
        self.reactor.process_forever()
        logger.warning('[{0}] Left reactor loop'.format(self.network))
