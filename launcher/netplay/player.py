class Player:
    def __init__(self, nick):
        self.nick = nick
        self.values = {}

    def get(self, key):
        try:
            return self.values[key]
        except KeyError:
            return ""

    def set(self, key, value):
        self.values[key] = value

    def __str__(self):
        return "<Player {0}>".format(self.nick)
