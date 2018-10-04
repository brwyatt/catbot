from random import randint

import asyncio
import irc3

from catbot.data import epoch_now
from catbot.plugin import Plugin


@irc3.plugin
class ChatStats(Plugin):
    userlist = {}

    def __init__(self, bot):
        super().__init__(bot)

    @property
    def frequency(self):
        return int(self.config.get('frequency', 300))

    @property
    def jitter(self):
        return int(self.config.get('jitter', self.frequency/10))

    def sanetize_nick(self, nick):
        nick = nick.lower()
        if nick[0] in ['~', '&', '@', '%', '+']:
            nick = nick[1:]
        return nick

    def update_stats(self, user, channel, add_kicks=0, add_messages=0,
                     add_time=True):
        self.log.info('Running user stats updates for {0} in {1}'
                      .format(user, channel))

        user = self.sanetize_nick(user)
        channel = channel.lower()
        entity = 'catbot.userdata/{0}'.format(user)

        data = self.data.get(entity, 'stats', ttl=(self.frequency*2),
                             default={})

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

    async def update_stats_task(self, user, channel):
        self.log.debug('Starting periodic update task for {user} in {channel}'
                       .format(user=user, channel=channel))
        while True:
            sleep_time = self.frequency + (
                randint(0, self.jitter*2) - self.jitter)
            self.log.debug('Scheduling next update for {user} in {channel} '
                           '{time} seconds from now.'.format(
                               user=user, channel=channel, time=sleep_time))
            await asyncio.sleep(sleep_time)

            self.update_stats(user, channel)

    def start_timer(self, user, channel):
        self.log.debug('Starting timer for {user} on {channel}.'
                       .format(user=user, channel=channel))

        user = self.sanetize_nick(user)
        channel = channel.lower()

        self.update_stats(user, channel, add_time=False)

        if channel not in self.userlist:
            self.userlist[channel] = {}

        self.userlist[channel][user] = self.bot.loop.create_task(
            self.update_stats_task(user, channel))

    def stop_timer(self, user, channel, add_kicks=0):
        self.log.debug('Stopping timer for {user} on {channel}.'
                       .format(user=user, channel=channel))

        user = self.sanetize_nick(user)
        channel = channel.lower()

        if (channel in self.userlist and user in self.userlist[channel]):
            self.userlist[channel][user].cancel()
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
