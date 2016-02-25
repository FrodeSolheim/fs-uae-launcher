from oyoyo import helpers
from oyoyo.cmdhandler import DefaultCommandHandler


class CommandHandler(DefaultCommandHandler):
    # noinspection SpellCheckingInspection
    def nicknameinuse(self, nick, *message):
        print("Nickname in use", nick, message)
        helpers.nick(self.client, self.client.handler.generate_nick())

    def __unhandled__(self, command, *args):
        handler = self.client.handler
        handler.post_message(command, args)
