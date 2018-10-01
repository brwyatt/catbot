from random import randint

import irc3
import schedule

from catbot.data import epoch_now
from catbot.plugin import Plugin


@irc3.plugin
class ChatStats(Plugin):
    timer = 300
    jitter = 30
    userlist = {}

    def __init__(self, bot):
        super().__init__(bot)

    def sanetize_nick(self, nick):
        nick = nick.lower()
        if nick[0] in ['~', '&', '@', '%', '+']:
            nick = nick[1:]
        return nick

    def update_stats(self, user, channel, add_kicks=0, add_messages=0,
                     add_time=True):
        user = self.sanetize_nick(user)
        channel = channel.lower()
        entity = 'catbot.userdata/{0}'.format(user)

        self.log.info('Running user stats updates for {0} in {1}'
                      .format(user, channel))

        data = self.data.get(entity, 'stats', ttl=(self.timer*2), default={})

        now = epoch_now()

        if channel not in data:
            data[channel] = {
                'kicks': 0,
                'last_update': now,
                'messages': 0,
                'time_in_channel': 0
            }

        if add_time:
            data[channel]['time_in_channel'] += \
                (now - data[channel]['last_update'])
        data[channel]['kicks'] += add_kicks
        data[channel]['messages'] += add_messages
        data[channel]['last_update'] = now

        self.data.set(entity, 'stats', data)

    def start_timer(self, user, channel):
        user = self.sanetize_nick(user)
        channel = channel.lower()

        self.update_stats(user, channel, add_time=False)

        if channel not in self.userlist:
            self.userlist[channel] = {}

        # Schedule with jitter
        timer = self.timer + (randint(0, self.jitter*2) - self.jitter)

        self.userlist[channel][user] = schedule.every(timer).seconds.do(
            self.update_stats, user, channel)

    def stop_timer(self, user, channel, add_kicks=0):
        user = self.sanetize_nick(user)
        channel = channel.lower()

        if (channel in self.userlist and user in self.userlist[channel]):
            schedule.cancel_job(self.userlist[channel][user])
            del self.userlist[channel][user]

        self.update_stats(user, channel, add_kicks=add_kicks, add_time=True)

    @irc3.event(irc3.rfc.JOIN)
    def join(self, mask, channel, **kwargs):
        if mask.nick != self.bot.nick:
            self.start_timer(mask.nick, channel)

    @irc3.event(irc3.rfc.KICK)
    def kick(self, mask, channel, **kwargs):
        if mask.nick != self.bot.nick:
            self.stop_timer(mask.nick, channel, add_kicks=1)
        else:
            # We got kicked, stop all the timers for this channel
            for nick in [x for x in self.userlist[channel]]:
                self.stop_timer(nick, channel)

    @irc3.event(irc3.rfc.NEW_NICK)
    def new_nick(self, nick, new_nick, **kwargs):
        if nick.nick != self.bot.nick and new_nick != self.bot.nick:
            # Only want the channels that the user is in
            for channel in [x for x in self.userlist
                            if nick.nick.lower() in self.userlist[x]]:
                self.stop_timer(nick.nick, channel)
                self.start_timer(new_nick, channel)

    @irc3.event(irc3.rfc.PART)
    def part(self, mask, channel, **kwargs):
        if mask.nick != self.bot.nick:
            self.stop_timer(mask.nick, channel)
        else:
            # We're the ones leaving, stop all the timers for this channel
            for nick in [x for x in self.userlist[channel]]:
                self.stop_timer(nick, channel)

    @irc3.event(irc3.rfc.PING)
    def ping(self, *args, **kwargs):
        schedule.run_pending()

    @irc3.event(irc3.rfc.PRIVMSG)
    def privmsg(self, mask, event, target, **kwargs):
        if mask.nick != self.bot.nick:
            if target.startswith('#'):  # Channels only!
                self.update_stats(mask.nick, target, add_messages=1)

    @irc3.event(irc3.rfc.QUIT)
    def quit(self, mask, **kwargs):
        if mask.nick != self.bot.nick:
            # Only want the channels that the user is (was) in
            for channel in [x for x in self.userlist
                            if mask.nick.lower() in self.userlist[x]]:
                self.stop_timer(mask.nick, channel)
        else:
            # We're quitting! Stop timers for everyone!
            for channel in [x for x in self.userlist]:
                for nick in [x for x in self.userlist[channel]]:
                    self.stop_timer(nick, channel)

    @irc3.event(irc3.rfc.RPL_NAMREPLY)
    def names(self, channel, data, **kwargs):
        nicks = data.split(' ')
        for nick in nicks:
            if nick != self.bot.nick:
                self.start_timer(nick, channel)
