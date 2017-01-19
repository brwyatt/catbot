import json


class Config:
    settings = {
        'logging': {
            'level': 'WARNING',
            'file': 'log/catbot.log'
        },
        'networks': {}
    }

    def __init__(self, configFile='settings.json'):
        settingsImport = json.load(open(configFile))
        self.settings = self._mergeDicts(self.settings, settingsImport)

    def _mergeDicts(self, original, new):
        if not isinstance(new, dict):
            raise TypeError('Expected dict, but got something else!')
        for k in new.keys():
            if k in original:
                if isinstance(original[k], dict):
                    original[k] = self._mergeDicts(original[k], new[k])
                else:
                    original[k] = new[k]
            else:
                original[k] = new[k]
        return original
