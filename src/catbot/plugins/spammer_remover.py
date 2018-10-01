import irc3

from catbot.plugin import Plugin


@irc3.plugin
class SpammerRemover(Plugin):

    @irc3.event(irc3.rfc.PRIVMSG)
    def privmsg(self, mask, event, target, **kwargs):
        if mask.nick != self.bot.nick:
            if target.startswith('#'):  # Channels only!
                pass
