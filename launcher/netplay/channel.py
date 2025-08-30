from .irc_broadcaster import IRCBroadcaster
from .irc_color import IRCColor


class Channel:
    def __init__(self, irc, name):
        self.name = name
        self.lines = []
        self.colors = []
        self.nicks = set()
        self.ops = set()
        self.half_ops = set()
        self.voices = set()
        self.irc = irc

    def get_text(self):
        return "\n".join(self.lines) + "\n"

    def is_op(self, nick=None):
        if nick is None:
            nick = self.irc.my_nick
        return nick in self.ops

    def message(self, message, color=None):
        if color is None:
            # default color does not work properly on Mac
            color = IRCColor.MESSAGE
        # remove special character (action)
        message = message.replace("\u0001", "")
        # remove special character (bold font)
        message = message.replace("\u0002", "")
        line = message + "\n"
        self.lines.append(line)
        self.colors.append(color)
        IRCBroadcaster.broadcast(
            "message", {"channel": self.name, "message": line, "color": color}
        )

    def info(self, message):
        return self.message(message, color=IRCColor.INFO)

    def warning(self, message):
        return self.message(message, color=IRCColor.WARNING)

    def get_nick_list(self):
        nicks = []
        for nick in self.nicks:
            if nick in self.ops:
                status = "@"
            elif nick in self.half_ops:
                status = "%"
            elif nick in self.voices:
                status = "+"
            else:
                status = ""
            nicks.append(status + nick)
        return sorted(nicks)

    def action(self, message):
        message = "\u0001ACTION {0}\u0001".format(message)
        self.privmsg(message)

    def privmsg(self, message, notice=False, echo=True):
        if echo and not message.startswith("__"):
            if notice:
                text = "-{0}- {1}".format(self.irc.my_nick, message)
            elif message.startswith("[*] "):
                text = "* {0} {1}".format(self.irc.my_nick, message[4:])
            elif message.startswith("\u0001ACTION"):
                text = "* {0} {1}".format(self.irc.my_nick, message[8:-1])
            else:
                text = "<{0}> {1}".format(self.irc.my_nick, message)
            self.message(text, IRCColor.MY_MESSAGE)
        if notice:
            self.irc.notice(self.name, message)
        else:
            self.irc.privmsg(self.name, message)

    def notice(self, message):
        return self.privmsg(message, notice=True)

    def add_nick(self, nick):
        self.nicks.add(nick)
        IRCBroadcaster.broadcast("join", {"channel": self.name, "nick": nick})

    def remove_nick(self, nick):
        IRCBroadcaster.broadcast("part", {"channel": self.name, "nick": nick})
        if nick not in self.nicks:
            # print("Channel.parted - warning, nick not in list", nick)
            pass
        else:
            self.nicks.remove(nick)
            IRCBroadcaster.broadcast("nick_list", {"channel": self.name})
        if nick in self.ops:
            self.ops.remove(nick)
        if nick in self.half_ops:
            self.half_ops.remove(nick)
        if nick in self.voices:
            self.voices.remove(nick)

    def handle_leave_channel(self):
        self.nicks.clear()
        self.ops.clear()
        self.voices.clear()
        IRCBroadcaster.broadcast("parted", {"channel": self.name})

    def on_privmsg(self, nick, message, notice=False):
        if message.startswith("__"):
            pass
        else:
            color = IRCColor.MESSAGE
            if notice:
                text = "-{0}- {1}".format(nick, message)
                color = IRCColor.NOTICE
            elif message.startswith("[*] "):
                text = "* {0} {1}".format(nick, message[4:])
            elif message.startswith("\u0001ACTION"):
                text = "* {0} {1}".format(nick, message[8:-1])
            else:
                text = "<{0}> {1}".format(nick, message)
            self.message(text, color)

    def on_notice(self, nick, message):
        return self.on_privmsg(nick, message, notice=True)

    # noinspection SpellCheckingInspection
    def on_currenttopic(self, topic):
        self.message("{0}".format(topic), IRCColor.TOPIC)

    def on_join(self, nick):
        from launcher.netplay.irc import LOBBY_CHANNEL
        if self.name == LOBBY_CHANNEL:
            # Show welcome only in local UI
            if self.irc.me(nick):
                self.message(
                    f"Welcome to the IRC {self.name}!",
                    IRCColor.JOIN
                )
                # Only the joining user sends the /me action
                self.irc.handle_command(f"/me has joined the lobby.")
            self.add_nick(nick)
        else:
            if self.irc.me(nick):
                self.nicks.clear()
                self.ops.clear()
                self.voices.clear()
                self.message(
                    f"You joined the game channel - {self.name}.",
                    IRCColor.JOIN
                )
                self.irc.set_active_channel_name(self.name)
                IRCBroadcaster.broadcast("joined", {"channel": self.name})
            else:
                # Only show this message to the joining user
                if self.irc.my_nick == nick:
                    self.message(
                        f"You joined the channel {self.name} as a user.",
                        IRCColor.JOIN
                    )
                # Show this message to everyone else
                self.message(
                    f"* {nick} joined ({self.name})", IRCColor.JOIN
                )
                if nick in self.nicks:
                    print(f"Channel.joined - warning, nick already in list {nick}")
                else:
                    self.add_nick(nick)
        IRCBroadcaster.broadcast("nick_list", {"channel": self.name})

    # noinspection SpellCheckingInspection
    def on_kick(self, kicker, kickee, reason):
        self.message(
            "* {0} kicked {1} ({2})".format(kicker, kickee, reason),
            IRCColor.KICK,
        )
        if self.irc.me(kickee):
            self.handle_leave_channel()

    def on_topic(self, who, topic):
        self.message(
            "* {0} changed topic to:\n{1} ".format(who, topic), IRCColor.TOPIC
        )

    def on_mode(self, who, args):
        if args[0] == "+o":
            for nick in args[1:]:
                self.ops.add(nick)
        elif args[0] == "-o":
            for nick in args[1:]:
                if nick in self.ops:
                    self.ops.remove(nick)
        elif args[0] == "+h":
            for nick in args[1:]:
                self.half_ops.add(nick)
        elif args[0] == "-h":
            for nick in args[1:]:
                if nick in self.half_ops:
                    self.half_ops.remove(nick)
        elif args[0] == "+v":
            for nick in args[1:]:
                self.voices.add(nick)
        elif args[0] == "-v":
            for nick in args[1:]:
                if nick in self.voices:
                    self.voices.remove(nick)
        if args[0].startswith("+"):
            color = IRCColor.POS_MODE
        else:
            color = IRCColor.NEG_MODE
        self.message("* {0} sets mode {1}".format(who, " ".join(args)), color)
        IRCBroadcaster.broadcast("nick_list", {"channel": self.name})

    # noinspection SpellCheckingInspection
    def on_namreply(self, nicks):
        for nick in nicks:
            if nick.startswith("@"):
                # self.nicks.add(nick[1:])
                self.ops.add(nick[1:])
                self.add_nick(nick[1:])
            elif nick.startswith("+"):
                # self.nicks.add(nick[1:])
                self.voices.add(nick[1:])
                self.add_nick(nick[1:])
            else:
                # self.nicks.add(nick)
                self.add_nick(nick)
        IRCBroadcaster.broadcast("nick_list", {"channel": self.name})

    def on_part(self, nick):
        if self.irc.me(nick):
            self.message("* you left " + self.name, IRCColor.PART)
            self.handle_leave_channel()
        else:
            self.message(
                "* {0} left {1}".format(nick, self.name), IRCColor.PART
            )
            self.remove_nick(nick)
        IRCBroadcaster.broadcast("nick_list", {"channel": self.name})

    def on_quit(self, nick, reason):
        if nick in self.nicks or self.name == nick or not self.name:
            self.message(
                "* {0} quit ({1}) ".format(nick, reason), IRCColor.PART
            )
        self.remove_nick(nick)
