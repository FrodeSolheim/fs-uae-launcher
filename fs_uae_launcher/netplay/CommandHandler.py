from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers


class CommandHandler(DefaultCommandHandler):

    def nicknameinuse(self, nick, *message):
        print("Nickname in use", nick, message)
        helpers.nick(self.client, self.client.handler.generate_nick())

    def __unhandled__(self, command, *args):
        handler = self.client.handler
        handler.post_message(command, args)
