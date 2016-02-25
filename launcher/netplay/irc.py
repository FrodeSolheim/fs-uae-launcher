import sys
import threading

from fsbc.application import call_after
from oyoyo import helpers
from oyoyo.client import IRCClient
from .command_handler import CommandHandler
from .irc_broadcaster import IRCBroadcaster
from .irc_color import IRCColor
from ..launcher_settings import LauncherSettings


# noinspection PyUnusedLocal
class IRC:
    def __init__(self):
        self.running = False
        self.stopping = False
        self.nick_number = 0
        self.channels = {}
        self.my_nick = ""
        self.client = None
        # FIXME: should not be hardcoded here
        self.default_channel = "#lobby"
        self.active_channel_name = self.default_channel
        self.connection = None

    # 
    # def reset(cls):
    #     self.running = False
    #     self.stopping = False
    #     self.nick_number = 0
    #     self.channels = {}
    #     self.my_nick = ""
    #     self.client = None
    #     # FIXME: should not be hardcoded here
    #     self.default_channel = "#lobby"
    #     self.active_channel_name = self.default_channel

    def message(self, message, color=None):
        self.channel(self.active_channel_name).message(message, color)

    def warning(self, message):
        self.message(message, IRCColor.WARNING)

    def info(self, message):
        self.message(message, IRCColor.INFO)

    def is_channel(self, name):
        return len(name) > 0 and name[0] in "&#+!"

    def channel(self, name):
        # FIXME: name should be checked case independently
        if not name:
            name = self.default_channel

        from .channel import Channel
        try:
            return self.channels[name]
        except KeyError:
            print("new channel", repr(name))
            self.channels[name] = Channel(self, name)
            print("channels are now", repr(self.channels))
            # self.set_active_channel(name)
            IRCBroadcaster.broadcast("channel_list", {"added": name})
            return self.channels[name]

    def active_channel(self):
        return self.channel(self.active_channel_name)

    def set_active_channel_name(self, name):
        self.active_channel_name = name
        IRCBroadcaster.broadcast("active_channel", {"channel": name})

    def connect(self):
        self.start()

    def start(self):
        self.stopping = False
        if self.running:
            print("IRC.start - already running")
            return
        threading.Thread(target=self.irc_thread,
                         name="IRCThread").start()
        self.running = True

    def stop(self):
        if not self.running:
            return
        self.stopping = True
        helpers.quit(self.client, "Exited")
        # self.client.quit()

    def irc_thread(self):
        try:
            self.irc_main()
        except Exception as e:
            def func():
                self.warning(repr(e))

            call_after(func)
            import traceback
            traceback.print_exc()
        self.running = False

    def nick(self, spec):
        nick = spec.split("!")[0]
        nick = nick.strip("@+")
        return nick

    def me(self, spec):
        nick = spec.split("!")[0]
        return nick == self.my_nick

    def get_irc_server_host(self):
        return LauncherSettings.get_irc_server()

    def irc_main(self):
        def func():
            self.message("connecting to {0}...".format(
                    self.get_irc_server_host()))

        call_after(func)

        self.client = IRCClient(
                CommandHandler,
                host=self.get_irc_server_host(),
                port=6667,
                nick=self.generate_nick(True),
                blocking=True,
                connect_cb=self.connect_callback)
        self.client.handler = self
        self.connection = self.client.connect()

        while not self.stopping:
            next(self.connection)
        print("irc_main done")
        self.running = False

    def connect_callback(self, client):
        def func():
            self.message("connected to {0}".format(self.get_irc_server_host()))

        call_after(func)

    def post_message(self, command, args):
        # command = command.decode("UTF-8", errors="replace")
        if self.stopping:
            print("ignoring message", command, "because we're stopping")
            return
        # print("post_message", command, args)
        # self.on_message(command, args)
        # print(command, args)

        args = list(args)

        # for i, arg in enumerate(args):
        #     if arg is not None:
        #         args[i] = arg.decode("UTF-8", errors="replace")

        def func():
            # if IRC.broadcast(command, args):
            #     return
            if self.irc_server_message(command, args):
                return
            name = "irc_" + command
            try:
                method = getattr(self, name)
            except AttributeError:
                self.info(" ".join([command] + args))
                pass
            else:
                method(*args)

        call_after(func)

    def privmsg(self, destination, message):
        helpers.msg(self.client, destination, message)

    def notice(self, destination, message):
        self.client.send("notice {0} :{1}".format(destination, message))

    def generate_nick(self, reset=False):
        if reset:
            self.nick_number = 0
        self.nick_number += 1
        if self.nick_number == 1:
            nick = LauncherSettings.get_irc_nick()
        else:
            nick = LauncherSettings.get_irc_nick() + str(self.nick_number)
        self.my_nick = nick
        return nick

    def append_text(self, message):
        self.message(message)

    def handle_command(self, message):
        if message.startswith("/"):
            return self.handle_command_string(message)
        else:
            if not self.active_channel_name:
                self.warning("no active channel")
            else:
                self.channel(self.active_channel_name).privmsg(message)

    def handle_command_string(self, message):
        message = message[1:]
        parts = message.split(" ")
        command = parts[0].lower()
        args = parts[1:]
        name = "command_" + command
        try:
            method = getattr(self, name)
        except AttributeError:
            self.warning(command + ": unknown command")
            return False
        else:
            method(args)
            return True

    def command_raw(self, args):
        if len(args) >= 1:
            self.client.send(" ".join(args))
        else:
            self.warning("usage: /raw <raw irc message>")

    # noinspection SpellCheckingInspection
    def command_whois(self, args):
        if len(args) >= 1:
            self.client.send("whois {0}".format(" ".join(args)))
        else:
            self.warning("usage: /whois <nick>")

    def command_away(self, args):
        if len(args) == 0:
            self.client.send("away")
        else:
            self.client.send("away {0}".format(" ".join(args)))

    def command_back(self, args):
        if len(args) == 0:
            self.client.send("away")
        else:
            self.warning("usage: /back")

    def command_msg(self, args):
        if len(args) >= 2:
            channel = args[0]
            message = " ".join(args[1:])
            # self.channel(channel).privmsg(message)
            # self.channel(channel).message("<{0}> {1}".format(self.my_nick,
            #        message), IRCColor.MY_MESSAGE)
            self.client.send("privmsg {0} :{1}".format(channel, message))
        else:
            self.warning("usage: /msg <nick|channel> <message>")

    def command_notice(self, args):
        if len(args) >= 2:
            channel = args[0]
            message = " ".join(args[1:])
            # self.channel(channel).notice(message)
            self.client.send("notice {0} :{1}".format(channel, message))
        else:
            self.warning("usage: /notice <nick|channel> <message>")

    # noinspection SpellCheckingInspection
    def command_oper(self, args):
        if len(args) == 2:
            self.client.send("oper {0} {1}".format(args[0], args[1]))
        else:
            self.warning("usage: /oper <user> <password>")

    def command_slap(self, args):
        if len(args) == 1:
            message = "slaps {0} around a bit with a large trout".format(
                    args[0])
            self.channel(self.active_channel_name).action(message)
        else:
            self.warning("usage: /slap <nick>")

    def command_me(self, args):
        if len(args) > 0:
            message = " ".join(args)
            self.channel(self.active_channel_name).action(message)
        else:
            self.warning("usage: /me <message>")

    def command_mode(self, args):
        if len(args) >= 2:
            self.client.send("mode {0}".format(" ".join(args)))
        else:
            self.warning("usage: /mode <channel|nick> <parameters...>")

    def command_kick(self, args):
        if not self.is_channel(self.active_channel_name):
            self.warning("cannot kick - not in a channel")
            return
        if len(args) >= 1:
            self.kick(self.active_channel_name, args[0], " ".join(args[1:]))
        else:
            self.warning("usage: /kick <nick> [<message>]")

    def kick(self, channel, nick, message="kicked"):
        self.client.send("KICK", channel, nick, ":{0}".format(message))

    def command_join(self, args):
        if len(args) == 1:
            self.join(args[0])
        else:
            self.warning("join: invalid arguments")

    def join(self, channel):
        helpers.join(self.client, channel)

    def command_leave(self, args):
        return self.command_part(args)

    def command_part(self, args):
        if len(args) == 1:
            self.part(args[0])
        else:
            self.warning("part: invalid arguments")

    def part(self, channel):
        helpers.part(self.client, channel)

    # noinspection SpellCheckingInspection
    def irc_server_message(self, command, args):
        commands = [
            "yourhost", "created", "luserclient", "luserchannels",
            "luserme", "n_local", "n_global", "luserconns", "motdstart",
            "motd", "nomotd", "endofmotd"
        ]
        if command in commands:
            self.message(args[2])
            return 1
        return 0

    # noinspection SpellCheckingInspection
    def irc_featurelist(self, server, nick, *features):
        self.message(" ".join(features))

    def irc_welcome(self, server, nick, message):
        self.message(message)

        password = LauncherSettings.get_irc_nickserv_pass()
        if password:
            self.privmsg("nickserv", "identify {0}".format(password))

        # self.join("#support")
        self.join("#lobby")

        # convenience for development...
        for arg in sys.argv:
            if arg.startswith("--netplay-game="):
                self.join("&" + arg[15:])
                break

    @classmethod
    def filter_nick(cls, full):
        nick = full.split("!")[0]
        return nick

    def irc_privmsg(self, sender, destination, message):
        nick = self.filter_nick(sender)
        if self.is_channel(destination):
            channel = destination
        else:
            channel = self.filter_nick(sender)
        self.channel(channel).on_privmsg(nick, message)
        IRCBroadcaster.broadcast("privmsg", {
            "channel": channel, "message": message, "nick": nick})

    def irc_notice(self, sender, destination, message):
        if sender:
            nick = self.filter_nick(sender)
        else:
            nick = "(server)"
        if self.is_channel(destination):
            channel = destination
        else:
            channel = self.active_channel_name
        self.channel(channel).on_notice(nick, message)
        IRCBroadcaster.broadcast("notice", {
            "channel": channel, "message": message, "nick": nick})

    def irc_kick(self, kicker, channel, who, why):
        self.channel(channel).on_kick(self.filter_nick(kicker), who, why)

    def irc_part(self, who, channel, *_):
        self.channel(channel).on_part(self.filter_nick(who))

    def irc_join(self, who, channel):
        self.channel(channel).on_join(self.filter_nick(who))

    # noinspection SpellCheckingInspection
    def irc_endofnames(self, sender, recipient, channel, message):
        pass

    # noinspection SpellCheckingInspection
    def irc_namreply(self, server, who, equals, channel, nicks):
        self.channel(channel).on_namreply(nicks.split(" "))

    # noinspection SpellCheckingInspection
    def irc_currenttopic(self, sender, recipient, channel, topic):
        self.channel(channel).on_currenttopic(topic)

    # noinspection SpellCheckingInspection
    def irc_topicinfo(self, sender, recipient, channel, who, when):
        pass

    # noinspection SpellCheckingInspection
    def irc_cannotsendtochan(self, server, who, channel, message):
        self.channel(channel).warning("cannot send to channel: " + message)

    def irc_topic(self, who, channel, topic):
        self.channel(channel).on_topic(who, topic)

    def irc_mode(self, who, destination, *args):
        if self.is_channel(destination):
            self.channel(destination).on_mode(self.filter_nick(who), args)
        else:
            self.message("{0} set mode {1} {2}".format(
                    who, destination, " ".join(args)))

    def irc_quit(self, who, reason):
        for name in self.channels:
            self.channel(name).on_quit(self.filter_nick(who), reason)
