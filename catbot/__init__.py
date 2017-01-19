import logging
import os
import sys

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
        fileHandler = logging.FileHandler(logfile)
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.debug('Filehandler added to logger')

    def start(self):
        logger.warn('CatBot.start() not implemented, exiting instead!')
        sys.exit()
