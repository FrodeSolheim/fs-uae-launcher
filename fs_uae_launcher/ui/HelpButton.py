from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from fsbc.desktop import open_url_in_browser
from .IconButton import IconButton


class HelpButton(IconButton):
    def __init__(self, parent, url):
        IconButton.__init__(self, parent, "16/information.png")
        self.url = url

    def on_activate(self):
        open_url_in_browser(self.url)
