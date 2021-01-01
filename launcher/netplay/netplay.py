import random
import traceback
import uuid
from urllib.parse import parse_qs

import requests

from fsgs.amiga.amiga import Amiga
from fsgs.context import fsgs
from .connection_tester import ConnectionTester
from .irc import IRC
from .irc_broadcaster import IRCBroadcaster
from .irc_color import IRCColor
from ..launcher_config import LauncherConfig
from ..server.Server import Server


class Netplay:
    _current = None

    @classmethod
    def current(cls):
        if cls._current:
            return cls._current
        return None

    host_ports = []

    @classmethod
    def new_host_port(cls):
        if cls.host_ports is not None:
            cls.host_ports = list(range(25102, 25500))
            random.shuffle(cls.host_ports)
        return cls.host_ports.pop()

    def __init__(self):
        self.enabled = False
        self.game_channel = ""
        self.connection_tester = None
        self.start_sequence = ""
        self.players = {}
        self.irc = IRC()

        LauncherConfig.add_listener(self)
        IRCBroadcaster.add_listener(self)

        Netplay._current = self

    def connect(self):
        self.enabled = True
        self.irc.connect()
        if self.connection_tester is None:
            self.connection_tester = ConnectionTester()

    def disconnect(self):
        if Netplay._current == self:
            Netplay._current = None

        self.enabled = False
        self.irc.stop()

        LauncherConfig.remove_listener(self)
        IRCBroadcaster.remove_listener(self)

    def is_connected(self):
        return self.enabled

    def player(self, nick):
        try:
            return self.players[nick]
        except Exception:
            from .player import Player

            self.players[nick] = Player(nick)
            print("players are now", self.players)
            return self.players[nick]

    def remove_player(self, nick):
        try:
            del self.players[nick]
        except Exception:
            print(
                "[NETPLAY] Warning, tried to remove player "
                "(but wasn't in list):",
                nick,
            )
        else:
            print("[NETPLAY] Players are now", self.players)

    def start_netplay_game(self):
        if self.set_ready():
            if self.is_op():
                self.game_info(
                    "you are marked as ready, initiating game start"
                )
                self.initiate_start_sequence()
            else:
                self.game_info(
                    "you are marked as ready (only ops can start game)"
                )
        else:
            self.game_info("you are not ready")

    def is_op(self):
        return self.irc.channel(self.game_channel).is_op(self.irc.my_nick)

    # noinspection SpellCheckingInspection
    def initiate_start_sequence(self):
        print("initiate start sequence")
        if not self.game_channel:
            self.game_info("cannot start - no game channel")
        self.start_sequence = str(uuid.uuid4())
        message = "__prestart {0} {1}".format(
            self.start_sequence, self.get_config_hash()
        )
        self.irc.channel(self.game_channel).privmsg(message)
        # in case one wants to try a single-player game for testing
        self.on_ackstart()

    # noinspection SpellCheckingInspection
    def on_ackstart(self):
        config_hash = self.get_config_hash()
        start_sequence = self.start_sequence
        player_count = 0
        for player in self.players.values():
            player_count += 1
            if player.nick == self.irc.my_nick:
                # implicitly ok!
                continue
            if player.get("config_hash") != config_hash:
                return
            if player.get("start_sequence") != start_sequence:
                return
        want_players = int(LauncherConfig.get("__netplay_players") or "0")
        if player_count != want_players:
            self.game_warning(
                "cannot start game, wanted {0} players, "
                "has {1}".format(want_players, player_count)
            )
            return
        self.game_info("sending game start command to all clients!")
        message = "__start {0} {1}".format(
            self.start_sequence, self.get_config_hash()
        )
        self.irc.channel(self.game_channel).privmsg(message)
        self.do_start_game()

    def do_start_game(self):
        self.game_info("starting game!")
        print("do start game")

        # we now reset __netplay_addresses so that the ConnectionTester
        # does not connect to the game in progress
        LauncherConfig.set("__netplay_addresses", "")
        from ..launcherapp import LauncherApp

        LauncherApp.start_local_game()

        # game done, resetting config as the same game server cannot be
        # used again
        self.reset_netplay_config()

    @staticmethod
    def get_config_hash():
        return LauncherConfig.checksum()

    # noinspection SpellCheckingInspection
    def set_ready(self):
        if not self.enabled:
            return False
        if not self.game_channel:
            self.irc.warning("cannot set ready - not in a game")
            return False
        if not LauncherConfig.get("__netplay_addresses"):
            self.game_warning("cannot set ready - no server configured")
            self.game_info(
                "an operator needs to use /startgame or "
                "/hostgame (or /customgame) first"
            )
            return False
        if not LauncherConfig.get("__netplay_host"):
            self.game_warning(
                "cannot set ready - no connection to game " "server"
            )
            return False
        LauncherConfig.set("__netplay_ready", "1")
        # check in case an component has force __netplay_ready back to 0
        return LauncherConfig.get("__netplay_ready") == "1"

    def on_config(self, key, value):
        if key == "__netplay_host_last_error" and value:
            self.game_warning("problem connecting to game server: " + value)
        elif key == "__netplay_host":
            if value:
                self.game_info(
                    "successfully connected to net play host: " + value
                )
        if not self.irc.running:
            return
        if not self.game_channel:
            return
        if key in LauncherConfig.sync_keys_set:
            message = "__config {0} {1}".format(key, value)
            self.irc.channel(self.game_channel).privmsg(message)

    def game_message(self, message, color=None):
        if not self.game_channel:
            self.irc.warning(
                "game message received (but not "
                "currently in a game channel): " + message
            )
            return
        self.irc.channel(self.game_channel).message(message, color)
        if self.game_channel != self.irc.active_channel_name:
            # also paste message to active console
            self.irc.active_channel().message(message, color)

    def game_warning(self, message):
        self.game_message(message, IRCColor.WARNING)

    def game_info(self, message):
        self.game_message(message, IRCColor.INFO)

    def is_game_channel(self, name):
        if not self.irc.is_channel(name):
            return False
        if name.startswith("&"):
            return True
        if name.endswith("-game"):
            return True
        return False

    def on_irc(self, key, args):
        if key == "joined":
            if self.is_game_channel(args["channel"]):
                if self.game_channel:
                    self.irc.part(self.game_channel)
                self.game_channel = ""
                self.reset_netplay_config()
                self.on_join_game_channel(args["channel"])
        elif key == "parted":
            if self.game_channel == args["channel"]:
                self.game_channel = ""
                self.reset_netplay_config()
        elif key == "privmsg":
            if args["message"].startswith("__"):
                if args["channel"] == self.game_channel:
                    self.handle_game_instruction(args["nick"], args["message"])
        elif key == "join":
            if args["channel"] == self.game_channel:
                # initialize new player
                self.player(args["nick"])
                if args["nick"] != self.irc.my_nick:
                    if self.is_op():
                        # operator - send config to new player(s)
                        self.irc.channel(self.game_channel).action(
                            "sends config on arrival of new player"
                        )
                        self.send_config()
        elif key == "part":
            if args["channel"] == self.game_channel:
                self.remove_player(args["nick"])

    def on_join_game_channel(self, channel):
        # first we erase config which is not part of the default configuration
        # key set, to avoid some problems
        keys = fsgs.config.values.keys()
        for key in keys:
            if key not in LauncherConfig.default_config:
                LauncherConfig.set(key, "")
        self.game_channel = channel
        # reset list of players
        self.players = {}

    @staticmethod
    def reset_config():
        LauncherConfig.load_default_config()

    @staticmethod
    def reset_netplay_config():
        LauncherConfig.set_multiple(
            [
                ("__netplay_id", ""),
                ("__netplay_password", ""),
                ("__netplay_players", ""),
                ("__netplay_port", ""),
                ("__netplay_addresses", ""),
                ("__netplay_host", ""),
            ]
        )

    def handle_command(self, command):
        if not command.startswith("/"):
            return False
        args = command[1:].split(" ")
        print(args)
        function_name = "command_" + args[0]
        try:
            function = getattr(self, function_name)
        except AttributeError:
            return False
        else:
            try:
                function(args[1:])
            except Exception:
                self.game_warning(traceback.format_exc())
            return True

    def command_ready(self, args):
        if len(args) != 0:
            self.irc.warning("syntax: /ready")
            return
        self.set_ready()
        if LauncherConfig.get("__netplay_ready") == "1":
            self.game_info("status set to ready")

    # noinspection SpellCheckingInspection
    def command_notready(self, args):
        if len(args) != 0:
            self.irc.warning("syntax: /notready")
            return
        LauncherConfig.set("__netplay_ready", "0")
        self.game_info("status set to not ready")

    def command_check(self, args):
        channel = self.irc.active_channel()
        if not self.require_game_channel(channel):
            return
        if len(args) != 1:
            self.irc.warning("syntax: /check <key>")
            return
        if not channel.is_op():
            self.irc.warning("check: you need to be an operator")
            return
        for arg in args:
            self.print_check_request(
                self.irc.my_nick, arg, LauncherConfig.get(arg)
            )
            message = "__check {0} {1}".format(arg, LauncherConfig.get(arg))
            self.irc.channel(self.game_channel).privmsg(message)

    # noinspection SpellCheckingInspection
    def command_verify(self, args):
        channel = self.irc.active_channel()
        if not self.require_game_channel(channel):
            return
        if len(args) != 0:
            self.irc.warning("syntax: /verify")
            return
        if not channel.is_op():
            self.irc.warning("verify: you need to be an operator")
            return
        # for arg in args:
        #     self.game_info("requesting verification of {0} = {1}".format(arg,
        #             Config.get(arg)))
        self.print_verify_request(self.irc.my_nick)
        self.irc.channel(self.game_channel).privmsg("__beginverify")
        for key in LauncherConfig.checksum_keys:
            value = LauncherConfig.get(key)
            message = "__verify {0} {1}".format(key, value)
            self.irc.channel(self.game_channel).privmsg(message)
        self.irc.channel(self.game_channel).privmsg("__endverify")

    # noinspection SpellCheckingInspection
    def command_sendconfig(self, args):
        channel = self.irc.active_channel()
        if not self.require_game_channel(channel):
            return
        if len(args) != 0:
            self.irc.warning("syntax: /sendconfig")
            return
        self.game_info("sending config")
        self.send_config()

    def send_config(self):
        if not self.game_channel:
            return
        channel = self.irc.channel(self.game_channel)
        # sending keys in preferred key order
        for key in LauncherConfig.sync_keys_list:
            value = LauncherConfig.get(key)
            message = "__config {0} {1}".format(key, value)
            channel.privmsg(message)

    def require_game_channel(self, channel):
        if not self.irc.running:
            return False
        result = self.game_channel and channel.name == self.game_channel
        if not result:
            channel.warning("not in active game channel")
        return result

    # noinspection SpellCheckingInspection
    def command_resetconfig(self, args):
        if len(args) != 0:
            self.irc.warning("syntax: /resetconfig")
            return
        channel = self.irc.active_channel()
        if not self.require_game_channel(channel):
            return

        channel.info("config reset by request")
        # send resetconfig command to other players first
        if channel.is_op():
            channel.privmsg("__resetconfig")
        # then reset own config, so config changes are applied after
        # other players have reset their configs
        self.reset_config()

    def parse_server_args(self, args, default_port):
        if len(args) == 0:
            return None
        host = args.pop(0)
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)
        else:
            port = default_port
        if len(args) > 0:
            players = args.pop(0)
            players = int(players)
        else:
            players = len(self.players)
        if len(args) > 0:
            password = args.pop(0)
        else:
            password = ""
        if len(args) > 0:
            return None
        return host, port, players, password

    # noinspection SpellCheckingInspection
    def command_startserver(self, args):
        return self.command_startgame(args)

    # noinspection SpellCheckingInspection
    def command_startgame(self, args):
        channel = self.irc.active_channel()
        if not self.require_game_channel(channel):
            return
        result = self.parse_server_args(args, 25101)
        if not result:
            self.irc.warning(
                "usage: /startgame <host>[:<port>] " "[<players>] [<password>]"
            )
            return
        host, port, players, password = result

        if not channel.is_op():
            self.irc.warning("startgame: you need to be an operator")
            return

        url = "http://{0}:{1}/game/create?players={2}&password={3}".format(
            host, port, players, password
        )
        try:
            r = requests.get(url)
            r.raise_for_status()
        except Exception:
            channel.warning(
                "Problem starting game server: {0}".format(
                    traceback.format_exc()
                )
            )
        else:
            result = r.text
            print(result)
            result_dict = parse_qs(result)
            print(result_dict)
            game_id = result_dict["id"][0]
            game_password = result_dict["password"][0]
            game_port = result_dict["port"][0]
            game_addresses = result_dict["addresses"][0]
            LauncherConfig.set_multiple(
                [
                    ("__netplay_game", game_id),
                    ("__netplay_password", game_password),
                    ("__netplay_players", str(players)),
                    ("__netplay_port", game_port),
                    ("__netplay_host", ""),
                    ("__netplay_addresses", game_addresses),
                ]
            )
            channel.info(
                "started game id: {0} password: {1} "
                "server: {2} port: {3}".format(
                    game_id, game_password, game_addresses, game_port
                )
            )

    def command_hostgame(self, args):
        channel = self.irc.active_channel()
        if not self.require_game_channel(channel):
            return
        result = self.parse_server_args(args, self.new_host_port())
        if not result:
            self.irc.warning(
                "usage: /hostgame <address>[,<address2>][:<port>] "
                "[<players>] [<password>]"
            )
            return
        addresses, port, players, password = result

        if not channel.is_op():
            self.irc.warning("hostgame: you need to be an operator")
            return

        server = Server(port, players, password)
        server.start()

        from ..server.ServerWindow import ServerWindow

        window = ServerWindow(None, server)
        window.show()

        game_id = str(uuid.uuid4())
        LauncherConfig.set_multiple(
            [
                ("__netplay_game", game_id),
                ("__netplay_password", password),
                ("__netplay_players", str(players)),
                ("__netplay_port", str(port)),
                ("__netplay_host", ""),
                ("__netplay_addresses", addresses),
            ]
        )
        channel.info(
            "started game id: {0} password: {1} "
            "server: {2} port: {3}".format(game_id, password, addresses, port)
        )

    # noinspection SpellCheckingInspection
    def command_setserver(self, args):
        return self.command_customgame(args)

    # noinspection SpellCheckingInspection
    def command_customgame(self, args):
        channel = self.irc.active_channel()
        if not self.require_game_channel(channel):
            return
        result = self.parse_server_args(args, 25100)
        if not result:
            self.irc.warning(
                "usage: /customgame <address>[,<address2>][:<port>] "
                "[<players>] [<password>]"
            )
            return
        addresses, port, players, password = result

        if not channel.is_op():
            self.irc.warning("customgame: you need to be an operator")
            return

        game_id = str(uuid.uuid4())
        LauncherConfig.set_multiple(
            [
                ("__netplay_game", game_id),
                ("__netplay_password", password),
                ("__netplay_players", str(players)),
                ("__netplay_port", str(port)),
                ("__netplay_host", ""),
                ("__netplay_addresses", addresses),
            ]
        )
        channel.info(
            "started game id: {0} password: {1} "
            "server: {2} port: {3}".format(game_id, password, addresses, port)
        )

    def command_set(self, args):
        channel = self.irc.active_channel()
        if not self.require_game_channel(channel):
            return
        if len(args) < 1:
            self.irc.warning("usage: /set <key> [<value>]")
            return
        if not channel.is_op():
            self.irc.warning("hostgame: you need to be an operator")
            return

        key = args[0]
        value = " ".join(args[1:])
        print("config, setting", key, "to", value)
        channel.action('set option {0} to "{1}"'.format(key, value))
        LauncherConfig.set(key, value)

    # noinspection SpellCheckingInspection
    def handle_game_instruction(self, nick, message):
        channel = self.irc.channel(self.game_channel)

        # if Netplay.game_channel != self.name:
        #     self.warning(self, "ignored command in "
        #             "non-active game: {0}".format(command), IRCColor.WARNING)
        #     return
        words = message.split(" ")
        command = words[0]
        arg = " ".join(words[1:])
        if command == "__config":
            if channel.is_op(nick):
                args = arg.split(" ", 1)
                key = args[0]
                value = ""
                if len(args) > 1:
                    value = args[1]
                self.set_config(key.strip(), value.strip())
        elif command == "__prestart":
            if channel.is_op(nick):
                seq, config_hash = arg.split(" ")
                my_config_hash = self.get_config_hash()
                if my_config_hash != config_hash:
                    channel.privmsg("not the same config hash")
                    return
                if LauncherConfig.get("__netplay_ready") != "1":
                    channel.privmsg(
                        "(op tried to start game, " "but I am not ready)"
                    )
                    return
                channel.privmsg(
                    "__ackstart {0} {1}".format(seq, my_config_hash)
                )
        elif command == "__ackstart":
            start_sequence, config_hash = arg.split(" ")
            self.player(nick).set("start_sequence", start_sequence)
            self.player(nick).set("config_hash", config_hash)
            self.on_ackstart()
            # FIXME: check start sequence?
        elif command == "__start":
            if channel.is_op(nick):
                start_sequence, config_hash = arg.split(" ")
                my_config_hash = self.get_config_hash()
                if my_config_hash != config_hash:
                    channel.action(
                        "could not start game " "(mismatching config hash)"
                    )
                    return
                self.do_start_game()
        elif command == "__resetconfig":
            if channel.is_op(nick):
                channel.info("config reset by op")
                self.reset_config()
        elif command == "__check":
            if channel.is_op(nick):
                args = arg.split(" ")
                key = args[0]
                value = " ".join(args[1:])
                my_value = LauncherConfig.get(key)
                self.print_check_request(nick, key, value)
                self.print_check_response(
                    self.irc.my_nick, key, my_value, value
                )
                channel.privmsg("__ackcheck {0} {1}".format(key, my_value))
        elif command == "__beginverify":
            if channel.is_op(nick):
                self.print_verify_request(nick)
        elif command == "__verify":
            if channel.is_op(nick):
                args = arg.split(" ")
                key = args[0]
                value = " ".join(args[1:])
                if LauncherConfig.get(key) != value:
                    self.print_verify_response(
                        self.irc.my_nick, key, LauncherConfig.get(key)
                    )
                    channel.privmsg(
                        "__ackverify {0} {1}".format(
                            key, LauncherConfig.get(key)
                        )
                    )
        elif command == "__endverify":
            pass
        elif command == "__ackcheck":
            args = arg.split(" ")
            key = args[0]
            value = " ".join(args[1:])
            my_value = LauncherConfig.get(key)
            self.print_check_response(nick, key, value, my_value)
        elif command == "__ackverify":
            args = arg.split(" ", 1)
            self.print_verify_response(nick, args[0], " ".join(args[1:]))
        else:
            channel.warning("unknown command received: {0}".format(command))

    def print_check_request(self, nick, key, value):
        self.irc.channel(self.game_channel).info(
            "* {0} requested check of {1} ({2})".format(nick, key, value)
        )

    def print_check_response(self, nick, key, value, check_value):
        if value == check_value:
            color = IRCColor.INFO
        else:
            color = IRCColor.WARNING
        self.irc.channel(self.game_channel).message(
            "{0} = {1} ({2})".format(key, value, nick), color
        )

    def print_verify_request(self, nick):
        self.irc.channel(self.game_channel).info(
            "* {0} requested automatic config verification".format(nick)
        )

    def print_verify_response(self, nick, key, value):
        self.irc.channel(self.game_channel).warning(
            "{0} = {1} ({2})".format(key, value, nick)
        )

    def set_config(self, key, value):
        # this config was received from a game channel operator
        print("received config", key, value)
        # channel =
        self.irc.channel(self.game_channel)
        if key not in LauncherConfig.sync_keys_set:
            print("not processing this key")
            return
        elif key in ["x_kickstart_file_sha1", "x_kickstart_ext_file_sha1"]:
            self.set_kickstart_config(key, value)
        elif key in self.file_config:
            self.set_file_config(key, value)
        else:
            LauncherConfig.set(key, value)

    def set_kickstart_config(self, key, value):
        channel = self.irc.channel(self.game_channel)
        if key == "x_kickstart_file_sha1":
            if value == Amiga.INTERNAL_ROM_SHA1:
                LauncherConfig.set_multiple(
                    [
                        ("kickstart_file", "internal"),
                        ("x_kickstart_file", "internal"),
                        (key, value),
                    ]
                )
            else:
                path = fsgs.file.find_by_sha1(sha1=value)
                if path:
                    LauncherConfig.set_multiple(
                        [
                            ("kickstart_file", path),
                            ("x_kickstart_file", path),
                            (key, value),
                        ]
                    )
                else:
                    channel.action(
                        "could not find kickstart for {0}".format(repr(value))
                    )
        elif key == "x_kickstart_ext_file_sha1":
            if not value:
                LauncherConfig.set_multiple(
                    [
                        ("kickstart_ext_file", ""),
                        ("x_kickstart_ext_file", ""),
                        (key, ""),
                    ]
                )
                return
            path = fsgs.file.find_by_sha1(sha1=value)
            if path:
                LauncherConfig.set_multiple(
                    [
                        ("kickstart_ext_file", path),
                        ("x_kickstart_ext_file", path),
                        (key, value),
                    ]
                )
            else:
                channel.action(
                    "could not find (ext) kickstart "
                    "for {0}".format(repr(value))
                )

    def set_file_config(self, key, value):
        channel = self.irc.channel(self.game_channel)
        set_key = self.file_config[key]
        if not value:
            LauncherConfig.set_multiple([(set_key, ""), (key, "")])
            return
        if value.startswith("http://") or value.startswith("https://"):
            path = value
        else:
            # path = Database.get_instance().find_file(sha1=value)
            path = fsgs.file.find_by_sha1(sha1=value)
        # if not path:
        #     path = find_downloadable_file(value)
        if path:
            LauncherConfig.set_multiple([(set_key, path), (key, value)])
        else:
            LauncherConfig.set_multiple([(set_key, ""), (key, "")])
            channel.action(
                "could not find {1} for " "for {0}".format(value, set_key)
            )

    file_config = {}
    for i in range(Amiga.MAX_FLOPPY_DRIVES):
        file_config[
            "x_floppy_drive_{0}_sha1".format(i)
        ] = "floppy_drive_{0}".format(i)
    for i in range(Amiga.MAX_FLOPPY_IMAGES):
        file_config[
            "x_floppy_image_{0}_sha1".format(i)
        ] = "floppy_image_{0}".format(i)
    for i in range(Amiga.MAX_CDROM_DRIVES):
        file_config[
            "x_cdrom_drive_{0}_sha1".format(i)
        ] = "cdrom_drive_{0}".format(i)
    for i in range(Amiga.MAX_CDROM_IMAGES):
        file_config[
            "x_cdrom_image_{0}_sha1".format(i)
        ] = "cdrom_image_{0}".format(i)
    for i in range(Amiga.MAX_HARD_DRIVES):
        file_config[
            "x_hard_drive_{0}_sha1".format(i)
        ] = "hard_drive_{0}".format(i)
